from flask import Flask
from logging import StreamHandler, getLogger
from .config import Config

def create_app():
    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    app.config.from_object(Config)

    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setLevel(app.config['LOG_LEVEL'])
    logger.setLevel(app.config['LOG_LEVEL'])
    logger.addHandler(handler)
    logger.propagate = False

    logger.debug('Flask app initialized with logging')

    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
