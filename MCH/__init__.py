from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# csrf = CSRFProtect(app)


app.config['SECRET_KEY'] = '12345'
app.config['WTF_CSRF_ENABLED'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:toor@localhost/musicChatDB'
db = SQLAlchemy(app)


# Initialize Flask-Migrate
migrate = Migrate(app, db)

from MCH import routes
