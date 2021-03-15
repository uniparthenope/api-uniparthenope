from app import Config
from cryptography.fernet import Fernet
from app.apis.badges.models import Scan
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
        scan = Scan.query.all()

        tod = datetime.datetime.now()
        d = datetime.timedelta(days = 28)
        a = tod - d
        count = 0

        for s in scan:
            if s.time_stamp < a and s.username is not None:
                count += 1
