from app import db

class UserAccess(db.Model):
    __tablename__ = 'userAccess'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    classroom = db.Column(db.String(16))

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<classroom {}>'.format(self.classroom)