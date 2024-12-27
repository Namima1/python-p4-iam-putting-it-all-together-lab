from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False, default='default_hash')  # Default for testing
    image_url = db.Column(db.String, default='')
    bio = db.Column(db.String, default='')

    recipes = db.relationship('Recipe', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError("Password cannot be accessed directly.")

    @password.setter
    def password(self, plaintext_password):
        self._password_hash = generate_password_hash(plaintext_password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, default=1) 