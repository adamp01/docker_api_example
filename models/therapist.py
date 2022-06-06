from flask import current_app as app

from application import db

# Many-To-Many association
mtm_assoc = db.Table(
    "therapist_specialisms",
    db.Column("therapist_id", db.ForeignKey("therapists.id"), primary_key=True),
    db.Column("specialism_id", db.ForeignKey("specialism.id"), primary_key=True),
)


class Therapist(db.Model):
    """Class defining the schema for the therapists table"""

    __tablename__ = "therapists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    appointments = db.relationship("Appointment", back_populates="therapist")
    specialisms = db.relationship(
        "Specialism", secondary=mtm_assoc, back_populates="therapists"
    )

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()


class Specialism(db.Model):
    """Clas defining the schema for the specialisms table"""

    __tablename___ = "specialisms"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True)
    therapists = db.relationship(
        "Therapist", secondary=mtm_assoc, back_populates="specialisms"
    )

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()
