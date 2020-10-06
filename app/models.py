from app import db
from datetime import datetime

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