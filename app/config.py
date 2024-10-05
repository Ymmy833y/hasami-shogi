"""
このモジュールはFlaskアプリケーションの設定を定義します。
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# pylint: disable=too-few-public-methods
class Config:
    """
    Flaskアプリケーション設定用のクラス
    環境変数からシークレットキーとログレベルを読み込みます。
    """
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your_default_secret_key'

    LOG_LEVEL = os.getenv('LOG_LEVEL') or logging.DEBUG
