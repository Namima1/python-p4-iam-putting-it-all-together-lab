from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Recipe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    try:
        user = User(
            username=data['username'],
            image_url=data.get('image_url'),
            bio=data.get('bio'),
        )
        user.password = data['password']
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        return jsonify({
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }), 201
    except Exception as e:
        return {"error": str(e)}, 422

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.authenticate(data['password']):
        session['user_id'] = user.id
        return jsonify({
            "id": user.id,
            "username": user.username,
            "image_url": user.image_url,
            "bio": user.bio
        }), 200
    return {"error": "Invalid credentials"}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    if 'user_id' not in session or not session['user_id']:
        return {"error": "Unauthorized"}, 401
    session.pop('user_id', None)
    return '', 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return {"error": "Unauthorized"}, 401
    user = db.session.get(User, user_id)
    if not user:
        return {"error": "User not found"}, 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio
    }), 200

@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    if 'user_id' not in session or not session['user_id']:
        return {"error": "Unauthorized"}, 401

    if request.method == 'GET':
        recipes = Recipe.query.all()
        return jsonify([{
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": recipe.user.id,
                "username": recipe.user.username
            }
        } for recipe in recipes]), 200

    if request.method == 'POST':
        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=session['user_id']
            )
            db.session.add(recipe)
            db.session.commit()
            return jsonify({
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username
                }
            }), 201
        except Exception as e:
            return {"error": str(e)}, 422