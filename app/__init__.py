from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
CORS(app)


app.config.from_object('config.Config')


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# Flask-Login setup for API backend only
login_manager = LoginManager()
login_manager.init_app(app)

from app import routes, models

