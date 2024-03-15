import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(500), primary_key=True, index=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(500), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

class Openai_thread(db.Model):
    thread_id = db.Column(db.String(500), primary_key=True)
    user_id = db.Column(db.String(500), db.ForeignKey("user.id"), nullable=False)
    chat_id = db.Column(db.String(500), nullable=False)
    configuration = db.Column(db.String(500), nullable=False)

class Chat_data(db.Model):
    msg_id = db.Column(db.String(500), primary_key=True, nullable=False, default=str(uuid.uuid4()))
    chat_id = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.String(500), db.ForeignKey("user.id"), nullable=False)
    date_time = db.Column(db.String(500), nullable=False)
    sender_name = db.Column(db.String(500), nullable=False)
    user_message = db.Column(db.String(1500), nullable=False)
    response = db.Column(db.String(2000), nullable=False)
    configuration = db.Column(db.String(500), nullable=False)
    configuration_id = db.Column(db.String(500), nullable=False)