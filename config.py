import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    """
        Конфигурационный класс для настройки параметров приложения.

        Атрибуты:
        SQLALCHEMY_DATABASE_URI : str
            URI для подключения к базе данных (используется SQLite).
        SQLALCHEMY_TRACK_MODIFICATIONS : bool
            Если True, Flask-SQLAlchemy будет отслеживать изменения объектов
            и отправлять сигнал.
        UPLOAD_FOLDER : str
            Путь к директории для загрузки изображений.
        SECRET_KEY : str
            Секретный ключ для обеспечения безопасности сессий
        LOGIN_VIEW : str
            Имя маршрута для перенаправления пользователей на страницу
            входа при попытке доступа к защищенным страницам.
        LOGIN_MESSAGE : str
            Сообщение, отображаемое пользователям при необходимости
            пройти аутентификацию.
        LOGIN_MESSAGE_CATEGORY : str
            Категория сообщения для отображения (например, 'info', 'warning').
        """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'cups.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(BASE_DIR / 'static' / 'images')
    SECRET_KEY = 'ghoeklxWEFPROLJDSV39klekf'
    LOGIN_VIEW = 'login'
    LOGIN_MESSAGE = 'Пожалуйста, войдите для доступа к этой странице.'
    LOGIN_MESSAGE_CATEGORY = 'info'

    @staticmethod
    def init_app(app):
        """Инициализирует приложение и создает необходимую директорию
            для загрузки изображений, если она не существует."""
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)