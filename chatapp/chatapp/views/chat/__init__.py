from flask import Blueprint

bp = Blueprint(
    'chat', 
    __name__,
    url_prefix='/chat',
)

from chatapp.views.chat import handlers