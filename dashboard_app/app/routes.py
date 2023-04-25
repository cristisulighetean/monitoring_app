from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from app.models import User, Sensor
import requests

from app.forms import LoginForm, RegistrationForm, AddSensorForm
from werkzeug.security import generate_password_hash, check_password_hash

import logging
logger = logging.getLogger(app.logger.name)

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    sensors = Sensor.query.all()
    return render_template('index.html', sensors=sensors)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # Write user to the database
        try:
            db.session.add(user)
            db.session.commit()
            logger.debug("User added to the db")
        except:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            logger.debug("User NOT added to the db")
            return render_template('register.html', title='Register', form=form)
        flash('Account created successfully! You can now log in.', 'success')

        # Send user to the login page
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/add_sensor', methods=['GET', 'POST'])
@login_required
def add_sensor():
    form = AddSensorForm()
    if form.validate_on_submit():
        # Data is valid
        name = form.name.data
        ip = form.ip.data

        # Check if sensor already exists
        existing_sensor = Sensor.query.filter((Sensor.name == name) | (Sensor.ip == ip)).first()
        if existing_sensor:
            flash('Sensor with the same name or IP already exists', 'danger')
        else:
            # Check if sensor is online
            try:
                response = requests.get(f'http://{ip}/status', timeout=5)
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                flash('Error communicating with the sensor: ' + str(e), 'danger')
                return render_template('add_sensor.html', form=form)
            if response.text == 'sensor_online':
                new_sensor = Sensor(name=name, ip=ip)
                try:
                    db.session.add(new_sensor)
                    db.session.commit()
                except:
                    db.session.rollback()
                    flash('Failed to add the sensor', 'danger')
                    #return render_template('add_sensor.html', form=form)
                flash('Sensor added successfully', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Sensor is not available', 'danger')

    return render_template('add_sensor.html', form=form)


@app.route('/reset_sensor/<int:sensor_id>')
@login_required
def reset_sensor(sensor_id):
    sensor = Sensor.query.get(sensor_id)
    if sensor:
        try: 
            response = requests.get(f'http://{sensor.ip}/reset')
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            flash('Error communicating with the sensor:'+ str(e), 'danger')
            return render_template('add_sensor.html')
        if response.text == 'reset_success':
            flash('Sensor reset successfully', 'success')
        else:
            flash('Failed to reset the sensor', 'danger')
    else:
        flash('Sensor not found', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/restart_sensor/<int:sensor_id>')
@login_required
def restart_sensor(sensor_id):
    sensor = Sensor.query.get(sensor_id)
    if sensor:
        try: 
            response = requests.get(f'http://{sensor.ip}/restart')
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            flash('Error communicating with the sensor:'+ str(e), 'danger')
            return render_template('add_sensor.html')
        if response.text == 'restart_success':
            flash('Sensor restarted successfully', 'success')
        else:
            flash('Failed to restart the sensor', 'danger')
    else:
        flash('Sensor not found', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/delete_sensor/<int:sensor_id>')
@login_required
def delete_sensor(sensor_id):
    sensor = Sensor.query.get(sensor_id)
    if sensor:
        db.session.delete(sensor)
        db.session.commit()
        flash('Sensor deleted successfully', 'success')
    else:
        flash('Sensor not found', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))