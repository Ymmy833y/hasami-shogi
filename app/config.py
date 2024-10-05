from dotenv import load_dotenv
import os
import logging

load_dotenv()

class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your_default_secret_key'

    LOG_LEVEL = os.getenv('LOG_LEVEL') or logging.DEBUG
