from datetime import timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, session, url_for
from src.models.model import *
from werkzeug.security import generate_password_hash, check_password_hash
from src.main.app import app
import jwt
from functools import wraps

auth_view = Blueprint("auth_view", __name__)

def check_for_token(func):
    @wraps(func)
    def wrapped(*args,**kwargs):
        token = session.get("token")
        if not token:
            return jsonify({"message": "Pehle Token Leke Aao Munna"}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            return func(*args, token_data=data, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 403

    return wrapped

@auth_view.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@auth_view.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    elif request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            error = f"Email {email} already exists."
            return render_template("register.html", error=error)
        
        hash_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hash_password)
        db.session.add(new_user)
        db.session.commit()

        user = User.query.filter_by(email=email).first()
        payload = {'user_id': user.id,
                   'exp': datetime.utcnow() + timedelta(hours=1)}

        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")

        session["token"] = token
        return  redirect(url_for("dashboard_view.dashboard", token = token))



        # msg = f"User with email {email} is registered successfully"
        # return render_template("index.html", msg=msg)
    
@auth_view.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        email = request.form['email']
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            msg = "Wrong email or password"
            return render_template("login.html", msg=msg)
        
        payload = {'user_id': user.id,
                   'exp': datetime.utcnow() + timedelta(hours=1)}

        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")

        session["token"] = token
        return  redirect(url_for("dashboard_view.dashboard", token = token))
