import os
from flask import Flask
from flask.ext.cors import CORS, cross_origin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fft_db:fftslam2017@fft-db2.cmridtwsayjd.us-east-1.rds.amazonaws.com:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


import model
from model import User

with app.app_context():
    db.create_all()



