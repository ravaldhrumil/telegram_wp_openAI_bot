import requests
from src.models.model import *
from src.models.configuration import *
from flask import redirect,url_for
import sqlalchemy
from src.handlers.open_ai import check_thread, generate_response
from src.main.app import app

def verify_tg_bot(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data["ok"]:   
        bot_name = data["result"]["username"]
        return bot_name
    else:
        return False
    
def add_tg_configuration(open_ai_key, assistant_id, bot_token, configuration, user_id, bot_name):
    bot = Telegram_configuration.query.filter_by(bot_token=bot_token).first()

    if bot:
        return False

    else:
        try:
            configuration_id = str(uuid.uuid4())
            new_tg_configuraton = Telegram_configuration(open_ai_key=open_ai_key, 
                                                        assistant_id=assistant_id, 
                                                        bot_token=bot_token,
                                                        configuration=configuration,
                                                        user_id=user_id,
                                                        configuration_id=configuration_id,
                                                        bot_name=bot_name)
            db.session.add(new_tg_configuraton)
            db.session.commit()

        except sqlalchemy.exc.IntegrityError:
            msg = "This bot is already active on another assistant"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg))
        
        except Exception as e:
            msg = "This bot is already active on another assistant"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg))

def send_message_to_telegram(chat_id, response, TELEGRAM_BASE_URL):
    print("send_message")
    data = {
        'chat_id': chat_id,
        'text': response
    }
    response = requests.post(TELEGRAM_BASE_URL + 'sendMessage', json=data)

    return
      
def fetch_tg_configuration_details(configuration_id, chat_id, user_message, date_time, sender_name):
    with app.app_context():
        configuration_data = Telegram_configuration.query.filter_by(configuration_id=configuration_id).first()
    bot_token = configuration_data.bot_token
    open_ai_key = configuration_data.open_ai_key
    user_id = configuration_data.user_id
    assistant_id = configuration_data.assistant_id
    configuration_id = configuration_data.configuration_id
    configuration = configuration_data.configuration
    


    TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{bot_token}/"

    thread_id = check_thread(chat_id=chat_id,
                            user_id=user_id,
                            open_ai_key=open_ai_key)
    
    response = generate_response(user_message=user_message,
                                thread_id=thread_id,
                                assistant_id=assistant_id)

    
    send_message_to_telegram(chat_id=chat_id,
                response=response, 
                TELEGRAM_BASE_URL=TELEGRAM_BASE_URL)
    
    msg_id = str(uuid.uuid4())
    with app.app_context():
        new_chat = Chat_data(chat_id=chat_id,
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