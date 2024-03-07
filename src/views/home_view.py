import threading
from flask import Blueprint, request
import flask
from src.models.model import *
from src.main.app import app

home_view = Blueprint(
    'home_view',
    __name__
)


@home_view.get('/home')
def handle_home():
    thread1 = threading.Thread(target=abc)
    thread1.start()
    
    return "ADDED"




def abc():
    xyz()

def xyz():
    lmn()

def lmn():
    with app.app_context():
        new_thread = Openai_thread(user_id="123", thread_id="123", chat_id="123", configuration="telegram")
        db.session.add(new_thread)
        db.session.commit()