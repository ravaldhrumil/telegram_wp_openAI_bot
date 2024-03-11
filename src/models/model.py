import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String, primary_key=True, index=True, default=str(uuid.uuid4()))
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

    def __repr__(self):
        return f"User(name={self.name}, email={self.email})"

class Integration(db.Model):
    integration_id = db.Column(db.String, primary_key=True, nullable=False, default=str(uuid.uuid4()))
    configuration = db.Column(db.String, nullable=False)
    # bot_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    # status = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"configuration={self.configuration})"

class Telegram_configuration(db.Model):
    configuration_id = db.Column(db.String, primary_key=True, nullable=False, default=str(uuid.uuid4()))
    open_ai_key = db.Column(db.String, nullable=False)
    assistant_id = db.Column(db.String, nullable=False)
    bot_token = db.Column(db.String, nullable=False, unique=True)
    configuration = db.Column(db.String, db.ForeignKey("integration.configuration"), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    integration_id = db.Column(db.String, db.ForeignKey("integration.integration_id"), nullable=False)

    def __repr__(self):
        return f"configuration={self.configuration})"
    
class Openai_thread(db.Model):
    thread_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    chat_id = db.Column(db.String, nullable=False)
    configuration = db.Column(db.String, nullable=False)

class Chat_data(db.Model):
    chat_id = db.Column(db.String, primary_key=True, nullable=False, default=str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    integration_id = db.Column(db.String, db.ForeignKey("integration.integration_id"), nullable=False)
    date_time = db.Column(db.String, nullable=False)
    sender_name = db.Column(db.String, nullable=False)
    user_message = db.Column(db.String, nullable=False)
    response = db.Column(db.String, nullable=False)
    configuration = db.Column(db.String, db.ForeignKey("integration.configuration"), nullable=False)