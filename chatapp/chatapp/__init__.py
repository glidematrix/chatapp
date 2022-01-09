import os
from flask import Flask, request


def create_app(test_config=None):
    """Application Factory
    """

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object('instance.config.Config')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from chatapp.views import chat
    app.register_blueprint(chat.bp)

    from chatapp.views import api
    app.register_blueprint(api.bp)

    return app