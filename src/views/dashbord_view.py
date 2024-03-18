from flask import redirect, render_template, Blueprint, request, url_for
from src.views.auth_view import check_for_token
from src.models.model import *
import openai
import requests
from twilio.rest import Client
from src.models.configuration import *
from src.handlers.open_ai import fetch_assistants
from src.handlers.telegram import verify_tg_bot, add_tg_configuration
from src.handlers.whatsapp import add_wp_configuration

dashboard_view = Blueprint("dashboard_view",__name__)

@dashboard_view.route("/dashboard")
@dashboard_view.route("/dashboard/<msg>")
@check_for_token
def dashboard(token_data=None, msg=None):
    user_id = token_data["user_id"]
    old_tg_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
    old_wp_integrations = Whatsapp_configuration.query.filter_by(user_id=user_id).all()
    return render_template("dashboard.html", old_tg_integrations=old_tg_integrations, old_wp_integrations=old_wp_integrations , msg=msg)

@dashboard_view.route("/new_integration", methods=["GET","POST"])
@check_for_token
def new_integration(token_data=None):
    user_id = token_data["user_id"]

    if request.method == "GET":
        open_ai_key = request.args.get('open_ai_key')
        configuration = request.args.get("configuration")

        try:
            my_assistants = fetch_assistants(open_ai_key=open_ai_key)

            if configuration == "telegram":
                return render_template("telegram_integration.html", open_ai_key=open_ai_key, assistants=my_assistants.data)
            
            if configuration == "whatsapp":
                return render_template("whatsapp_integraion.html", open_ai_key=open_ai_key, assistants=my_assistants.data)
            
        except openai.AuthenticationError:
            msg = "Wrong API key"
            bgcolor = "red"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
        
        except Exception as e:
            msg = e
            bgcolor = "red"
            return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
        
    elif request.method == "POST":
        configuration = request.form["configuration"]
        open_ai_key = request.form["open_ai_key"]
        assistant_id = request.form["assistant_id"]

        if configuration == "telegram":
            bot_token = request.form["bot_token"]
            bot_name = verify_tg_bot(bot_token)

            if bot_name:
                configuration_id = add_tg_configuration(open_ai_key=open_ai_key, 
                                    assistant_id=assistant_id, 
                                    bot_token=bot_token,
                                    configuration=configuration,
                                    user_id=user_id,
                                    bot_name=bot_name)

                if configuration_id == False:
                    msg = "This bot is already active on another assistant"
                    bgcolor = "red"
                    return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
                
                else:
                    msg = "Configuration added successfully"
                    bgcolor = "green"
                    return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
            else:
                msg = "Wrong bot token"
                bgcolor = "red"
                return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
            
        if configuration == "whatsapp":
            twilio_sid = request.form["twilio_sid"]
            twilio_auth = request.form["twilio_auth"]
            phone_number = request.form["phone_number"]

            try:
                client = Client(twilio_sid, twilio_auth)
                account = client.api.accounts(twilio_sid).fetch()

                configuration_id = add_wp_configuration(open_ai_key=open_ai_key, 
                                    assistant_id=assistant_id,
                                    configuration=configuration,
                                    user_id=user_id,
                                    phone_number=phone_number,
                                    twilio_sid=twilio_sid,
                                    twilio_auth=twilio_auth)

                if configuration_id == False:
                    msg = "This bot is already active on another assistant"
                    bgcolor = "red"
                    return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
                
                else:
                    msg = "Configuration added successfully"
                    bgcolor = "green"
                    return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))

            except Exception as e:
                msg = "Wrong twilio info"
                bgcolor = "red"
                return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))

@dashboard_view.route("/activate_tg_webhook/<configuration_id>/<bot_token>")
@check_for_token
def activate_tg_webhook(configuration_id, bot_token, token_data=None):
    base_url = request.headers['X-Forwarded-Proto'] + "://" + request.headers['X-Forwarded-Host']
    WEBHOOK_URL = f'{base_url}/telegram/{configuration_id}'
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    payload = {'url': WEBHOOK_URL}
    response = requests.post(url, json=payload)

    if response.ok:
        existing_configuration = Telegram_configuration.query.filter_by(configuration_id=configuration_id).first()
        existing_configuration.status = True
        db.session.commit()
        msg = "Bot setup successfully"
        bgcolor = "green"
        return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
    
    else:
        msg = "There was an error" 
        bgcolor = "red"
        return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
    
@dashboard_view.route("/deactivate_tg_webhook/<configuration_id>/<bot_token>")
@check_for_token
def deactivate_tg_webhook(configuration_id, bot_token, token_data=None):
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    payload = {'url': ''}
    response = requests.post(url, json=payload)
    if response.ok:
        existing_configuration = Telegram_configuration.query.filter_by(configuration_id=configuration_id).first()
        existing_configuration.status = False
        db.session.commit()
        msg = "Webhook deactivated successfully!"
        bgcolor = "green"
        return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))
    else:
        msg = f"Failed to deactivate webhook. Status code: {response.status_code}, Response: {response.text}" 
        bgcolor = "red"
        return redirect(url_for(f"dashboard_view.dashboard", msg=msg, bgcolor=bgcolor))