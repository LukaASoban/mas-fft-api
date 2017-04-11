#from app_init import db
import constants
import os
from flask import Flask
from flask_cors import CORS, cross_origin
from sqlalchemy.dialects.postgresql import JSON
from flask_sqlalchemy import SQLAlchemy
import uuid
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADER'] = 'Content-Type'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fft_db:fftslam2017@fft-db2.cmridtwsayjd.us-east-1.rds.amazonaws.com:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['WTF_CSRF_ENABLED'] = False
db = SQLAlchemy(app)
#db = SQLAlchemy(app)
def uuid_gen():
    return str(uuid.uuid4())

# Create our database model
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.String(120), primary_key=True, default=uuid_gen)
    created_time = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email_id = db.Column(db.String(120), unique=True)
    profile_pic_url = db.Column(db.String)
    phone_number = db.Column(db.Numeric)
    password = db.Column(db.String)
    location = db.Column(JSON)
    provider = db.Column(db.String)

    def __init__(self, user_json):
        self.created_time = user_json[constants.c_created_time]
        self.first_name = user_json[constants.c_first_name]
        self.last_name = user_json[constants.c_last_name]
        self.email_id = user_json[constants.c_email_id]
        self.provider = user_json[constants.c_provider]
        if constants.c_profile_pic_url in user_json:
            self.profile_pic_url = user_json[constants.c_profile_pic_url]
        if constants.c_phone_number in user_json:
            self.phone_number = user_json[constants.c_phone_number]
        if constants.c_location in user_json:
            self.location = user_json[constants.c_location]
        self.password = user_json[constants.c_password]

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def column_items(self):
        return dict([(c, getattr(self, c)) for c in self.columns])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.column_items)

    def to_json(self):
        return self.column_items



class Share(db.Model):
    __tablename__ = "shares"
    share_id = db.Column(db.String(120),primary_key=True, default=uuid_gen)
    created_time = db.Column(db.String(120))
    user_id = db.Column(db.String(120))
    serve_size = db.Column(db.Integer)
    last_time = db.Column(db.String)
    available_time = db.Column(db.String)
    food_type = db.Column(db.String)
    image_ids = db.Column(db.String)
    share_status = db.Column(db.String) #matched
    share_location = db.Column(JSON)
    #contact: 'name','phone_number','email'
    sharer_contact = db.Column(JSON) 
    # status = db.Column(db.String)
    # created_time = db.Column(db.String)

    def __init__(self, share_json):
        #self.share_id = share_json[constant.c_share_id]
        self.created_time = share_json[constants.c_created_time]
        self.user_id = share_json[constants.c_user_id]
        self.serve_size  = share_json[constants.c_serve_size ]
        self.last_time = share_json[constants.c_last_till]
        self.available_time = share_json[constants.c_available_time]
        self.food_type = share_json[constants.c_food_type]
        self.image_ids = share_json[constants.c_image_ids]
        self.share_status = share_json[constants.c_share_status]
        self.share_location = share_json[constants.c_share_location]
        self.share_contact = share_json[constants.c_contact]

        # self.status = c.c_status_open
        # self.created_time = datetime.utcnow().isoformat()[:-7] + 'Z'

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def column_items(self):
        return dict([(c, getattr(self, c)) for c in self.columns])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.column_items)

    def to_json(self):
        return self.column_items

class transportRequests(db.Model):
    __tablename__ = "transportreq"
    transport_id = db.Column(db.String(120), primary_key=True, default=uuid_gen)
    created_time = db.Column(db.String(120))
    transport_user_id = db.Column(db.String(120)) #transporter user_id
    transport_status = db.Column(db.String)
    
    pickup_location = db.Column(JSON) # share_location
    drop_location = db.Column(JSON) # request_location

    pickup_time = db.Column(db.String) # share_available_time
    delivery_time = db.Column(db.String) # request_available_time
    serve_size = db.Column(db.Integer) #minimum of sharer and requester
    
    request_user_id=db.Column(db.String)
    share_id = db.Column(db.String(120))
    #request_id = db.Column(db.String(120))
    #pickup_contact = db.Column(JSON)
    #drop_contact = db.Column(JSON)
    #transport_name = db.Column(db.String(120)) #name
    

    def __init__(self, transport_json):
        #self.transport_id = transport_json[constants.c_id]
        self.created_time = transport_json[constants.c_created_time]
        self.transport_user_id = transport_json[constants.c_transport_user_id]
        #self.transport_name = transport_json[constants.c_transport_name]
        self.pickup_location = transport_json[constants.c_pickup_location]
        self.drop_location = transport_json[constants.c_drop_location]
        #self.pickup_contact = transport_json[constants.c_pickup_contact]
        #self.drop_contact = transport_json[constants.c_drop_contact]
        self.pickup_time = transport_json[constants.c_pickup_time]
        self.delivery_time = transport_json[constants.c_delivery_time]
        self.serve_size = transport_json[constants.c_serve_size]
        self.transport_type = transport_json[constants.c_transport_type]
        self.transport_status = transport_json[constants.c_transport_status]
        #self.request_id = transport_json[constants.c_request_id]
        self.request_user_id = transport_json[constants.c_request_user_id]
        self.share_id = transport_json[constant.c_share_id]

    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def column_items(self):
        return dict([(c, getattr(self, c)) for c in self.columns])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.column_items)

    def to_json(self):
        return self.column_items

class Request(db.Model):
    __tablename__ = "request"
    request_id = db.Column(db.String(120), primary_key=True, default=uuid_gen)
    created_time = db.Column(db.String(120))
    user_id = db.Column(db.String(120))
    name = db.Column(db.String(120))
    pickup_location = db.Column(JSON)
    pickup_contact = db.Column(JSON)
    #contact: 'name','phone_number','email'
    available_till = db.Column(db.String) #time
    serve_size = db.Column(db.Integer)
    matched = db.Column(db.String)

    def __init__(self, request_json):
        #self.request_id = request_json[constants.c_request_id]
        self.created_time = request_json[constants.c_created_time]
        self.user_id = request_json[constants.c_user_id]
        self.name = request_json[constants.c_name]
        self.pickup_location = request_json[constants.c_pickup_location]
        self.pickup_contact = request_json[constants.c_pickup_contact]
        self.available_till = request_json[constants.c_available_till]
        self.serve_size = request_json[constants.c_serve_size]
        self.matched = request_json[constants.c_matched]


    @property
    def columns(self):
        return [c.name for c in self.__table__.columns]

    @property
    def column_items(self):
        return dict([(c, getattr(self, c)) for c in self.columns])

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.column_items)

    def to_json(self):
        return self.column_items

# app = Flask(__name__)
# cors = CORS(app)
# app.config['CORS_HEADER'] = 'Content-Type'
# #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://fft_db:fftslam2017@fft-db2.cmridtwsayjd.us-east-1.rds.amazonaws.com:5432/postgres'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['WTF_CSRF_ENABLED'] = False
# db = SQLAlchemy(app)
#db.create_all()    
with app.app_context():
    db.create_all()

