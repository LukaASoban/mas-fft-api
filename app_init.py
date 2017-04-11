import os
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
# from model import db
# #from model import User
# #from model import Share
# #from model import transportRequests
# #from model import Request

# app = Flask(__name__)
# cors = CORS(app)
# app.config['CORS_HEADER'] = 'Content-Type'
# #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fft_db:fftslam2017@fft-db2.cmridtwsayjd.us-east-1.rds.amazonaws.com:5432/postgres'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['WTF_CSRF_ENABLED'] = False
# db = SQLAlchemy(app)
# #db.create_all()
# with app.app_context():
#     db.create_all()