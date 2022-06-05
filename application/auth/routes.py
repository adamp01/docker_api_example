import json
import html
from functools import wraps
from flask import request
from flask import current_app as app
from sqlalchemy import exc
from application.main import generate_response
from models.user import User


def auth_token_required(f):
    """Decorator to secure endpoints."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            # Get access token from header
            auth_header = request.headers.get('Authorization')
            access_token = auth_header.split(' ')[1]
        except AttributeError:
            # Occurs in event of no Authorisation header
            return generate_response('Invalid Authorization token in header.', 401)
        if access_token:
            # Attempt to decode token for User ID           
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                return f(*args, **kwargs)
            else:
                # String user_id indicates invalid token
                return generate_response(user_id, 401)
        return f(*args, **kwargs)
    return wrapper

def get_args(data):
    try:
        # Data could be an already parsed dict or a json string
        if isinstance(data, str):
            return json.loads(data)
        else:
            return data
    except TypeError:
        return generate_response(f"Invalid JSON data supplied.", 400)
    except json.decoder.JSONDecodeError:
        return generate_response(f"Invalid JSON data supplied.", 400)

@app.route("/register", methods=["POST"])
def register():
    # Get the request arguments
    args = get_args(request.json)

    # args will only be a tuple if loading failed
    if isinstance(args, tuple):
        return args

    # Ensure we have both email and password
    if list(args.keys()) != ['email', 'password']:
        return generate_response('email and/or password not passed with request.', 400)

    # Make sure that email and password are both string values
    if not isinstance(args['email'], str) or not isinstance(args['password'], str):
        return generate_response('Incorrect type for email and/or password.', 400)

    # Add a new user
    try:
        user = User(html.escape(args['email']))
        user.set_password(html.escape(args['password']))
        user.save()
        return generate_response(f'Successfully registered new user: {user.email}', 201)
    except exc.IntegrityError:
        return generate_response(f'User already exists.', 400)
    except Exception as e:
        return generate_response( f'Error adding user.', 500)


@app.route("/login", methods=["POST"])
def login():
    # Get request arguments
    args = get_args(request.json)

    # Args will only be a tuple if loading failed
    if isinstance(args, tuple):
        return args

    # Ensure we have both email and password
    if list(args.keys()) != ['email', 'password']:
        return generate_response('email and/or password not passed with request.', 400)
    
    try:
        user = User.query.filter_by(email=html.escape(args['email'])).first()
        # If user not found or password is incorrect, unauthorized
        if user is None or not user.check_password(html.escape(args['password'])):
            return generate_response('Invalid email or password. Please try again.', 401)

        # Generate and return token 
        token = user.generate_token()
        return generate_response('Token generated with 5 minute expiration.', 200, token=token)
    except Exception as e:
        return generate_response(f'Error retrieving token: {e}', 500)
