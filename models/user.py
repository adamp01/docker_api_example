import jwt

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app

from application import db


class User(db.Model):
    """Class defining the schema for the users table"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    appointments = db.relationship("Appointment", back_populates="client")

    def __repr__(self):
        return "User email: {0}".format(self.email)

    def __init__(self, email):
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate user access token."""
        try:
            # Set payload with expiration time
            payload = {
                "exp": datetime.utcnow() + timedelta(minutes=5),
                "iat": datetime.utcnow(),
                "sub": self.email,
            }
            # Create byte string token using payload and SECRET
            jwt_string = jwt.encode(
                payload, app.config.get("SECRET"), algorithm="HS256"
            )
            return jwt_string
        except TypeError:
            return "Please set SECRET env variable to a string value."
        except Exception as e:
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes access token from Authorisation header."""
        try:
            payload = jwt.decode(token, app.config.get("SECRET"), algorithms="HS256")
            return payload["sub"].encode()
        except jwt.ExpiredSignatureError:
            return "Expired token. Please login to get new token."
        except jwt.InvalidTokenError:
            return "Invalid token. Please register or login."

    def save(self):
        db.session.add(self)
        db.session.commit()
