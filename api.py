from flask import url_for, request
from flask_restful import Resource, Api
from models import Cup
from extensions import db


def init_api(app):
    api = Api(app)

    class CupList(Resource):
        def get(self):
            # Получаем параметры фильтрации из URL
            category = request.args.get('category')
            color = request.args.get('color')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)

            query = Cup.query

            # Применяем фильтры если они есть
            if category:
                query = query.filter_by(category=category)
            if color:
                query = query.filter_by(color=color)
            if min_price is not None:
                query = query.filter(Cup.price >= min_price)
            if max_price is not None:
                query = query.filter(Cup.price <= max_price)

            # Преобразуем результат в JSON
            cups = query.all()
            return {
                'cups': [{
                    'id': cup.id,
                    'title': cup.title,
                    'description': cup.description,
                    'price': float(cup.price),  # Decimal -> float для JSON
                    'image': url_for('static', filename=f'images/{cup.image}', _external=True),
                    'category': cup.category,
                    'color': cup.color
                } for cup in cups]
            }

    class CupDetail(Resource):
        def get(self, cup_id):
            cup = Cup.query.get_or_404(cup_id)
            return {
                'id': cup.id,
                'title': cup.title,
                'description': cup.description,
                'price': float(cup.price),
                'image': url_for('static', filename=f'images/{cup.image}', _external=True),
                'category': cup.category,
                'color': cup.color
            }

    # Регистрируем только GET-эндпоинты
    api.add_resource(CupList, '/api/cups')
    api.add_resource(CupDetail, '/api/cups/<int:cup_id>')