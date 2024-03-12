from flask import Blueprint, request
from src.models.model import *
import threading
import datetime
import pytz
from src.handlers.telegram import fetch_tg_configuration_details
from src.handlers.whatsapp import handle_incoming_wp_message


message_view = Blueprint("message_view", __name__)

@message_view.route("/telegram/<configuration_id>",methods=["POST"])
def handle_telegram_configuration_id(configuration_id):
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
        thread1 = threading.Thread(target= fetch_tg_configuration_details, args=[configuration_id, chat_id, user_message, date_time, sender_name])
        thread1.start()
        return "", 200
    
    else:
        return "",404

@message_view.route("/whatsapp/<configuration_id>",methods=["POST"])
def handle_whatsapp_configuration(configuration_id):
    user_message = request.form['Body']
    sender_number = request.form['From']
    sender_name = request.form["ProfileName"]
    
    thread1 = threading.Thread(target=handle_incoming_wp_message, args=[user_message, sender_number, configuration_id, sender_name])
    thread1.start()
    return '', 200