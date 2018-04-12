from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import column_property


event_speakers = db.Table('event_speakers',
                          db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                          db.Column('speaker_id', db.Integer, db.ForeignKey('speaker.id'))
                          )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(144), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    speaker_id = db.Column(db.Integer, db.ForeignKey('speaker.id'))


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    street = db.Column(db.String(120), index=True)
    city = db.Column(db.String(60), index=True)
    state = db.Column(db.CHAR(2))
    zip = db.Column(db.Integer)

    event = db.relationship('Event', back_populates='address')
    speaker = db.relationship('Speaker', back_populates='address')


class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    name = column_property(first_name + ' ' + last_name)
    email = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(120))

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', back_populates='speaker')

    knowledge_average = db.Column(db.Float)
    concise_average = db.Column(db.Float)
    responsive_average = db.Column(db.Float)
    overall_average = db.Column(db.Float)

    comments = db.relationship('Comment', backref='speaker')

    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), index=True)
    date = db.Column(db.Date())

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', back_populates='event')
    speakers = db.relationship('Speaker',
                               secondary=event_speakers, backref=db.backref('events', lazy='dynamic')
                               )
    survey = db.relationship('Survey', back_populates='event')

    value_average = db.Column(db.Float)
    speakers_average = db.Column(db.Float)
    content_average = db.Column(db.Float)
    facility_average = db.Column(db.Float)
    overall_average = db.Column(db.Float)

    comments = db.relationship('Comment', backref='event', lazy='dynamic')

    def __repr__(self):
        return '{} - {}'.format(self.topic, self.date)


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value_1 = db.Column(db.Integer)
    value_2 = db.Column(db.Integer)
    value_3 = db.Column(db.Integer)
    value_4 = db.Column(db.Integer)
    value_5 = db.Column(db.Integer)
    value_average = db.Column(db.Float)

    speaker_1 = db.Column(db.Integer)
    speaker_2 = db.Column(db.Integer)
    speaker_3 = db.Column(db.Integer)
    speaker_average = db.Column(db.Float)

    content_1 = db.Column(db.Integer)
    content_2 = db.Column(db.Integer)
    content_average = db.Column(db.Float)

    facility_1 = db.Column(db.Integer)
    facility_2 = db.Column(db.Integer)
    facility_average = db.Column(db.Float)

    overall_average = db.Column(db.Float)

    response_1 = db.Column(db.String(144))
    response_2 = db.Column(db.String(144))
    response_3 = db.Column(db.String(144))
    response_4 = db.Column(db.String(144))
    name = db.Column(db.String(144))
    email = db.Column(db.String(144))

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event', back_populates='survey')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    is_admin = db.Column(db.Boolean, default=False)
    is_editor = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
