from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, validators, SubmitField
from MCH import app, db
from MCH.models import User, Playlist, Track, ChatMessage
import requests
from MCH.spotify import search_spotify
from flask_wtf import FlaskForm 
from wtforms.validators import DataRequired

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
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form['search']
        results = search_spotify(query)
        return render_template('search_results.html', results=results)
    return render_template('search.html')

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm(request.form)
    if request.method == 'POST' and form.validate():
        playlist = Playlist(name=form.name.data, user_id=current_user.id)
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist created successfully.')
        return redirect(url_for('index'))
    return render_template('create_playlist.html', form=form)

@app.route('/add_to_playlist/<playlist_id>', methods=['POST'])
@login_required
def add_to_playlist(playlist_id):
    track_data = request.get_json().get('track_data')

    # Check if the track is already in the playlist
    existing_track = Track.query.filter_by(playlist_id=playlist_id, spotify_track_id=track_data['id']).first()
    if existing_track:
        flash('This track is already in the playlist.')
        return redirect(request.referrer)

    # Create a new Track object and add it to the playlist
    track = Track(
        title=track_data['name'],
        artist=track_data['artists'],
        album=track_data['album'],
        playlist_id=playlist_id,
        spotify_track_id=track_data['id'],
        track_uri=track_data['uri'],
        album_uri=track_data['album_uri'],
        artist_uri=track_data['artist_uri'],
        album_cover_url=track_data['album_cover_url'],
        release_date=track_data['release_date']
    )
    db.session.add(track)
    db.session.commit()
    flash('Track added to the playlist.')
    return redirect(request.referrer)



# Add a route for fetching track details using the Spotify API
@app.route('/track/<track_id>')
@login_required
def track_details(track_id):
    # Call the Spotify API track endpoint with the track_id
    # Parse the track details and render them in the track details template
    pass
