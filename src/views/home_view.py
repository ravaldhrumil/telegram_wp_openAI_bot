from twilio.rest import Client
from flask import Blueprint, redirect, url_for

home_view = Blueprint("home_view", __name__)


@home_view.route("/home/<msg>")
@home_view.route("/home")
def home(msg=None):
    if msg:
        return f"{msg}"
    else:
        return "Normal"
    
@home_view.route("/abc")
def abc():
    msg = "This is message"
    return redirect(url_for("home_view.home", msg=msg))