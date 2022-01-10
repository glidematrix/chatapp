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