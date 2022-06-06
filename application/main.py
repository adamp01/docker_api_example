import logging.config

from flask import Flask, make_response, jsonify
from config import configurations
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Set up logging
logging.config.fileConfig("./logging.ini", disable_existing_loggers=False)
logger = logging.getLogger("main")


def generate_response(msg, code, **kwargs):
    """Helper to generate a nicely formatted response."""
    response = {
        "message": msg,
    }
    for k, v in kwargs.items():
        response[k] = v
    # Log 4xx and 5xx errors
    if int(str(code)[0]) in [4, 5]:
        logging.error(response)
    return make_response(jsonify(response)), code


def create_app(config):
    """Factory to set up the flask app."""
    # Import the relevant models
    from models.appointment import Appointment
    from models.therapist import Therapist, Specialism
    from models.user import User

    # Set up and configure the app and db objects
    app = Flask(__name__)
    app.config.from_object(configurations[config])
    db.init_app(app)
    migrate.init_app(app, db)
    # Register the routes
    with app.app_context():
        import application.auth.routes
        import application.appointments.routes

    return app
