from openai import OpenAI
import openai
from src.models.model import *
from src.main.app import app

def fetch_assistants(open_ai_key):
        client = OpenAI(api_key = open_ai_key)

        my_assistants = client.beta.assistants.list(
            order="desc",
            limit="20",
        )

        return my_assistants

def generate_response(user_message, thread_id, assistant_id):
    _ = openai.beta.threads.messages.create(
        thread_id=thread_id,
        content=user_message,
        role='user'
    )
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    flag = True
    while flag:
        retrieved_run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if retrieved_run.status == 'completed':
            flag = False
            
    retrieved_messages = openai.beta.threads.messages.list(
        thread_id=thread_id
    )
    message_text = retrieved_messages.data[0].content[0].text.value

    return message_text

def check_thread(chat_id, user_id, open_ai_key):
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
    with app.app_context():
        thread_id = Openai_thread.query.filter_by(user_id=user_id, chat_id=chat_id).one_or_none()
    return thread_id

def update_thread_id_from_recipient_id(chat_id, thread_id, user_id):
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