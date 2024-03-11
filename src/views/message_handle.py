from flask import Blueprint, request
from src.models.model import *
import requests
import openai
import threading
from src.main.app import app
import datetime
import pytz


message_view = Blueprint("message_view", __name__)

@message_view.route("/telegram/<configuration_id>",methods=["POST"])
def handle_telegram_configuration_id(configuration_id):
    print("handle_telegram_configuration_id")
    update = request.json
    message = update['message']
    chat_id = message['chat']['id']
    user_message = message.get('text', '')
    sender_name = message['from']['first_name'] + " " + message['from']['last_name']
    unix_timestamp = message['date']
 
    utc_date_time = datetime.datetime.utcfromtimestamp(unix_timestamp)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_date_time = utc_date_time.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
    date_time = ist_date_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')


    if user_message:
        thread1 = threading.Thread(target= fetch_configuration_details, args=[configuration_id, chat_id, user_message, date_time, sender_name])
        thread1.start()
        return "", 200
    
    else:
        return "",404

def fetch_configuration_details(configuration_id, chat_id, user_message, date_time, sender_name):
    print("fetch_configuration_details")
    with app.app_context():
        configuration_data = Telegram_configuration.query.filter_by(configuration_id=configuration_id).first()
    bot_token = configuration_data.bot_token
    open_ai_key = configuration_data.open_ai_key
    user_id = configuration_data.user_id
    assistant_id = configuration_data.assistant_id
    integration_id = configuration_data.integration_id
    configuration = configuration_data.configuration
    


    TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{bot_token}/"

    thread_id = check_thread(chat_id=chat_id,
                            user_id=user_id,
                            open_ai_key=open_ai_key)
    
    response = generate_response(user_message=user_message,
                                thread_id=thread_id,
                                assistant_id=assistant_id)

    print(f"\n\n\n\nUSER MESSAGE: {user_message}")
    print(f"RESPONSE: {response}\n\n\n\n")
    
    send_message(chat_id=chat_id,
                response=response, 
                TELEGRAM_BASE_URL=TELEGRAM_BASE_URL)
    
    with app.app_context():
        new_chat = Chat_data(chat_id=chat_id,
                             user_id=user_id,
                             integration_id=integration_id,
                             date_time=date_time,
                             sender_name=sender_name,
                             user_message=user_message,
                             response=response,
                             configuration=configuration)
        db.session.add(new_chat)
        db.session.commit()
        

def check_thread(chat_id, user_id, open_ai_key):
    print("check_thread")
    openai.api_key = open_ai_key
    try:
        thread_id = get_thread_id_from_recipient_id(chat_id=chat_id,
                                                    user_id=user_id)
        
        if thread_id:
            try:
                thread = openai.beta.threads.retrieve(
                        thread_id=thread_id
                    )

            except openai.NotFoundError:
                thread = openai.beta.threads.create()
                thread_id=thread.id
                update_thread_id_from_recipient_id(chat_id=chat_id, 
                                                thread_id=thread_id, 
                                                user_id=user_id)
        else:
            thread = openai.beta.threads.create()
            thread_id=thread.id
            update_thread_id_from_recipient_id(chat_id=chat_id, 
                                               thread_id=thread_id, 
                                               user_id=user_id)

    except Exception as e:
        return e

    return thread_id

def get_thread_id_from_recipient_id(chat_id, user_id):
    print("get_thread_id_from_recipient_id")
    with app.app_context():
        thread_id = Openai_thread.query.filter_by(user_id=user_id, chat_id=chat_id).one_or_none()
    return thread_id

def update_thread_id_from_recipient_id(chat_id, thread_id, user_id):
    print("update_thread_id_from_recipient_id")
    print("THREAD: ",thread_id)
    thread_id = thread_id[len("thread_"):]
    with app.app_context():
        thread = Openai_thread.query.filter_by(user_id=user_id, chat_id=chat_id).first()
        if thread:
            thread.thread_id = thread_id
            db.session.commit()
        else:
            new_thread = Openai_thread(user_id=user_id, thread_id=thread_id, chat_id=chat_id, configuration="telegram")
            db.session.add(new_thread)
            db.session.commit()
    return

def generate_response(user_message, thread_id, assistant_id):
    print("generate_response")
    print(f"USER MESSAGE: {user_message}")
    print(f"ASSISTANT ID: {assistant_id}")
    _ = openai.beta.threads.messages.create(
        thread_id=thread_id,
        content=user_message,
        role='user'
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    print(run.id)
    flag = True
    while flag:
        retrieved_run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        print("Status: ",retrieved_run.status)
        if retrieved_run.status == 'completed':
            flag = False
            
    retrieved_messages = openai.beta.threads.messages.list(
        thread_id=thread_id
    )
    print(retrieved_messages.data[0])
    message_text = retrieved_messages.data[0].content[0].text.value

    return message_text

def send_message(chat_id, response, TELEGRAM_BASE_URL):
    print("send_message")
    data = {
        'chat_id': chat_id,
        'text': response
    }
    response = requests.post(TELEGRAM_BASE_URL + 'sendMessage', json=data)

    return
