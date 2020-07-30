from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin

import os

### <database> ###
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default.db')
SQLALCHEMY_BINDS = {
    'access': 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apis/access/access.db'),
    'eating': 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apis/eating/eating.db'),
    'ga': 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apis/ga_uniparthenope/ga.db'),
    'uniparthenope': 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apis/uniparthenope/uniparthenope.db'),
    'badges': 'sqlite:///' + os.path.join(os.path.dirname(os.path.realpath(__file__)), 'apis/badges/badges.db')
    # Insert here your database
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '---'
### </database> ###


app = Flask(__name__, static_url_path='/')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

authorizations = {
    'Basic Auth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Authorization'
    },
}

api = Api(app, version='1.0', title='University of Naples "Parthenope" API',
          description='A simply and affordanble path to accelerate STEM knowledge via a smarter and smarter University',
          authorizations=authorizations)

# app.config.from_object(Config)
app.config.from_object(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

### <routes> ###
from app.apis.auth import routes
from app.apis.access import routes
from app.apis.uniparthenope import routes
from app.apis.ga_uniparthenope import routes
from app.apis.bus import routes
from app.apis.badges import routes
from app.apis.eating import routes
### </routes> ###
