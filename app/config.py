import os

class Config:
    SECRET_KEY = os.getenv('SECRET_JKEY', 'default_secret_key')
    FOLDER_UPLOAD = './'
