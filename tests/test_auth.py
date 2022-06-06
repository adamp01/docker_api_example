import unittest
import json
from application import create_app, db
from wsgi import app


class AuthTestCase(unittest.TestCase):
    """Test case for the authentication."""

    def setUp(self):
        """Set up test variables."""
        self.app = app
        self.client = self.app.test_client()
        self.user_data = json.dumps(
            {"email": "test@example.com", "password": "test_password"}
        )
        self.bad_json = "{'bad':'data'}"
        self.bad_email = json.dumps({"email": 1234, "password": "test_password"})
        self.bad_password = json.dumps({"email": "test@example.com", "password": 1234})

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correctly."""
        res = self.client.post(
            "/register",
            json=self.user_data,
            headers={"Content-Type": "application/json"},
        )
        result = json.loads(res.data.decode())
        self.assertEqual(
            result["message"], "Successfully registered new user: test@example.com"
        )
        self.assertEqual(res.status_code, 201)

    def test_registration_bad_json(self):
        """Test user registration fails gracefully when bad json sent."""
        res = self.client.post(
            "/register",
            json=self.bad_json,
            headers={"Content-Type": "application/json"},
        )
        result = json.loads(res.data.decode())
        self.assertEqual(result["message"], "Invalid JSON data supplied.")
        self.assertEqual(res.status_code, 400)

    def test_already_registered_user(self):
        """Test user uniqueness."""
        res = self.client.post(
            "/register",
            json=self.user_data,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(res.status_code, 201)
        second_res = self.client.post(
            "/register",
            json=self.user_data,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(second_res.status_code, 400)
        result = json.loads(second_res.data.decode())
        self.assertEqual(result["message"], "User already exists.")

    def test_bad_value_type(self):
        """Test request with non-string email/password values."""
        # Test bad email
        res = self.client.post(
            "/register",
            json=self.bad_email,
            headers={"Content-Type": "application/json"},
        )
        result = json.loads(res.data.decode())
        self.assertEqual(result["message"], "Incorrect type for email and/or password.")
        self.assertEqual(res.status_code, 400)
        # Test bad email
        res = self.client.post(
            "/register",
            json=self.bad_email,
            headers={"Content-Type": "application/json"},
        )
        result = json.loads(res.data.decode())
        self.assertEqual(result["message"], "Incorrect type for email and/or password.")
        self.assertEqual(res.status_code, 400)

    def test_user_login(self):
        """Test registered user can get a token."""
        res = self.client.post(
            "/register",
            json=self.user_data,
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(res.status_code, 201)
        login_res = self.client.post(
            "/login", json=self.user_data, headers={"Content-Type": "application/json"}
        )
        result = json.loads(login_res.data.decode())
        self.assertEqual(result["message"], "Token generated with 5 minute expiration.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result["token"])

    def test_non_registered_user_login(self):
        """Test non registered users cannot get a token."""
        not_user = json.dumps({"email": "not@user.com", "password": "notauser"})
        res = self.client.post("/login", json=not_user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result["message"], "Invalid email or password. Please try again."
        )

    def test_login_bad_json(self):
        """Test user login fails gracefully when bad json sent."""
        res = self.client.post(
            "/login", json=self.bad_json, headers={"Content-Type": "application/json"}
        )
        result = json.loads(res.data.decode())
        self.assertEqual(result["message"], "Invalid JSON data supplied.")
        self.assertEqual(res.status_code, 400)
