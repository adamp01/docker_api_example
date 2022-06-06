import html
from datetime import datetime, date, timedelta
from flask import request, jsonify, make_response
from flask import current_app as app
from models.user import User
from models.appointment import Appointment
from models.therapist import Therapist, Specialism
from application.main import generate_response
from application.auth.routes import auth_token_required


@app.route("/get_appointments", methods=["GET"])
@auth_token_required
def get_appointments():
    """Get appointments filtered by date, specialism or type.

    URL
    ----------
    GET /get_appointments

    Query Parameters
    ----------
    start :
        A date formatted string defining the start date to check for appointments.
    end :
        A date formatted string defining the end date to check for appointments.
    specialisms :
        A comma separated list of therapist specialisms.
    type :
        The type of appointments to find.

    Reponse
    -------
    400 :
        No query parameters found.
    200 :
          Appointments found: {int}
          Example :
            {
                "message": "Appointments found: 2.",
                "appointments": [
                    {
                        "time": "2022-06-06 09:41:00",
                        "duration": 60.0,
                        "therapist": "John Smith",
                        "type": "one-off",
                    },
                    {
                        "time": "2022-06-06 09:41:00",
                        "duration": 60.0,
                        "therapist": "Jane Smith",
                        "type": "one-off",
                    },
                ],
            }

    """
    args = request.args
    arg_keys = args.keys()
    # Return early if no query string params sent.
    if not arg_keys:
        return generate_response("No query parameters found.", 400)

    # If start and end dates passed, limit to that date range
    if "start" in arg_keys and "end" in arg_keys:
        start = html.escape(args["start"])
        end = html.escape(args["end"])
    else:
        start = date(1970, 1, 1)
        end = datetime(2999, 12, 12)

    # If specialisms passed, find therapists with those specialisms only
    if "specialisms" in arg_keys:
        specialisms = html.escape(args["specialisms"]).split(",")
        therapists = Therapist.query.filter(
            Therapist.specialisms.any(Specialism.name.in_(specialisms))
        ).all()
    else:
        therapists = Therapist.query.all()

    # If a specific type passed, use that, otherwise use the default options
    if "type" in arg_keys:
        appt_type = [html.escape(args["type"])]
    else:
        appt_type = Appointment.types()

    # Grab the list of appointments from the db according to filters
    appointments = Appointment.query.filter(
        Appointment.start_datetime.between(start, end),
        Appointment.therapist_id.in_([x.id for x in therapists]),
        Appointment.appointment_type.in_(appt_type),
    ).all()

    # Parse the appointments so we have the correct format
    parsed_appointments = list(
        map(
            lambda x: {
                "time": x.start_datetime,
                "duration": (x.end_datetime - x.start_datetime) / timedelta(minutes=1),
                "therapist": x.therapist.name,
                "type": x.appointment_type,
            },
            appointments,
        )
    )

    # Return the parsed appointments list
    return generate_response(
        f"Appointments found: {len(appointments)}",
        200,
        appointments=parsed_appointments,
    )


@app.route("/add_appointment", methods=["POST"])
@auth_token_required
def add_appointment():
    """Add new appointment.

    URL
    ----------
    POST /add_appointment

    Query Parameters
    ----------
    start :
        A datetime formatted string defining the start date of the appointment.
    duration :
        The duration of the appointment in minutes.
    type :
        The type of appointment to add.
    therapist_id :
        The id of the therapist to assign the appointment to.

    Response
    -------
    400 :
        Invalid query string values.
    200 :
          Appointment added.
          Example :
            {
                "message": "Appointment added.",
            }

    """
    args = request.args
    arg_keys = args.keys()
    # Only accept complete requests
    if (
        "start" not in arg_keys
        or "duration" not in arg_keys
        or "type" not in arg_keys
        or "therapist_id" not in arg_keys
    ):
        return generate_response(
            "Missing arguments. All of [start, duration, type, therapist_id] are required.",
            400,
        )

    if args["type"] not in Appointment.types():
        return generate_response(
            f"Incorrect type. Must be one of {Appointment.types()}", 400
        )

    therapist = Therapist.query.filter_by(id=html.escape(args["therapist_id"])).first()
    if therapist is None:
        return generate_response("Therapist not found.", 400)

    # Convert string times to datetime compatible objects
    try:
        start = datetime.strptime(args["start"], "%Y-%m-%d %H:%M")
        duration = timedelta(minutes=int(args["duration"]))
    except ValueError:
        return generate_response("Invalid start time or duration.", 400)

    # Actually add the appointment
    appointment = Appointment(start, duration, args["type"], therapist)
    res = appointment.save()

    # Ensure correct status code returned depending on save status
    if res == "Appointment added.":
        code = 200
    else:
        code = 400
    return generate_response(res, code)
