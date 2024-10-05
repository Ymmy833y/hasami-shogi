"""
このモジュールはFlaskアプリケーションを初期化します。
"""

from logging import StreamHandler, getLogger
from flask import Flask
from .config import Config
from .routes import main_routes

def create_app():
    """
    Flaskアプリケーションを作成し、設定を行います。
    ---
    Returns Flaskアプリのインスタンス
    """
    app = Flask(__name__, template_folder='./templates', static_folder='./static')
    app.config.from_object(Config)

    logger = getLogger(__name__)
    handler = StreamHandler()
    handler.setLevel(app.config['LOG_LEVEL'])
    logger.setLevel(app.config['LOG_LEVEL'])
    logger.addHandler(handler)
    logger.propagate = False

    logger.debug('Flask app initialized with logging')

    app.register_blueprint(main_routes)

    return app
