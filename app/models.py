from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    roles = db.relationship('Role', backref='user')

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<roles {}>'.format(self.roles)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Role {}>'.format(self.role)