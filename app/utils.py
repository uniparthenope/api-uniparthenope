from app import Config
from cryptography.fernet import Fernet

class Utils(object):

    def encrypt_user(self, username):
        encoded_message = username.encode()
        f = Fernet(Config.CRYPTO_KEY)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message.decode('utf-8')

    def decrypt_user(self, crypted_usr):
        f = Fernet(Config.CRYPTO_KEY)
        return f.decrypt(bytes(crypted_usr,'utf8')).decode('utf-8')