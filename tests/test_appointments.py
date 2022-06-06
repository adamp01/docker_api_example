import unittest
import json
import os
from datetime import datetime, date, timedelta
from application import create_app, db
from wsgi import app
from models.user import User
from models.therapist import Therapist, Specialism
from models.appointment import Appointment
from .create_dummy_data import insert_dummy_data


class AppointmentTestCase(unittest.TestCase):
    """Test case for the appointments."""

    def setUp(self):
        """Set up test variables."""
        self.app = app
        self.client = self.app.test_client()
        self.email = "test@example.com"
        self.user_data = json.dumps({"email": self.email, "password": "test_password"})

        with self.app.app_context():
            self.token = User(self.email).generate_token()
            db.session.close()
            db.drop_all()
            db.create_all()
            insert_dummy_data(self.app)

    def get_result(self, endpoint):
        res = self.client.get(
            endpoint, headers={"Authorization": f"Bearer {self.token}"}
        )
        result = json.loads(res.data.decode())
        # Get rid of the time element, ensure the rest is equal
        if "appointments" in result.keys():
            list(map(lambda x: x.pop("time"), result["appointments"]))
        return res, result

    def get_post_result(self, endpoint):
        res = self.client.post(
            endpoint, headers={"Authorization": f"Bearer {self.token}"}
        )
        result = json.loads(res.data.decode())
        return res, result

    def test_get_appointments_by_date_range(self):
        """Test that appointments can be filtered by date range."""
        res, result = self.get_result(
            "/get_appointments?start=2022-06-03&end=2022-06-09"
        )
        self.assertEqual(result["message"], "Appointments found: 2")
        self.assertEqual(
            result["appointments"],
            [
                {"duration": 60.0, "therapist": "John Smith", "type": "one-off"},
                {"duration": 60.0, "therapist": "Jane Smith", "type": "one-off"},
            ],
        )
        self.assertEqual(res.status_code, 200)

    def test_get_appointments_by_specialism(self):
        """Test that appointments can be filtered by specialism."""
        res, result = self.get_result("/get_appointments?specialisms=Addiction")
        self.assertEqual(result["message"], "Appointments found: 2")
        self.assertEqual(
            result["appointments"],
            [
                {"duration": 60.0, "therapist": "John Smith", "type": "one-off"},
                {"duration": 30.0, "therapist": "John Smith", "type": "consultation"},
            ],
        )
        self.assertEqual(res.status_code, 200)

    def test_get_appointments_by_type(self):
        """Test that appointments can be filtered by type."""
        res, result = self.get_result("/get_appointments?type=one-off")
        self.assertEqual(result["message"], "Appointments found: 2")
        self.assertEqual(
            result["appointments"],
            [
                {"duration": 60.0, "therapist": "John Smith", "type": "one-off"},
                {"duration": 60.0, "therapist": "Jane Smith", "type": "one-off"},
            ],
        )
        self.assertEqual(res.status_code, 200)

    def test_get_appointments_by_multiple(self):
        """Test that appointments can be filtered by a combination of filters."""
        res, result = self.get_result(
            "/get_appointments?start=2022-06-03&end=2022-06-12&specialisms=Addiction&type=one-off"
        )
        self.assertEqual(result["message"], "Appointments found: 1")
        self.assertEqual(
            result["appointments"],
            [{"duration": 60.0, "therapist": "John Smith", "type": "one-off"}],
        )
        self.assertEqual(res.status_code, 200)

    def test_get_appointments_no_params(self):
        """Test that attempting to get appointments with no params fails."""
        res, result = self.get_result("/get_appointments")
        self.assertEqual(result["message"], "No query parameters found.")
        self.assertEqual(res.status_code, 400)

    def test_add_appointment(self):
        """Test that an appointment can be added."""
        res, result = self.get_post_result(
            "/add_appointment?start=2022-06-20 12:41&duration=60&type=one-off&therapist_id=1"
        )
        self.assertEqual(result["message"], "Appointment added.")
        self.assertEqual(res.status_code, 200)

    def test_cant_add_overlapping_appointment(self):
        """Test that an appointment cannot be added with an already occupied start time."""
        res, result = self.get_post_result(
            "/add_appointment?start=2022-06-20 12:41&duration=60&type=one-off&therapist_id=1"
        )
        res, result = self.get_post_result(
            "/add_appointment?start=2022-06-20 12:41&duration=60&type=one-off&therapist_id=1"
        )
        result = json.loads(res.data.decode())
        self.assertEqual(result["message"], "Overlapping with existing appointment.")
        self.assertEqual(res.status_code, 400)

    def test_cant_add_appointment_with_invalid_start(self):
        """Test that an appointment cannot be added with an invalid start datetime or duration."""
        res, result = self.get_post_result(
            "/add_appointment?start=2022-05-06&duration=60&type=one-off&therapist_id=1"
        )
        self.assertEqual(result["message"], "Invalid start time or duration.")
        self.assertEqual(res.status_code, 400)
        res, result = self.get_post_result(
            "/add_appointment?start=2022-05-06 12:41&duration=fail&type=one-off&therapist_id=1"
        )
        self.assertEqual(result["message"], "Invalid start time or duration.")
        self.assertEqual(res.status_code, 400)

    def test_cant_add_without_therapist(self):
        """Test that an appointment cannot be added without a valid therapist id."""
        res, result = self.get_post_result(
            "/add_appointment?start=2022-05-06 12:41&duration=60&type=one-off&therapist_id=7"
        )
        self.assertEqual(result["message"], "Therapist not found.")
        self.assertEqual(res.status_code, 400)

    def test_cant_add_appointment_in_past(self):
        """Test that an appointment cannot be added in the past."""
        res, result = self.get_post_result(
            "/add_appointment?start=2022-05-06 12:41&duration=60&type=one-off&therapist_id=1"
        )
        self.assertEqual(result["message"], "Cannot add an appointment in the past.")
        self.assertEqual(res.status_code, 400)
