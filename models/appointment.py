from datetime import datetime
from flask import current_app as app

from application import db
from .therapist import Therapist


class Appointment(db.Model):
    """Class defining the schema for the appointments table"""

    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, index=True)
    end_datetime = db.Column(db.DateTime)
    appointment_type = db.Column(db.String(120))
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    client = db.relationship("User", back_populates="appointments")
    therapist_id = db.Column(db.Integer, db.ForeignKey("therapists.id"))
    therapist = db.relationship("Therapist", back_populates="appointments")

    def __init__(self, datetime, length, appointment_type, therapist, client=None):
        self.start_datetime = datetime
        self.end_datetime = datetime + length
        self.appointment_type = appointment_type
        self.client = client
        self.therapist = therapist

    def save(self):
        # Don't want to be able to add appointments in the past
        if self.start_datetime < datetime.now():
            return "Cannot add an appointment in the past."

        therapist = Therapist.query.filter_by(id=self.therapist.id).first()
        # Find if the therapist already has an appointment at the requested time.
        overlap = list(
            filter(
                lambda x: x.id != self.id
                and x.start_datetime <= self.start_datetime <= x.end_datetime
                and x.start_datetime <= self.end_datetime <= x.end_datetime,
                therapist.appointments,
            )
        )
        if not overlap:
            db.session.add(self)
            db.session.commit()
            return "Appointment added."
        return "Overlapping with existing appointment."

    @staticmethod
    def types():
        return ["one-off", "consultation"]
