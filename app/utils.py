from app import Config
from cryptography.fernet import Fernet
from app.apis.badges.models import Scan
from app import db
import datetime 


class Utils(object):

    @staticmethod
    def encrypt_user(username):
        encoded_message = username.encode()
        f = Fernet(Config.CRYPTO_KEY)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message.decode('utf-8')

    @staticmethod
    def decrypt_user(crypted_usr):
        f = Fernet(Config.CRYPTO_KEY)
        return f.decrypt(bytes(crypted_usr, 'utf8')).decode('utf-8')

    @staticmethod
    def obscure_data():
        print("Inizio cancellazione dati")
        scan = Scan.query.all()

        today = datetime.datetime.now()
        delta = datetime.timedelta(days=28)
        new_data = today - delta

        for s in scan:
            if s.time_stamp < new_data and s.username is not None and s.username != '_USERNAME_':
                s.username = '_USERNAME_'
                s.matricola = '_ID_'

        db.session.commit()
        print("Fine cancellazione dati")