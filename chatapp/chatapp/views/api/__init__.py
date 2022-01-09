from flask import Blueprint

bp = Blueprint(
    'api', 
    __name__,
    url_prefix='/api',
)

from chatapp.views.api import handlers