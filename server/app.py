#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return make_response({"restaurants": [restaurant.to_dict() for restaurant in restaurants]}, 200)

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    if request.method == "GET":
        return make_response({"restaurant": restaurant.to_dict(rules = ("-restaurant_pizzas", "-restaurant_pizzas.pizza"))}, 200)
    
    elif request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return make_response({"pizzas": [pizza.to_dict(rules = ("-restaurant_pizzas",)) for pizza in pizzas]}, 200)


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]

        if not (1 <= price <= 30):
            raise ValueError("validation errors")

        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return make_response(restaurant_pizza.to_dict(), 201)

    except Exception:
        return make_response({"errors": ["validation errors"]}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
