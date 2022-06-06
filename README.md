## Initial Architectural Decisions
Before writing any code I'm going to briefly decide on a basic structure.
As we are wanting this to be a high availability and scalable API the 
database and API should be distinct services. This will allow us to scale
the number of API instances and still allow a new instance to access pre-
existing data. I'll use a simple docker-compose file for this purpose.

I also want to ensure that the API is built with readibility and 
maintainability at it's core. As such models and endpoints will 
be clearly segregated based upon what they relate to, e.g. auth
or appointments.

I've decided to use Flask as a framework for the API as it is 
what I am most familiar with. Frameworks like FastAPI or Sanic
would likely provide performance benefits, but for the purposes
of this exercise I thought I'd stick with what I have used the most.

Configurations should be easily changed so that we can deploy to a
variety of environments without undergoing any length code changes.
In this case I'll use a `config.py` to hold configs for `dev, test, prod`.
We can decide which config to deploy with by setting the `APPLICATION_STAGE`
environment variable.

Finally, there will be a testing directory that will also be split out
depending on what overarching functionality they relate to.

Note:  
As I am reviewing my work the next day, I've noticed two very obvious improvements. Firstly 
the endpoints should probably be behind a version number, such as `/api/v1/get_appointments`.
Otherwise what happens if we have a major refactor of the codebase at some point in the
future? Our API will be at risk of breakage for many users. 
Secondly, the checking for presence of at least one query string param in `/get_appointments`
is redundant as we add default if the key isn't present. This would allow us to simply
request all appointments by not supplying any query string params. Removing lines
16-18 of application/appointments/routes.py would resolve this (and updating tests accordingly).

## Deploying
To deploy the API run:  
`docker-compose -f docker-compose.yml up -d --build`

## Running tests
Test can be run with (Note: running tests on prod will clear out the database):  
`docker-compose exec web python manage.py test`

## Creating and Seeding Database
To create the database and tables run:  
`docker-compose exec web python manage.py create_db`

To seed the database with some dummy data run:  
`docker-compose exec web python manage.py seed_db`

You can verify that the database has been created and seeded by running:  
`docker-compose exec db psql --username=prod_user --dbname=prod_db`  
`psql=# \c prod_db`  
`prod_db=# select * from therapists;`  

## Example requests
To register to an auth token:  
`curl -X POST -H "Content-Type: application/json" --data "{\"email\": \"test@test.com\", \"password\": \"testpassword\"}" http://localhost:5000/register`

To request an auth token:  
`curl -X POST -H "Content-Type: application/json" --data "{\"email\": \"test@test.com\", \"password\": \"testpassword\"}" http://localhost:5000/login`

Appointments can be filtered by passing one or more of the following query string params:
* start: The start date of the range query. Must be passed with end. Format: YYY-MM-DD
* end: The end date of the range query. Must be passed with start. Format: YYY-MM-DD
* specialisms: A comma separated list of specialisms that a Therapist has. Format: spec1,spec2,spec3
* type: The type of appointment. Must be one of one-off or consultation.

Example:  
`curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer {token}" "http://localhost:5000/get_appointments?start=2022-05-03&end=2022-06-25&specialisms=Addiction&type=one-off"`

An appointment can be added by sending a POST request to `/add_appointments` with all the following query string parameters:
* start: The start datetime of the appointment. Format YYYY-MM-DD%20HH:mm
* duration: The duration of the appointment, in minutes.
* type: The type of appointment. Must be one of one-off or consultation.
* therapist_id: The id of the therapist to assign the appointment to. Seed data will provide two therapists with id 1 and 2.  
Notes:  
* Appointment times for a therapist cannot overlap.
* Appointment time must not be in the past.

Example:  
`curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer {token}" "http://localhost:5000/add_appointment?start=2022-06-06%2012:41&duration=60&type=one-off&therapist_id=1"`

## Destroying
To spin down the API and database run:  
`docker-compose -f docker-compose.yml down -v`

