from app import Config
from cryptography.fernet import Fernet
from app.apis.badges.models import Scan


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
        print("Begin")
        scan = Scan.query.all()
        print(scan)