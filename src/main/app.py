from datetime import timedelta
from flask import Flask
from src.models.model import db
from flask_session import Session
from src.models.model import *
from Config.config import *

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Models.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db.init_app(app)



app.template_folder = "F:\\Open AI integration V1\\src\\templates"
app.static_folder = "F:\\Open AI integration V1\\src\\static"

from src.views.auth_view import auth_view
app.register_blueprint(auth_view)

from src.views.dashbord_view import dashboard_view
app.register_blueprint(dashboard_view)

from src.views.message_handle import message_view
app.register_blueprint(message_view)

from src.views.home_view import home_view
app.register_blueprint(home_view)