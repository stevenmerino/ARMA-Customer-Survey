from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.fields.html5 import DateField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, Regexp
from app.models import User, Speaker


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class AddressForm(FlaskForm):
    street = StringField("Street", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=2)])
    zip = StringField("Zip", validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=15, message="Username must be between 5 and 15 characters."), Regexp('^\w+$', message="Username must contain only letters numbers or underscore")])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Email already exists.")


class SpeakerForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone")
    street = StringField("Street", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=2)])
    zip = StringField("Zip", validators=[DataRequired()])
    submit = SubmitField("Save")


class EventForm(FlaskForm):
    topic = StringField("Topic", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()])
    street = StringField("Street", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=2)])
    zip = StringField("Zip", validators=[DataRequired()])
    speakers = QuerySelectMultipleField("Speakers")
    submit = SubmitField("Save")


class SurveyForm(FlaskForm):
    event = QuerySelectField("Event")

    value_1 = IntegerField("The topics were of valuable experience")
    value_2 = IntegerField("The program met my expectations")
    value_3 = IntegerField("The program increased my skills/awareness")
    value_4 = IntegerField("I would recommend this program to others")
    value_5 = IntegerField("The topics were of valuable experience")

    speaker_1 = IntegerField("The speaker(s) were knowledgeable and helpful")
    speaker_2 = IntegerField("The speaker(s) were clear, concise and easy to understand")
    speaker_3 = IntegerField("The speaker(s) were responsive to the participants")

    content_1 = IntegerField("The topic content will be useful in my current job")
    content_2 = IntegerField("The topic handouts (if provided) will be useful for future use")

    facility_1 = IntegerField("The meeting room was clean and comfortable")
    facility_2 = IntegerField("The quantity and quality of the food was good")

    response_1 = StringField("If you are not a memeber of ARMA, are you planning to join? If 'No', please share your reason(s)" )
    response_2 = StringField("We are constantly looking to improve the quality of the meeting experience for our memebers. We welcome your suggestions")
    response_3 = StringField("Is there another location where you would prefer to meet?")
    response_4 = StringField("Additional Comments")

    name = StringField("Name")
    email = StringField("Email", validators=[Email()])

    submit = SubmitField("Save")
