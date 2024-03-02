from datetime import datetime

import bcrypt
from flask import Flask, request, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from models.user import User
from models.meal import Meal, format_datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "daily_diet_api_key"
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:admin123@127.0.0.1:3306/daily-diet"

login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)


@login_manager.user_loader
def load_user(id_user):
    return User.query.get(int(id_user))


# region User routes


@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    name = data.get("name")
    username = data.get("username")
    password = data.get("password")

    if name and username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())

        user = User(name=name, username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Usuário cadastrado com sucesso!"})

    return jsonify({"message": "Dados inválidos."}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            return jsonify({"message": "Autenticação realizada com sucesso!"})

    return jsonify({"message": "Credenciais inválidas"}), 400


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})


@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def read_user(id_user):
    user = User.query.get(id_user)

    if user:
        return jsonify({"name": user.name, "username": user.username})

    return jsonify({"message": "Usuário não encontrado!"}), 404


@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
    data = request.json
    user = User.query.get(id_user)

    if user:  # verify if id_user is the existing user
        if data.get("username") and data.get("password"):
            user.username = data.get("username")
            user.password = bcrypt.hashpw(str.encode(data.get("password")), bcrypt.gensalt())
            db.session.commit()
            if user == current_user.get_id():
                logout_user()
            return jsonify({"message": f"Dados do usuário {id_user} atualizado com sucesso. Por favor realize login "
                                       f"novamente."})
        if data.get("username"):
            user.username = data.get("username")
            db.session.commit()
            if user == current_user.get_id():
                logout_user()
            return jsonify(
                {"message": f"Username atualizado com sucesso para {data.get("username")}. Por favor realize "
                            f"login novamente para validação."})
        if data.get("password"):
            user.password = bcrypt.hashpw(str.encode(data.get("password")), bcrypt.gensalt())
            db.session.commit()
            if user == current_user.get_id():
                logout_user()
            return jsonify({"message": f"Password do usuário {id_user} atualizado com sucesso. Por favor realize "
                                       f"login novamente para validação."})
    return jsonify({"message": "Usuário não encontrado"}), 404


# endregion

# region Meal routes

@app.route("/meal", methods=["POST"])
@login_required
def create_meal():
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date_time = data.get("date_time")
    diet = data.get("diet")

    if name and date_time or diet:
        date_time_formatted = datetime.strptime(date_time, "%d-%m-%Y %H:%M")
        meal = Meal(name=name, description=description, datetime=date_time_formatted, diet=diet,
                    user_id=current_user.get_id())
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": "Refeição cadastrada com sucesso"})

    return jsonify({"message": "Dados inválidos"}), 404


@app.route("/meal/<int:id_meal>", methods=["PUT"])
@login_required
def update_meal(id_meal):
    data = request.json
    name = data.get("name")
    description = data.get("description")
    date_time = data.get("date_time")
    diet = data.get("diet")

    meal_by_user = Meal.query.filter(Meal.user_id.like(current_user.get_id()),
                                     Meal.id_meal.like(id_meal)).first()

    if name or date_time or diet or description:
        if meal_by_user:
            meal_by_user.name = name if name is not None else meal_by_user.name
            meal_by_user.description = description
            meal_by_user.datetime = format_datetime(date_time) if date_time is not None else meal_by_user.datetime
            meal_by_user.diet = diet if diet is not None else meal_by_user.diet
            db.session.commit()
            return jsonify({"message": "Refeição atualizada com sucesso"})
        return jsonify({"message": "Refeição não encontrada para este usuário"}), 404
    return jsonify({"message": "Dados inválidos"}), 404


@app.route("/meal/<int:id_meal>", methods=["DELETE"])
@login_required
def delete_meal(id_meal):
    meal_by_user = Meal.query.filter(Meal.user_id.like(current_user.get_id()),
                                     Meal.id_meal.like(id_meal)).first()
    if meal_by_user:
        db.session.delete(meal_by_user)
        db.session.commit()
        return jsonify({"message": f"Refeição {id_meal} deletada com sucesso!"})
    return jsonify({"message": "Refeição não encontrada para este usuário"})


@app.route("/meals", methods=["GET"])
def read_meals():
    meals_list = []
    meals = Meal.query.filter_by(user_id=current_user.get_id()).all()
    meals_list = [meal.to_dict() for meal in meals]
    if len(meals_list) > 0:
        return jsonify(meals_list)
    return jsonify({"message": "Refeições não encontradas para este usuário"})


@app.route("/meal/<int:id_meal>", methods=["GET"])
def read_meal(id_meal):
    meal = Meal.query.filter(Meal.user_id.like(current_user.get_id()),
                             Meal.id_meal.like(id_meal)).first()
    if meal:
        return jsonify(meal.to_dict())
    return jsonify({"message": "Refeição não encontrada para este usuário"}), 404

# endregion

@app.route("/hello-world", methods=["GET"])
def hello_world():
    return "Hello World"


if __name__ == '__main__':
    app.run(debug=True)
