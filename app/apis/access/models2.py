from app import db


class UserAccessFull(db.Model):
    __tablename__ = 'userAccessFull'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    classroom = db.Column(db.String(16))
    grpId = db.Column(db.Integer)
    persId = db.Column(db.Integer)
    stuId = db.Column(db.Integer)
    matId = db.Column(db.Integer)
    matricola = db.Column(db.String(16))
    cdsId = db.Column(db.Integer)

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<classroom {}>'.format(self.classroom)
