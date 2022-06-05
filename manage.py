import os
import unittest

from flask.cli import FlaskGroup

from application import create_app, db
from tests import test_appointments, test_auth, create_dummy_data


app = create_app(os.getenv("APPLICATION_STAGE"))

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    create_dummy_data.insert_dummy_data(app)


@cli.command("test")
def test():
    # Initialize the test suite
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # Add tests to the test suite
    suite.addTests(loader.loadTestsFromModule(test_appointments))
    suite.addTests(loader.loadTestsFromModule(test_auth))

    # Run the suite
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)


if __name__ == "__main__":
    cli()
