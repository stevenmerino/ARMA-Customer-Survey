from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_event = db.Column(db.Boolean, index=True)
    street = db.Column(db.String(120), index=True)
    city = db.Column(db.String(60), index=True)
    state = db.Column(db.CHAR(2))
    zip = db.Column(db.Integer)


class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(120), index=True)
    speaker_address = db.Column(db.Integer, db.ForeignKey('address.id'))


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), index=True)
    date = db.Column(db.Date())
    event_address = db.Column(db.Integer, db.ForeignKey('address.id'))


class EventSpeakers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Integer, db.ForeignKey('event.id'))
    speaker = db.Column(db.Integer, db.ForeignKey('speaker.id'))


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.Integer, db.ForeignKey('event.id'))
    value_1 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    value_2 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    value_3 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    value_4 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    value_5 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    speaker_1 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    speaker_2 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    speaker_3 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    content_1 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    content_2 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    facility_1 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    facility_2 = db.Column(db.Enum('1', '2', '3', '4', '5'))
    response_1 = db.Column((db.String(144)))
    response_2 = db.Column((db.String(144)))
    response_3 = db.Column((db.String(144)))
    response_4 = db.Column((db.String(144)))
    name = db.Column((db.String(120)))
    email = db.Column((db.String(120)))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_editor = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
