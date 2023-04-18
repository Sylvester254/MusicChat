from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:toor@localhost/musicChatDB'
db = SQLAlchemy(app)


# Initialize Flask-Migrate
migrate = Migrate(app, db)

from MCH import routes
