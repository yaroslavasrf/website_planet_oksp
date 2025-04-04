import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'cups.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'images')
    SECRET_KEY = 'your-secret-key-here'
    LOGIN_VIEW = 'login'
    LOGIN_MESSAGE = 'Пожалуйста, войдите для доступа к этой странице.'
    LOGIN_MESSAGE_CATEGORY = 'info'

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)