from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

### <database> ###
SQLALCHEMY_DATABASE_URI = 'sqlite:///default.db'
SQLALCHEMY_BINDS = {
    'ga': 'sqlite:///apis/ga_uniparthenope/ga.db',
    'uniparthenope': 'sqlite:///apis/uniparthenope/uniparthenope.db',
    # Insert here your database
}
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'fPALYbDsVo119ifBO5Mk9Fwyd3mIdzzSqI3sPfQuzPlfco22LqpvHtOHMzKhZQ4'
### </database> ###


app = Flask(__name__, static_url_path='/')

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
from app.apis.uniparthenope import routes
from app.apis.ga_uniparthenope import routes
from app.apis.bus import routes
### </routes> ###
