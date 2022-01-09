from flask import render_template
from chatapp.views.api import bp

from chatapp.websocket import WebSocket


@bp.route('/')
def test():

    res = {
        'status': 'OK'
    }

    WebSocket.write_to_clients(msg="this is a test")

    return res