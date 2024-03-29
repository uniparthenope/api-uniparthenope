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
    course_name = db.Column(db.String(128), nullable=False)
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime, index=True, nullable=False)
    username = db.Column(db.String(64), nullable=False)
    matricola = db.Column(db.String(32), nullable=False)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    id_lezione = db.Column(db.Integer, nullable=False)
    reserved_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return '<Id Lezione{}>'.format(self.id_lezione) + '<Id Corso{}>'.format(self.id_corso) + '<username{}>'.format(self.username)


class ReservableRoom(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'reservableRoom'
    
    id_corso = db.Column(db.String(16), primary_key=True)

    def __repr__(self):
        return '<Id Corso{}>'.format(self.id_corso)

class EntrySeq(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'entry_seq'
    id = db.Column(db.Integer, primary_key=True)

class Entry(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'entry'
    id = db.Column(db.String(64), primary_key=True, default='0', nullable=False)
    start_time = db.Column(db.DateTime, index=True, nullable=False)
    end_time = db.Column(db.DateTime, index=True, nullable=False)
    time = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(128), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

class Room(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    id_esse3 = db.Column(db.String(16), nullable=True)
    room_name = db.Column(db.String(64), nullable=False)
    piano = db.Column(db.String(16), nullable=False)
    lato = db.Column(db.String(16), nullable=True)
    capacity = db.Column(db.Integer, nullable=False)
    room_id = db.relationship('Entry', backref='room')
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    user_access = db.Column(db.String(32), nullable=True)


class Area(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True)
    area_name = db.Column(db.String(64), nullable=False)
    cod_area = db.Column(db.String(16), nullable=True)
    area_id = db.relationship('Room', backref='area')


class UserTemp(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'user_temp'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    matricola = db.Column(db.String(16), unique=True)


class GaTypes(db.Model):
    __bind_key__ = 'ga'
    __tablename__ = 'ga_types'
    type = db.Column(db.String(4), primary_key=True)
    type_name_abb = db.Column(db.String(32), nullable=False)
    type_name_complete = db.Column(db.String(128), nullable=True)
    cdsID = db.Column(db.String(128), nullable=True)

