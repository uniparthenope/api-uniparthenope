import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_BINDS = {
        'uniparthenope': 'sqlite:///app/apis/uniparthenope/uniparthenope.db',
        'demo': 'sqlite:///app/apis/demo/demo.db'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    extend_existing = True
    SECRET_KEY = 'fPALYbDsVo119ifBO5Mk9Fwyd3mIdzzSqI3sPfQuzPlfco22LqpvHtOHMzKhZQ4'
