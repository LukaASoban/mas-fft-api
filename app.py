#!/usr/bin/python
import os
from app_init import app

from flask import request, json
import constants as c
from model import *

from werkzeug.utils import secure_filename
from uuid import uuid4
import boto



@app.route('/')
def index():
    return "Food for thought API v1.0"

# Upload images
# class UploadForm(FlaskForm):
#     example = FileField('Example File')

@app.route('/upload_image', methods=['POST', 'GET'])

def get_full_image_path(image_id):
    return "/".join([c.c_S3_AWS_URL, c.c_S3_BUCKET, image_id])

def upload_page():
    image = request.files['image']
    acl = 'public-read'

    source_filename = secure_filename(image.filename)
    source_extension = os.path.splitext(source_filename)[1]

    destination_filename = uuid4().hex + source_extension

    conn = boto.connect_s3(c.c_S3_KEY, c.c_S3_SECRET)
    b = conn.get_bucket(c.c_S3_BUCKET)

    sml = b.new_key(destination_filename)
    sml.set_contents_from_string(image.read())
    sml.set_acl(acl)

    return destination_filename

@app.route('/register', methods=['POST'])
def create_user_handler():
    user_json = json.loads(request.data)
    email = user_json[constants.c_email_id]
    res = db.session.query(User).filter(User.email_id == email)
    if not res.count():
        reg = User(user_json)
        db.session.add(reg)
        db.session.commit()
        return json.dumps(reg.to_json())
    elif res.first().provider == 'FACEBOOK':
        return json.dumps(res.first().column_items)
    return error_msg('Unable to create user')


@app.route('/login', methods=['POST'])
def login():
    login_json = json.loads(request.data)
    email = login_json[constants.c_email_id]
    password = login_json[constants.c_password]
    for user in db.session.query(User).filter(User.email_id == email):
        user_json = user.to_json()
        if password == user_json[constants.c_password]:
            return json.dumps(user_json)
        else:
            return error_msg('Invalid Credentails')
    return error_msg('No user found')


@app.route('/user/<userid>')
def user(userid):
    res = db.session.query(User).filter(User.id == userid)
    if res.count():
        for r in res:
            return json.dumps(r.column_items)
    return error_msg('No user found')


## SHARE ##

# Post a share request
@app.route('/share', methods=['POST'])
def share():
    share_json = json.loads(request.data)
    share = Share(share_json)
    db.session.add(share)
    db.session.commit()
    return ''

# Get all active shares for a user
@app.route('/shares_user/<userid>')
def shares_user(userid):
    query = db.session.query(Share).filter(Share.user_id == userid)
    res=[]
    for q in query:
        res.append(json.dumps(q.column_items))
    return '['+','.join(res)+']'

# Get details of a share
@app.route('/shares_id/<id>')
def shares_id(id):
    query = db.session.query(Share).filter(Share.id == id)
    res=[]
    for q in query:
        res.append(json.dumps(q.column_items))
    return '['+','.join(res)+']'

# Get all active shares
@app.route('/shares_all')
def shares_all():
    query = db.session.query(Share)
    res=[]
    for q in query:
        user = db.session.query(User).filter(q.column_items[constants.c_user_id] == User.id)[0]
        d = {}
        for item in q.column_items:
             d[item] = q.column_items[item]
        d[constants.c_full_name] = user.first_name+ ' '+user.last_name
        print d
        res.append(json.dumps(d))
    return '['+','.join(res)+']'

## TRANSPORT ##

@app.route('/transport_postRequest', methods=['POST'])
def transport_postRequest():
    transport_json = json.loads(request.data)
    transport = transportRequests(transport_json)
    db.session.add(transport)
    db.session.commit()
    return "Success"


@app.route('/transport_getRequests', methods=['GET'])
def transport_getRequests():
    query = db.session.query(transportRequests)
    res = []
    for q in query:
        res.append(json.dumps(q.column_items))
    return '[' + ','.join(res) + ']'

@app.route('/requestsPost',methods=['POST'])
def requestPost():
    request_json = json.loads(request.data)
    request1 = Request(request_json)
    db.session.add(request1)
    db.session.commit()
    return "Success"

@app.route('/requestsGet', methods=['GET'])
def requestsGet():
    query = db.session.query(Request)
    res = []
    for q in query:
        res.append(json.dumps(q.column_items))
    return '[' + ','.join(res) + ']'


## REQUEST ##

@app.route('/request_postRequest', methods=['POST'])
def request_postRequest():
    request_json = json.loads(request.data)
    request_object = Request(request_json)
    db.session.add(request_object)
    db.session.commit()
    return ''



def error_msg(param):
    err_j = {}
    err_j['Error'] = param
    return json.dumps(err_j)

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
