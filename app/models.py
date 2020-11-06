from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    roles = db.relationship('Role', backref='user')

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<roles {}>'.format(self.roles)


class Role(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Role {}>'.format(self.role)


class TokenAuth(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    token_MD5 = db.Column(db.String(128), nullable=False)
    result = db.Column(db.Text, nullable=False)
    expire_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class UserNotifications(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'user_notifications'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    devices = db.relationship('Devices', backref='user_notifications')


class Devices(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'devices'
    token = db.Column(db.String(256), primary_key=True)
    device_model = db.Column(db.String(32), nullable=True)
    os_version = db.Column(db.String(16), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_notifications.id'))


class OtherUser(db.Model):
    __bind_key__ = 'users_roles'
    __tablename__ = 'otherUser'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    nome = db.Column(db.String(128))
    telefono = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
