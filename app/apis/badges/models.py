from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Badges(db.Model):
    __bind_key__ = 'badges'
    token = db.Column(db.String(256), primary_key=True)
    expire_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Token {}>'.format(self.token) + ", " +'<expire_time {}>'.format(self.expire_time)