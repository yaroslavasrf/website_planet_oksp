from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from models import User, Cup
from forms import RegistrationForm, LoginForm
from extensions import db, login_manager
from config import Config
from api import init_api

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
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
    logout_user()
    return redirect(url_for('index'))


@app.route('/add_cup', methods=['GET', 'POST'])
@login_required
def add_cup():
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


if __name__ == '__main__':
    app.run(debug=True)