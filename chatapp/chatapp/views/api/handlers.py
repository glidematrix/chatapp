import os
from flask import request
from chatapp.views.api import bp
from chatapp.websocket import WebSocket
# from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

@bp.route('/test')
def test():

    res = {
        'status': 'OK'
    }

    WebSocket.write_to_clients(message="this is a test")

    return res


@bp.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():

    res = {
        'status': 'ok'
    }
    
    data = request.form

    # logger.info(data)

    message = data.get('Body')
    sender = data.get('From')

    WebSocket.write_to_agents(
        message,
        sender=sender
    )

    return res


@bp.route('/webhook/facebook', methods=['GET','POST'])
def webhook_facebook():

    res = {
        'status': 'ok'
    }


    if request.method == 'GET':
        if (request.args.get('hub.verify_token', '') == os.getenv('FB_VERIFY_TOKEN')):
            print("Verified")
            return request.args.get('hub.challenge', '')
        else:
            print("Wrong token")
            return "Error, wrong validation token"

    if request.method == 'POST':
        data = request.get_json()

        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):

                        # recipient_id = messaging_event["recipient"]["id"]  
                        sender_id = messaging_event["sender"]["id"]
                        message = messaging_event["message"]["text"]  

                        WebSocket.write_to_agents(
                            message,
                            sender=sender_id,
                            channel='FB'
                        )

    return res

