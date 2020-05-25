from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Building(db.Model):
    __bind_key__ = 'ga'
    id_corso = db.Column(db.Integer, primary_key=True)
    struttura_des = db.Column(db.String(120))
    struttura_id = db.Column(db.String(10))
    struttura_ga_id = db.Column(db.Integer)
    corso_ga_id = db.Column(db.String(10))

    def __repr__(self):
        return '<Id Corso {}>'.format(self.id_corso)