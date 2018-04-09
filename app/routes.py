from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import AddressForm
from app.forms import SpeakerForm
from app.forms import EventForm
from app.forms import SurveyForm

from app.models import User
from app.models import Address
from app.models import Speaker
from app.models import Event
from app.models import Survey

from werkzeug.urls import url_parse

from flask_principal import Identity, AnonymousIdentity, identity_changed
from flask_principal import identity_loaded, RoleNeed, UserNeed, Permission

admin_permission = Permission(RoleNeed('admin'))
editor_permission = Permission(RoleNeed('editor'))
verified_permission = Permission(RoleNeed('verified'))

##### fix wtforms-sqlalchemy query factory bug
import wtforms_sqlalchemy.fields as f
def get_pk_from_identity(obj):
    cls, key = f.identity_key(instance=obj)[:2]
    return ':'.join(f.text_type(x) for x in key)
f.get_pk_from_identity = get_pk_from_identity
#######

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', title='Home')
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # Testing Principal identity - change identity
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        # End test
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# @app.route('/address', methods=['GET', 'POST'])
# @login_required
# def address():
#     form = AddressForm()
#     if form.validate_on_submit():
#         address = Address(is_event=False, street=form.street.data, city=form.city.data, state=form.state.data, zip=form.zip.data)
#         db.session.add(address)
#         db.session.commit()
#         flash("Address saved.")
#         return redirect(url_for('login'))
#     return render_template('address.html', title='Save Address', form=form)


# @app.route('/addresses')
# @login_required
# @verified_permission.require(http_exception=403)
# def show_address():
#     addresses = Address.query.all()
#     return render_template('addresses.html', title='Address List', addresses=addresses)


@app.route('/logout')
def logout():
    logout_user()
    # Testing Principal - set user to anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    # End test
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful.")
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)


@app.route('/admin')
@admin_permission.require(http_exception=403)
def admin():
    users = User.query.all()
    return render_template('admin.html', title='Admin Dashboard', users=users)


@app.route('/update/admin/<username>')
@login_required
@admin_permission.require(http_exception=403)
def admin_update(username):
    user = User.query.filter_by(username=username).first_or_404()
    user.is_admin = not user.is_admin
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/update/editor/<username>')
@login_required
@admin_permission.require(http_exception=403)
def editor_update(username):
    user = User.query.filter_by(username=username).first_or_404()
    user.is_editor = not user.is_editor
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/update/verified/<username>')
@login_required
@admin_permission.require(http_exception=403)
def verified_update(username):
    user = User.query.filter_by(username=username).first_or_404()
    user.is_verified = not user.is_verified
    db.session.commit()
    return redirect(url_for('admin'))


def update_speaker(speaker):
    knowledge = concise = responsive = count = 0
    for event in speaker.events:
        for survey in event.survey:
            count += 1
            knowledge += survey.speaker_1
            concise += survey.speaker_2
            responsive += survey.speaker_3
    if count is not 0:
        knowledge = knowledge / count
        concise = concise / count
        responsive = responsive / count
        overall_average = (knowledge + concise + responsive) / 3
        speaker.knowledge_average = knowledge
        speaker.concise_average = concise
        speaker.responsive_average = responsive
        speaker.overall_average = overall_average
        db.session.commit()


@app.route('/show/speakers', methods=['GET', 'POST'])
@login_required
@verified_permission.require(http_exception=403)
def show_speakers():
    page = request.args.get('page', 1, type=int)
    speakers = Speaker.query.order_by(Speaker.id.desc()).paginate(page, app.config['ITEMS_PER_PAGE'], False)
    for speaker in speakers.items:
        update_speaker(speaker)
    next_url = url_for('show_speakers', page=speakers.next_num) if speakers.has_next else None
    prev_url = url_for('show_speakers', page=speakers.prev_num) if speakers.has_prev else None
    return render_template('show_speakers.html', title='Speaker List', speakers=speakers.items, next_url=next_url, prev_url=prev_url)


@app.route('/add/speaker', methods=['GET', 'POST'])
@login_required
@editor_permission.require(http_exception=403)
def add_speaker():
    form = SpeakerForm()
    if form.validate_on_submit():
        address = Address(street=form.street.data, city=form.city.data, state=form.state.data,
                          zip=form.zip.data)
        speaker = Speaker(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                          phone=form.phone.data)
        db.session.add(speaker)
        db.session.commit()
        speaker.address = address
        db.session.commit()
        flash("Speaker Saved.")
        return redirect(url_for('index'))
    return render_template('add_speaker.html', title='Add Speaker', form=form)


@app.route('/show/events', methods=['GET', 'POST'])
@login_required
@editor_permission.require(http_exception=403)
def show_events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.date.desc()).paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('show_events', page=events.next_num) if events.has_next else None
    prev_url = url_for('show_events', page=events.prev_num) if events.has_prev else None
    return render_template('show_events.html', title='Event List', events=events.items, next_url=next_url, prev_url=prev_url)


def speaker_query():
    return Speaker.query


@app.route('/add/event', methods=['GET', 'POST'])
@login_required
@editor_permission.require(http_exception=403)
def add_event():
    form = EventForm()
    form.speakers.query_factory = speaker_query
    if form.validate_on_submit():
        address = Address(street=form.street.data, city=form.city.data, state=form.state.data, zip=form.zip.data)
        event = Event(topic=form.topic.data, date=form.date.data)
        db.session.add(event)
        db.session.commit()
        event.address = address
        for speaker in form.speakers.data:
            event.speakers.append(speaker)
        db.session.commit()
        flash("Event Saved.")
        return redirect(url_for('index'))
    return render_template('add_event.html', title='Add Event', form=form)


@app.route('/show/surveys', methods=['GET', 'POST'])
@login_required
@editor_permission.require(http_exception=403)
def show_surveys():
    page = request.args.get('page', 1, type=int)
    surveys = Survey.query.order_by(Survey.id.desc()).paginate(page, app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('show_surveys', page=surveys.next_num) if surveys.has_next else None
    prev_url = url_for('show_surveys', page=surveys.prev_num) if surveys.has_prev else None
    return render_template('show_surveys.html', title='Survey List', surveys=surveys.items, next_url=next_url, prev_url=prev_url)



def event_query():
    return Event.query


@app.route('/add/survey', methods=['GET', 'POST'])
@login_required
@editor_permission.require(http_exception=403)
def add_survey():
    form = SurveyForm()
    form.event.query_factory = event_query
    if form.validate_on_submit():
        value_average = (form.value_1.data + form.value_2.data + form.value_3.data + form.value_4.data + form.value_5.data) / 5
        speaker_average = (form.speaker_1.data + form.speaker_2.data + form.speaker_3.data) / 3
        content_average = (form.content_1.data + form.content_2.data) / 2
        facility_average = (form.facility_1.data + form.facility_2.data) / 2
        overall_average = (value_average + speaker_average + content_average + facility_average) / 4
        survey = Survey(value_1=form.value_1.data, value_2=form.value_2.data, value_3=form.value_3.data,
                        value_4=form.value_4.data, value_5=form.value_5.data, value_average=value_average,
                        speaker_1=form.speaker_1.data, speaker_2=form.speaker_2.data, speaker_3=form.speaker_3.data,
                        speaker_average=speaker_average, content_1=form.content_1.data, content_2=form.content_2.data,
                        content_average=content_average, facility_1=form.facility_1.data, facility_2=form.facility_2.data,
                        facility_average=facility_average, response_1=form.response_1.data, response_2=form.response_2.data,
                        response_3=form.response_3.data, response_4=form.response_4.data, name=form.name.data,
                        email=form.email.data, overall_average=overall_average
                        )

        db.session.add(survey)
        db.session.commit()
        survey.event = form.event.data
        db.session.commit()
        flash("Survey Saved.")
        return redirect(url_for('index'))
    return render_template('add_survey.html', title='Add Survey', form=form)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'is_admin'):
        if current_user.is_admin:
            identity.provides.add(RoleNeed('admin'))

    if hasattr(current_user, 'is_verified'):
        if current_user.is_verified:
            identity.provides.add(RoleNeed('verified'))

    if hasattr(current_user, 'is_editor'):
        if current_user.is_editor:
            identity.provides.add(RoleNeed('editor'))
