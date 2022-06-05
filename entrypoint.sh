#!/bin/sh

# Wait for postgres to be alive before attempting to run the flask app
if [ "$DB_TYPE" = "postgres" ]
then
    while ! nc -z $DB_HOST $DB_POST; do
      sleep 0.1
    done
fi

exec "$@"
