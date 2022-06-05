from datetime import datetime, timedelta

from models.user import User
from models.therapist import Therapist, Specialism
from models.appointment import Appointment


def add_specialisms(therapist, specialisms):
    for name in specialisms:
        specialism = Specialism.query.filter_by(name=name).first()
        if specialism is None:
            specialism = Specialism(name)
        therapist.specialisms.append(specialism)
    return therapist


def insert_dummy_data(app):
    with app.app_context():
        # Create a user
        user = User("someone@test.com")
        user.set_password("randompassword")
        user.save()
        # Create a therapist with specialisms
        therapist = Therapist("John Smith")
        specialisms = ["Addiction", "CBT"]
        therapist = add_specialisms(therapist, specialisms)
        therapist.save()
        # Add some appointments
        appointment = Appointment(datetime.now() + timedelta(minutes=1), timedelta(minutes=60), "one-off", therapist)
        appointment.save()
        appointment = Appointment(datetime.now() + timedelta(days=14), timedelta(minutes=30), "consultation", therapist)
        appointment.save()
        # And another therapist
        therapist = Therapist("Jane Smith")
        specialisms = ["Sexuality", "CBT"]
        therapist = add_specialisms(therapist, specialisms)
        therapist.save()
        # Add some more appointments
        appointment = Appointment(datetime.now()+ timedelta(minutes=1), timedelta(minutes=60), "one-off", therapist)
        appointment.save()
        appointment = Appointment(datetime.now() + timedelta(days=3), timedelta(minutes=45), "consultation", therapist)
        appointment.save()


if __name__ == "__main__":
    insert_dummy_data()