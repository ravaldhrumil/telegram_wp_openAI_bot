from flask import redirect, render_template, Blueprint, request, url_for
import sqlalchemy
from src.views.auth_view import check_for_token
from src.models.model import *
from openai import OpenAI
import openai
import requests

dashboard_view = Blueprint("dashboard_view",__name__)


@dashboard_view.route("/dashboard")
@check_for_token
def dashboard(token_data=None):
    user_id = token_data["user_id"]
    old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
    return render_template("dashboard.html", old_integrations=old_integrations)

def verify_tg_bot(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data["ok"]:   
        bot_name = data["result"]["username"]
        return bot_name
    else:
        return False

def fetch_assistants(open_ai_key):
        client = OpenAI(api_key = open_ai_key)

        my_assistants = client.beta.assistants.list(
            order="desc",
            limit="20",
        )

        return my_assistants


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
            old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
            msg = "This bot is already active on another assistant"
            return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
        
        except Exception as e:
            old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
            msg = "This bot is already active on another assistant"
            return render_template("dashboard.html", old_integrations=old_integrations, msg=e)

    return configuration_id

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
            
        except openai.AuthenticationError:
            old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
            msg = "Wrong API key"
            return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
        
        except Exception as e:
            old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
            return render_template("dashboard.html", old_integrations=old_integrations, msg=e)
        
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
                    old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
                    msg = "This bot is already active on another assistant"
                    return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
                
                else:
                    old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
                    msg = "Configuration added successfully"
                    return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
            else:
                old_integrations = Telegram_configuration.query.filter_by(user_id=user_id).all()
                msg = "Wrong bot token"
                return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)

@dashboard_view.route("/activation/<configuration_id>/<bot_token>")
def setting_webhook(configuration_id, bot_token):
    base_url = request.headers['X-Forwarded-Proto'] + "://" + request.headers['X-Forwarded-Host']
    WEBHOOK_URL = f'{base_url}/telegram/{configuration_id}'
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    payload = {'url': WEBHOOK_URL}
    response = requests.post(url, json=payload)


    if response.ok:
        existing_configuration = Telegram_configuration.query.filter_by(configuration_id=configuration_id).first()
        existing_configuration.status = True
        db.session.commit()

        return redirect(url_for("dashboard_view.dashboard"))
    
    else:
        msg = "There was an error" 
        return render_template("dashboard.html", msg=msg)
