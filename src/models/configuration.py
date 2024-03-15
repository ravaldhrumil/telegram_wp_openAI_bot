from src.models.model import *

class Telegram_configuration(db.Model):
    configuration_id = db.Column(db.String(500), primary_key=True, nullable=False, default=str(uuid.uuid4()))
    open_ai_key = db.Column(db.String(500), nullable=False)
    assistant_id = db.Column(db.String(500), nullable=False)
    bot_token = db.Column(db.String(500), nullable=False, unique=True)
    configuration = db.Column(db.String(500),  nullable=False)
    user_id = db.Column(db.String(500), db.ForeignKey("user.id"), nullable=False)
    bot_name = db.Column(db.String(500), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    

    def __repr__(self):
        return f"configuration={self.configuration})"
    
class Whatsapp_configuration(db.Model):
    configuration_id = db.Column(db.String(500), primary_key=True, nullable=False, default=str(uuid.uuid4()))
    open_ai_key = db.Column(db.String(500), nullable=False)
    assistant_id = db.Column(db.String(500), nullable=False)
    configuration = db.Column(db.String(500),  nullable=False)
    twilio_sid = db.Column(db.String(500),  nullable=False)
    twilio_auth = db.Column(db.String(500),  nullable=False)
    phone_number = db.Column(db.String(500),  nullable=False)
    user_id = db.Column(db.String(500), db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=False)
    

    def __repr__(self):
        return f"configuration={self.configuration})"