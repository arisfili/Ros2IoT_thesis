from flask import Flask
from flask_pymongo import PyMongo
from flask import jsonify
from flask import request
import hashlib
from flask_mongoengine import MongoEngine
from user_device_db import DeviceDb , Users


DB_NAME = "test"
DB_HOST = "127.0.0.1"
DB_PORT = 27017

app = Flask(__name__)
app.config["MONGODB_SETTING"]={"host":'mongodb://{}:{}/{}'.format(DB_HOST, DB_PORT,DB_NAME)}
mongo = MongoEngine(app)

@app.route("/auth/vhost", methods=["GET"])
def authenticate_vhost():
    return "allow"

@app.route("/auth/resource", methods=["GET"])
def authenticate_resource():
    return "allow"

@app.route("/auth/topic", methods=["GET"])
def authenticate_topic():
    return "allow"

@app.route("/auth/user", methods=["GET"])
def authenticate_user():
    username = request.args["username"]
    password = request.args["password"]
    users = Users.objects
    device = DeviceDb.objects
    token = hashlib.sha512(password.encode()).hexdigest()
    try:
        user = users.get(username = username)
        if user["password"] == password :
            return "allow"
    except:
        print("user not found")
    try:
        device = device.get(name = username)
        if device["token"] ==token:
            return "allow"
    except:
        print ("device not found")
    return "deny"



@app.route("/register/user", methods=["POST"])
def register_user():
    full_name = request.json["fullname"]
    username = request.json["username"]
    password = request.json["password"]
    if full_name == None:
        print("Missing name!")
    user = Users(full_name= full_name,
                 username = username,
                 password = password)
    try:
        user.save()
        return jsonify({"result": "Done"})
    except:
        # raise ValueError ("user with username {} already exists".format(username))
        return jsonify({"result": "user with username {} already exists".format(username)})

@app.route("/users/register_device", methods=["POST"])
def register_user_device():
    username = request.json["username"]
    device_name = request.json["device_name"]
    device_password = request.json["password"]
    users = Users.objects
    if  users.get(username = username) == None:
        raise ValueError("user with username {} does not exist".format(username))
    user = users.get(username = username)
    token = hashlib.sha512(device_password.encode()).hexdigest()
    if device_password == None:
        print ("missing device password")
    devices = DeviceDb.objects
    try:
        device = devices.get(name = device_name)
    except:
        return jsonify({"result":" device with device name {} does not exist".
                       format(device_name)})
        #raise Exception ("device with device name {} does not exist".format(device_name))
    if device["token"] == token:
        if device in user.devices:
            return jsonify({"result":"device is already in users list"})
            #raise ValueError("device is already in users list")
        else:
            user.devices.append(device)
            user.save()

    else:
        return jsonify({"result":"You  have  no access to device {} "
                       .format(device_name)})

    return jsonify({"result":"Done"})

@app.route("/devices", methods=["GET"])
def get_all_devices():
    devices = DeviceDb.objects
    output = []
    for d in devices:
        output.append({"name":d["name"]
                       })
    return jsonify({"list of devices":output})


@app.route("/devices/connected", methods=["GET"])
def get_connected_devices():
    output = []
    devices = DeviceDb.objects
    for d in devices:
        if d["connected"] == True :
            output.append({"name": d["name"]})
    return jsonify({"connected devices":output})


@app.route("/devices/<string:name>", methods=["GET"])
def get_device_details(name):
    devices = DeviceDb.objects
    device = devices.get(name = name)
    output = [{"role":device["role"],
               "model":device["model"],
               "ip":device["ip"],
               "connected":device["connected"]}]
    return jsonify({"device details":output})


@app.route("/register/device", methods=["POST"])
def register_device():
    name = request.json["name"]
    password = request.json["password"]
    role = request.json["role"]
    ip = request.json["ip"]
    token = hashlib.sha512(password.encode()).hexdigest()
    if name == None:
        print("Missing device name!")
    try:
        device = DeviceDb(name = name,
                          password = password,
                          role = role,
                          token = token,
                          ip = ip)
        device.save()
        return {"result": "Done"}
    except:
         # raise ValueError("device with name {} already exists".format(name))
        return {"result":"device with name {} already exists".format(name)}

@app.route("/devices/connect/<string:name>", methods=["POST"])
def set_device_connected(name):
    devices = DeviceDb.objects
    device = devices.get(name = name)
    device.update(connected = True)
    return {"result":"done"}

@app.route("/user/device",methods =["GET"])
def get_user_devices():
    username = request.json["username"]
    users = Users.objects
    user = users.get(username = username)
    devices = user["device"]
    output = []
    for d in devices:
        output.append({"name": d["name"]
                       })
    return jsonify({"list of devices":output})

@app.route("/device/temp",methods =["GET"])
def get_device_temp():
    return jsonify({"temperature":50})

@app.route("/device/alarm",methods =["POST"])
def set_device_alarm():
    return jsonify({"result":"done"})


if __name__== "__main__":
    app.run(debug=True,port=8080)