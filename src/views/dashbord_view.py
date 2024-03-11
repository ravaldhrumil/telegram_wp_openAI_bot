from flask import render_template, Blueprint, request
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
    old_integrations = Integration.query.filter_by(user_id=user_id).all()
    return render_template("dashboard.html", old_integrations=old_integrations)

def verify_tg_bot(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    response = requests.get(url)
    data = response.json()
    bot_name = data["result"]["username"]
    if response.status_code == 200 and data["ok"]:
        return True
    else:
        return False

def fetch_assistants(open_ai_key):
        client = OpenAI(api_key = open_ai_key)

        my_assistants = client.beta.assistants.list(
            order="desc",
            limit="20",
        )

        return my_assistants

def add_integration(configuration, user_id):
        try:
            integration_id = str(uuid.uuid4())
            new_integration = Integration(integration_id=integration_id, 
                                        configuration=configuration, 
                                        user_id=user_id)
            db.session.add(new_integration)
            db.session.commit()

        except Exception as e:
            old_integrations = Integration.query.filter_by(user_id=user_id).all()
            return render_template("dashboard.html", old_integrations=old_integrations, msg=e)
        

        return integration_id

def add_tg_configuration(open_ai_key, assistant_id, bot_token, configuration, integration_id, user_id):
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
                                                        integration_id=integration_id,
                                                        user_id=user_id,
                                                        configuration_id=configuration_id)
            db.session.add(new_tg_configuraton)
            db.session.commit()

        except sqlalchemy.exc.IntegrityError:
            old_integrations = Integration.query.filter_by(user_id=user_id).all()
            msg = "This bot is already active on another assistant"
            return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
        
        except Exception as e:
            old_integrations = Integration.query.filter_by(user_id=user_id).all()
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
            old_integrations = Integration.query.filter_by(user_id=user_id).all()
            msg = "Wrong API key"
            return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
        
        except Exception as e:
            old_integrations = Integration.query.filter_by(user_id=user_id).all()
            return render_template("dashboard.html", old_integrations=old_integrations, msg=e)
        
    elif request.method == "POST":
        configuration = request.form["configuration"]
        open_ai_key = request.form["open_ai_key"]
        assistant_id = request.form["assistant_id"]

        if configuration == "telegram":
            bot_token = request.form["bot_token"]

            bot_name = verify_tg_bot(bot_token)

            if bot_name:
                integration_id = add_integration(configuration=configuration,
                                         user_id=user_id)
                
                
                configuration_id = add_tg_configuration(open_ai_key=open_ai_key, 
                                    assistant_id=assistant_id, 
                                    bot_token=bot_token,
                                    configuration=configuration,
                                    integration_id=integration_id,
                                    user_id=user_id)

                if configuration_id == False:
                    integration_to_delete = Integration.query.filter_by(integration_id=integration_id).first()
                    db.session.delete(integration_to_delete)
                    db.session.commit()
                    
                    old_integrations = Integration.query.filter_by(user_id=user_id).all()
                    msg = "This bot is already active on another assistant"
                    return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)
                
                else:
                    response = setting_webhook(configuration_id=configuration_id,
                                            bot_token=bot_token)

                    if response.ok:
                        msg = "Bot has been set successfully" 
                        return render_template("dashboard.html", msg=msg, color="green")
                    else:
                        msg = "There was an error" 
                        return render_template("dashboard.html", msg=msg)
            else:
                old_integrations = Integration.query.filter_by(user_id=user_id).all()
                msg = "Wrong bot token"
                return render_template("dashboard.html", old_integrations=old_integrations, msg=msg)

def setting_webhook(configuration_id, bot_token):
    base_url = request.headers['X-Forwarded-Proto'] + "://" + request.headers['X-Forwarded-Host']
    WEBHOOK_URL = f'{base_url}/telegram/{configuration_id}'
    url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
    payload = {'url': WEBHOOK_URL}
    response = requests.post(url, json=payload)

    return response