from app import db


class UserAccess(db.Model):
    __bind_key__ = 'access'
    __tablename__ = 'userAccess'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    classroom = db.Column(db.String(16), default="presence")
    autocertification = db.Column(db.Boolean, default=True)
    grpId = db.Column(db.Integer)
    persId = db.Column(db.Integer)
    stuId = db.Column(db.Integer)
    matId = db.Column(db.Integer)
    matricola = db.Column(db.String(16))
    cdsId = db.Column(db.Integer)
    GP_expire = db.Column(db.DateTime, default='2001-01-01 00:00:00')
    greenpass = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username) + '<classroom {}>'.format(self.classroom) + '<flag {}>'.format(self.autocertification)
