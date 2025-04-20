from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from models import User, Cup
from forms import RegistrationForm, LoginForm
from extensions import db, login_manager
from config import Config
from api import init_api

# Создание экземпляра класса Flask
app = Flask(__name__)
# Загрузка конфигурации из класса 'Config'
app.config.from_object(Config)

# Инициализация базы данных и менеджера аутентификации
db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
       Эта функция используется Flask-Login для получения объекта пользователя по его идентификатору.
       Принимает `user_id`, преобразует его в целое число и возвращает объект пользователя из базы данных.

       Returns:
       User or None
           Объект пользователя из базы данных, если пользователь с таким идентификатором существует, иначе None.
       """
    return User.query.get(int(user_id))


# Создание таблиц в базе данных (пустой бд) с помощью SQLAlchemy
with app.app_context():
    db.create_all()


@app.route('/')
@app.route('/index')
def index():
    """
        Главная страница приложения. Обрабатывает запросы с фильтрацией по категориям,
        цветам и ценовому диапазону для отображения списка чашек. Рассчитывает и возвращает
        отфильтрованный список чашек на основе параметров запроса, включая категорию, цвет,
        минимальную и максимальную цену.

        Parameters:
        category : str, optional
            Фильтр по категории чашки. Если передан, применяется к запросу.
        color : str, optional
            Фильтр по цвету чашки. Если передан, применяется к запросу.
        min_price : str, optional
            Минимальная цена чашки. Если передан, применяется к запросу.
        max_price : str, optional
            Максимальная цена чашки. Если передан, применяется к запросу.

        Returns:
            HTML-шаблон 'index.html' с переданными данными:
                - cups : list of Cup
                    Отфильтрованный список чашек.
                - categories : list of Category
                    Уникальные категории чашек.
                - colors : list of Color
                    Уникальные цвета чашек.
                - current_filters : dict
                    Текущие фильтры, используемые для отображения.
        """
    category = request.args.get('category')
    color = request.args.get('color')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = Cup.query

    if category:
        query = query.filter_by(category=category)
    if color:
        query = query.filter_by(color=color)
    if min_price:
        query = query.filter(Cup.price >= float(min_price))
    if max_price:
        query = query.filter(Cup.price <= float(max_price))

    cups = query.all()

    categories = db.session.query(Cup.category.distinct()).all()
    colors = db.session.query(Cup.color.distinct()).all()

    return render_template('index.html',
                           cups=cups,
                           categories=categories,
                           colors=colors,
                           current_filters={
                               'category': category,
                               'color': color,
                               'min_price': min_price,
                               'max_price': max_price
                           })


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
        Страница регистрации нового пользователя. Обрабатывает запросы на создание
        нового пользователя через форму регистрации. Если пользователь уже
        аутентифицирован, происходит перенаправление на главную страницу. При успешной валидации
        формы регистрации, новый пользователь создается и добавляется в базу данных.

        GET: Отображение формы регистрации.
        POST: Обработка данных формы и создание нового пользователя.

        Returns:
            HTML-шаблон 'register.html' с формой регистрации, если это GET-запрос,
            или выполняет перенаправление в случае успешной регистрации или
            если пользователь уже аутентифицирован.

        Redirect:
            Перенаправление на страницу входа (login) после успешной регистрации,
            или на главную страницу (index), если пользователь уже аутентифицирован.
        """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
        Страница входа для пользователей. Обрабатывает запросы на вход в систему.
        Если пользователь уже аутентифицирован, происходит перенаправление на
        главную страницу. При успешной аутентификации пользователя он перенаправляется на страницу, указанную в
        параметре `next`, или на главную страницу по умолчанию. Если введенные
        имя пользователя или пароль неверны, отображается сообщение об ошибке.

        Returns:
            HTML-шаблон 'login.html' с формой входа, если это GET-запрос,
            или выполняет перенаправление на следующую страницу после успешного
            входа.

        Redirect:
            Перенаправление на следующую страницу после успешного входа или на
            главную страницу (index) по умолчанию, если пользователь не указан.
            Если аутентификация не удалась, отображается сообщение об ошибке.
        """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Неверное имя пользователя или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """
    При выходе пользователя происходит завершение его сессии, и
    осуществляется перенаправление на главную страницу.

    Redirect:
        Перенаправляет на главную страницу сайта после успешного выхода
        пользователя.
    """

    logout_user()
    return redirect(url_for('index'))


@app.route('/add_cup', methods=['GET', 'POST'])
@login_required
def add_cup():
    """
       Обрабатывает запросы на добавление новой чашки.

       Если метод запроса - POST, извлекает данные из формы, загружает
       изображение и создает новый объект Cup, который сохраняется в базе данных.
       Если метод запроса - GET, отображает страницу с формой для добавления чашки.

       Redirect:
           Перенаправляет на главную страницу после успешного добавления чашки
           (для метода POST).
       render_template
           Отображает страницу 'add_cup.html' (для метода GET).

       Raises:
       ValueError
           Если не удается преобразовать цену в тип float.
       FileNotFoundError
           Если не удается сохранить изображение в указанной папке.

       Notes:
       Для корректной работы функции требуется, чтобы пользователь был
       авторизован (декоратор @login_required). Формируемая форма должна
       содержать поля 'title', 'description', 'price', 'category', 'color' и
       'image'.
       """
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        color = request.form['color']

        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_cup = Cup(
            title=title,
            description=description,
            price=price,
            image=filename,
            category=category,
            color=color
        )

        db.session.add(new_cup)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_cup.html')

# Запускает сервер Flask в режиме отладки
if __name__ == '__main__':
    app.run(debug=True)