#!/usr/bin/python
from flask import request, json
from flask_cors import cross_origin

from sqlalchemy import update, select, exists
import threading

import constants
import os

from app_init import app, db
from model import *


@app.route('/')
def index():
    return "Food for thought API v1.0"


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
