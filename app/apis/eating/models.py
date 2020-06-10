from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserFood(db.Model):
    __bind_key__ = 'eating'
    __tablename__ = 'userFood'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    nome_bar = db.Column(db.String(120), index=True, unique=True)
    foods = db.relationship('Food', backref='userFood')

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<foods {}>'.format(self.foods)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Food(db.Model):
    __bind_key__ = 'eating'
    __tablename__ = 'food'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120))
    image = db.Column(db.BLOB)
    tipologia = db.Column(db.String(120))
    descrizione = db.Column(db.String(120))
    prezzo = db.Column(db.Integer)
    sempre_attivo = db.Column(db.Boolean)
    data = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_username = db.Column(db.String(120), db.ForeignKey('userFood.nome_bar'))

    def __repr__(self):
        return '<Nome {}>'.format(self.nome)