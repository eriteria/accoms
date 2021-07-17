import os
FLASK_DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
# SQLALCHEMY_DATABASE_URI = 'sqlite:////home/joseph/PycharmProjects/accoms/accoms/db.sqlite3'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ.get('SECRET_KEY')
# SECRET_KEY = "ldvsdsbvjdbvlsvbdblwbvdvbzldv "

UPLOAD_FOLDER = f"{os.getcwd()}/static/Uploads"
