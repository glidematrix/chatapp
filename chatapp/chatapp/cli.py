import os
from chatapp import create_app, websocket
import argparse
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, FallbackHandler
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

app = create_app()

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--port", default=8080, help="Default Port")
args = parser.parse_args()


def run():

    # app.run(
    #     host="0.0.0.0",
    #     port=args.port,
    #     debug=True
    # )

    logger.info(f'App running on port: {args.port}')

    ioloop = IOLoop.current()

    container = WSGIContainer(app)

    settings = {
        'autoreload': True,
        'debug':True,
        'websocket_ping_interval': 5,
    }

    container = WSGIContainer(app)
    tornado_app = Application([
        (r'/websocket', websocket.WebSocket),
        (r'.*', FallbackHandler, dict(fallback=container)),
    ], **settings)
    server = HTTPServer(tornado_app)
    server.listen(args.port)
    ioloop.start()