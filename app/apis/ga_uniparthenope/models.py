from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Reservations(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'reservations'
    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        db.UniqueConstraint('username', 'id_lezione'),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_corso = db.Column(db.String(16), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    matricola = db.Column(db.String(32), nullable=False)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    id_lezione =  db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Id Lezione{}>'.format(self.id_lezione) + '<Id Corso{}>'.format(self.id_corso) + '<username{}>'.format(self.username)
