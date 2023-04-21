from flask import render_template, request, redirect, session, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from google.auth import jwt as google_jwt
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, validators, SubmitField
from MCH import app, db
from MCH.models import User, Playlist, Track, ChatMessage
import requests
from MCH.spotify import search_spotify
from flask_wtf import FlaskForm 
from flask_wtf.csrf import generate_csrf
from twilio.rest import Client
from wtforms.validators import DataRequired
from firebase_admin import auth, initialize_app
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth


cred = credentials.Certificate("/home/silver/ALX-Software_engineering/musicchat-firebasekey.json")
firebase_admin.initialize_app(cred)

class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired()])
    submit = SubmitField('Create Playlist')


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField(
        'Email', [validators.Length(min=6, max=50), validators.Email()])
    display_name = StringField(
        'Display Name', [validators.DataRequired(), validators.Length(min=4, max=15)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')


class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


@app.route('/')
@app.route('/index')
def index():
    csrf_token = generate_csrf()
    custom_token = session.get('custom_token', None)
    return render_template('index.html', csrf_token=csrf_token, custom_token=custom_token)


@app.route('/register', methods=['GET', 'POST'])
def register():
    csrf_token = generate_csrf()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        display_name = form.display_name.data
        password = generate_password_hash(form.password.data)
        user = User(username=username, email=email,
                    display_name=display_name, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, csrf_token=csrf_token)


@app.route('/login', methods=['GET', 'POST'])
def login():
    csrf_token = generate_csrf()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            # Generate a custom token for the user
            custom_token = auth.create_custom_token(str(user.id))
            print("Server-side Custom Token:", custom_token)

            # Store the custom token in the user's session
            session['custom_token'] = custom_token.decode('utf-8')

            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form, csrf_token=csrf_token)


@app.route('/logout')
@login_required
def logout():
    if 'custom_token' in session:
        session.pop('custom_token')
    logout_user()
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    csrf_token = generate_csrf()
    if request.method == 'POST':
        query = request.form['search']
        results = search_spotify(query)
        return render_template('search_results.html', results=results, csrf_token=csrf_token)
    return render_template('search.html')

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    csrf_token = generate_csrf()
    form = PlaylistForm(request.form)
    if request.method == 'POST' and form.validate():
        playlist = Playlist(name=form.name.data, user_id=current_user.id)
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist created successfully.')
        return redirect(url_for('index'))

    # Fetch user's playlists and their tracks
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    for playlist in playlists:
        playlist.tracks = Track.query.filter_by(playlist_id=playlist.id).all()

    return render_template('create_playlist.html', form=form, csrf_token=csrf_token, playlists=playlists)

@app.route('/add_to_playlist/<playlist_id>', methods=['POST'])
@login_required
def add_to_playlist(playlist_id):
    track_data = request.get_json().get('track_data')
    
    if track_data is None:
        return jsonify(status='error', message='Error adding track to the playlist. Track data is missing.')

    else:
        # Check if the track is already in the playlist
        existing_track = Track.query.filter_by(playlist_id=playlist_id, spotify_track_id=track_data['id']).first()
        if existing_track:
            return jsonify(status='warning', message='This track is already in the playlist.')

        # Create a new Track object and add it to the playlist
        track = Track(
            title=track_data['name'],
            artist=track_data['artists'][0]['name'],
            album=track_data['album']['name'],
            playlist_id=playlist_id,
            spotify_track_id=track_data['id'],
            track_uri=track_data['uri'],
            album_uri=track_data['album']['uri'],
            artist_uri=track_data['artists'][0]['uri'],
            album_cover_url=track_data['album']['images'][0]['url'],
            release_date=track_data['album']['release_date']
        )

        db.session.add(track)
        db.session.commit()
        return jsonify(status='success', message='Track added to the playlist.')

@app.route('/chat')
@login_required
def chat():
    custom_token = session.get('custom_token', None)
    csrf_token = generate_csrf()
    return render_template('chat.html', csrf_token=csrf_token, custom_token=custom_token)
