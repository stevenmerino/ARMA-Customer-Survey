from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import AddressForm

from app.models import User
from app.models import Address
from werkzeug.urls import url_parse

from flask_principal import Identity, AnonymousIdentity, identity_changed
from flask_principal import identity_loaded, RoleNeed, UserNeed, Permission


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


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


@app.route('/address', methods=['GET', 'POST'])
@login_required
def address():
    form = AddressForm()
    if form.validate_on_submit():
        address = Address(is_event=False, street=form.street.data, city=form.city.data, state=form.state.data, zip=form.zip.data)
        db.session.add(address)
        db.session.commit()
        flash("Address saved.")
        return redirect(url_for('login'))
    return render_template('address.html', title='Save Address', form=form)


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


admin_permission = Permission(RoleNeed('admin'))


@app.route('/admin')
@admin_permission.require(http_exception=403)
def admin():
    return render_template('admin.html', title='Admin Dashboard')


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'is_admin'):
        if current_user.is_admin:
            identity.provides.add(RoleNeed('admin'))
        #for role in current_user.roles:
            #identity.provides.add(RoleNeed(role.name))
