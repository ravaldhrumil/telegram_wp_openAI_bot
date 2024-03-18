from src.models.model import *
from src.models.configuration import *
import sqlalchemy
from flask import redirect, url_for
from src.main.app import app
from twilio.rest import Client
from src.handlers.open_ai import check_thread, generate_response

def add_wp_configuration(open_ai_key, assistant_id, configuration, user_id, phone_number, twilio_auth, twilio_sid):
    number = Whatsapp_configuration.query.filter_by(phone_number=phone_number).first()

    if number:
        return False

    else:
        try:
            configuration_id = str(uuid.uuid4())
            new_wp_configuraton = Whatsapp_configuration(open_ai_key=open_ai_key, 
                                                        assistant_id=assistant_id,
                                                        configuration=configuration,
                                                        user_id=user_id,
                                                        configuration_id=configuration_id,
                                                        twilio_auth=twilio_auth,
                                                        twilio_sid=twilio_sid,
                                                        phone_number=phone_number)
            db.session.add(new_wp_configuraton)
            db.session.commit()

        except sqlalchemy.exc.IntegrityError:
            msg = "This bot is already active on another assistant"
            bgcolor = "red"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
        
        except Exception as e:
            msg = e
            bgcolor = "red"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))

    return configuration_id

def send_message_to_whatsapp(sender_number, message, user_phone_number, twilio_sid, twilio_auth):
    client = Client(twilio_sid, twilio_auth)
    client.messages.create(
        from_=f"whatsapp:{user_phone_number}",
        body=message,
        to=sender_number
    )

    return

def handle_incoming_wp_message(user_message, sender_number, configuration_id, sender_name):
    with app.app_context():
        configuration_data = Whatsapp_configuration.query.filter_by(configuration_id=configuration_id).first()
    user_phone_number = configuration_data.phone_number
    twilio_sid = configuration_data.twilio_sid
    twilio_auth = configuration_data.twilio_auth
    open_ai_key = configuration_data.open_ai_key
    user_id = configuration_data.user_id
    assistant_id = configuration_data.assistant_id
    configuration = configuration_data.configuration
    
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    thread_id = check_thread(chat_id=sender_number,
                            user_id=user_id,
                            open_ai_key=open_ai_key)
    
    response = generate_response(user_message=user_message,
                                thread_id=thread_id,
                                assistant_id=assistant_id)
    
    send_message_to_whatsapp(sender_number, response, user_phone_number, twilio_sid, twilio_auth)

    msg_id = str(uuid.uuid4())
    with app.app_context():
        new_chat = Chat_data(chat_id=sender_number,
                             user_id=user_id,
                             configuration_id=configuration_id,
                             date_time=date_time,
                             sender_name=sender_name,
                             user_message=user_message,
                             response=response,
                             configuration=configuration,
                             msg_id=msg_id)
        db.session.add(new_chat)
        db.session.commit()