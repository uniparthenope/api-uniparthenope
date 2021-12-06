from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config

app = Flask(__name__, static_url_path='/')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

### <SWAGGER> ###
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
### </SWAGGER> ###

### <DATABASE> ###
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
### </DATABASE> ###

from app.utils import Utils

sched = BackgroundScheduler()
sched.add_job(Utils.obscure_data, 'cron', minute='0', hour='23')
sched.start()

### <ROUTES> ###
# from app.apis.auth import routes
from app.apis.access import routes
from app.apis.uniparthenope import routes
from app.apis.ga_uniparthenope import routes
from app.apis.bus import routes
from app.apis.badges import routes
from app.apis.eating import routes
from app.apis.notifications import routes
from app.apis.export import routes
### </ROUTES> ###
