from flask import Flask, render_template, request
from config import Config
from extensions import db
from models import User, Cup

app = Flask(__name__)
app.config.from_object(Config)


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


if __name__ == '__main__':
    app.run(debug=True)
