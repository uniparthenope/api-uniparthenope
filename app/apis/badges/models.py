from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Badges(db.Model):
    __bind_key__ = 'badges'
    __tablename__ = 'badges'
    token = db.Column(db.String(256), primary_key=True)
    expire_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Token {}>'.format(self.token) + ", " +'<expire_time {}>'.format(self.expire_time)


class Scan(db.Model):
    __bind_key__ = 'badges'
    __tablename__ = 'scan'
    id = db.Column(db.Integer, primary_key=True)
    time_stamp =  db.Column(db.DateTime, index=True, default=datetime.utcnow)
    id_tablet = db.Column(db.String(64))
    username = db.Column(db.String(64))
    grpId = db.Column(db.Integer)
    matricola = db.Column(db.String(64))
    result = db.Column(db.String(64))
    scan_by = db.Column(db.String(64))

    def __repr__(self):
        return '<Id Tablet {}>'.format(self.id_tablet) + ", " +'<Result {}>'.format(self.result) + ", " +'<Time {}>'.format(self.time_stamp)