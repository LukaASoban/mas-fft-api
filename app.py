#!/usr/bin/python
import os
#JUST TO COMMIT - SIGN UP, SIGN IN, SHARE WORKS
#from app_init import app
from model import app
import urllib2
import base64

from flask import request, json
import constants as c
from model import *

from werkzeug.utils import secure_filename
from uuid import uuid4
import boto
import os
import re
from PIL import Image
import cStringIO
from io import BytesIO
import requests

@app.route('/')
def index():
    return "Food for thought API v1.0"

@app.route('/upload_image', methods=['POST', 'GET'])
def upload_page():
    image_data = re.sub('^data:image/.+;base64,', '', request.form['image']).decode('base64')

    filename = uuid4().hex + '.jpg';

    # image = Image.open(filename,'w+')
    # image.write(image_data)

    image = Image.open(cStringIO.StringIO(image_data))
    acl = 'public-read'

    conn = boto.connect_s3(os.environ['S3_KEY'], os.environ['S3_SECRET'])
    b = conn.get_bucket(c.c_S3_BUCKET)

    sml = b.new_key(filename)
    out_im2 = cStringIO.StringIO()
    image.save(out_im2, 'JPEG')
    sml.set_contents_from_string(out_im2.getvalue())
    sml.set_acl(acl)

    return filename


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


    # url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(share_json["share_location"]["lat"]) +',' + str(share_json["share_location"]["lng"]) + "&sensor=true"
    # response = urllib2.urlopen(url)
    # temp = response.read()
    # data = json.loads(temp)

    # # print data['results'][0]
    # if data["results"]:

    #     address = data["results"][0]["formatted_address"]

    #     share_json["share_location"]["address"] = address.decode('utf-8')
    #     share = Share(share_json)
    # else:
    #     share_json["share_location"]["address"] = "NOT FOUND"
    #     share = Share(share_json)

    #next line is needed only if address resolution at front-end
    share = Share(share_json)
    db.session.add(share)
    db.session.commit()

    # return json.dumps(share.to_json())

    return 'Success'

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

@app.route('/share_cancel/<id>')
def share_cancel(id):
    query = db.session.query(Share).filter(Share.id == id)
    query.share_status = 'canceled'

    query2 = db.session.query(transportRequests).filter(transportRequests.share_id == id)
    query2.transport_status = 'share_canceled'

    return query2.request_user_id

# Get all active shares
@app.route('/shares_all')
def shares_all():
    query = db.session.query(Share).filter(Share.share_status=='active')
    res=[]
    for q in query:
        #user = db.session.query(User).filter(q.column_items[constants.c_user_id] == User.user_id)[0]
        d = {}
        for item in q.column_items:
             d[item] = q.column_items[item]
        # d[constants.c_full_name] = user.first_name+ ' '+user.last_name
        # print d
        res.append(json.dumps(d))
    return '['+','.join(res)+']'

## TRANSPORT ##

#api endpoints for posting a transport request - for INTERNAL USE ONLY
@app.route('/transport_postRequest', methods=['POST'])
def transport_postRequest():
    transport_json = json.loads(request.data)
    transport = transportRequests(transport_json)
    db.session.add(transport)
    db.session.commit()
    return "Success"


#api endpoint for matched requests, update transport table , MATCHED REQUESTS, CREATE TRANSPORT REQUEST
@app.route('/transport_createRequest',methods=['POST'])
def transport_createRequest():
    transport_json = json.loads(request.data)
    transport = transportRequests(transport_json)
    db.session.add(transport)


    # if transport_json["transport_type"]=='pickup':
    query2 = db.session.query(Share).filter(Share.share_id == transport_json['share_id'])
    query2.share_status = 'matched'
    db.session.commit()
    return json.dumps(transport.to_json())


#api endpoint for viewing all transport requests
@app.route('/transport_getRequests', methods=['GET'])
def transport_getRequests():
    query = db.session.query(transportRequests).filter(transportRequests.transport_type == 'delivery')
    res = []
    for q in query:
        #if q.transport_status == 'active':
        if q.transport_status =='active':
            # queryTemp = db.session.query()
            res.append(json.dumps(q.column_items))

    return '[' + ','.join(res) + ']'



#api endpoint for transporter accepting transport request
@app.route('/transport_acceptRequest',methods=['POST']) #required transport id and transporter(user_id)
def transport_acceptRequest():

    temp = json.loads(request.data)

    query = db.session.query(transportRequests).filter(transportRequests.transport_id == temp['transport_id'])
    print "HELLOSAKLNFLAKFNKLADFNLKFN"
    print type(query)
    # print len(query)
    query[0].transport_status = 'assigned'
    query[0].transport_user_id = temp['transport_user_id']

    url = "https://api.ionic.io/push/notifications"


    payload = {
    "tokens": ["c1WRKuB-_UE:APA91bGnoKqHsjrYsRlxv7mVbA574uhIx_ZVd-PrvaxRzaNmyKMxiR8952ToihbKDCvc4WJT0NT8F0xGoGD7kBclHt4MXM-j3L35HmveNAB8tiidGP7HebWzlz6jCnoP81RU1QM1pbvK"],
    "profile": "mas2017",
    "notification": {
        "title": "Test Test",
        "message": "Hello..This is special message for luka"
    }
    }
    

    headers = {
    'content-type': "application/json",
    'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIyYWI3NTNhNi1mYmYxLTQ4ZDYtOWEzZC1lZGIzMGI4NGQ2ZTMifQ.nRO6XwHOod2mGKHHtO-H13qHdrJQLWxxSurE17fLofI",
    'cache-control': "no-cache",
    'postman-token': "7e8e9e73-9ff6-69e5-ff68-4c0b94e26c12"
    }
    

    query3 = db.session.query(User).filter(User.user_id ==temp['request_user_id'] )
    tempDecode = query3[0].token
    payload['tokens'][0] = tempDecode.encode('ascii','ignore')
    print payload['tokens']
    response = requests.request("POST", url, data=payload, headers=headers)


    query3 = db.session.query(Share).filter(Share.share_id ==temp['share_id'] )
    query4 = db.session.query(User).filter(User.user_id ==query3[0].user_id )
    tempDecode = query4[0].token
    payload['tokens'][0] = tempDecode.encode('ascii','ignore')
    print payload['tokens']
    response = requests.request("POST", url, data=payload, headers=headers)
    print "RESPONSE",
    print response
    # query2 = db.session.query(Share).filter(Share.share_id == temp['share_id'])
    # query2.share_status = 'matched'

    db.session.commit()

    return ''


#api endpoint for transport request completion
@app.route('/transport_completeRequest/<id>')
def transport_completeRequest(id):
    query = db.session.query(transportRequests).filter(transportRequests.transport_id == id)
    query.transport_status = 'complete'

    query2 = db.session.query(Share).filter(Share.share_id == query.share_id)
    query2.share_status = 'complete'

    db.session.commit()

    #Assign brownie points to sharer and transporter
    #CODE GOES BELOW




## REQUEST FOOD ##
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

# @app.route('/request_activeRequest',methods=['POST'])
# def request_postRequest():
#     request.json = json.loads(request.data)
#     request_object = Request()


# Get detailed transport information for a transport request
@app.route('/transport/<id>', methods=['GET'])
def getTransportDetails(id):
    query = db.session.query(transportRequests).filter(transportRequests.transport_id == id).first()
    res = query.column_items
    query1 = db.session.query(Share).filter(Share.share_id == res[constants.c_share_id]).first()
    share_user_id = query1.user_id
    query2 =  db.session.query(User).filter(User.user_id == share_user_id).first().column_items
    query3 = db.session.query(User).filter(User.user_id == res["request_user_id"]).first().column_items
    res["share_user_name"] = query2["first_name"]+" "+query2["last_name"]
    res["share_user_contact"] = query2["phone_number"]
    res["request_user_name"] = query3["first_name"] + " " + query3["last_name"]
    res["request_user_contact"] = query3["phone_number"]
    return json.dumps(res)


def error_msg(param):
    err_j = {}
    err_j['Error'] = param
    return json.dumps(err_j)

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
