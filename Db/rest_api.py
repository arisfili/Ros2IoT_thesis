from flask import Flask
from flask_restplus import Api,Resource
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
api = Api(app = app)

@api.route("/auth")
class authentication(Resource):

    # @api.route("/auth/vhost", methods=["GET"])
    def get(self):
        return "allow"

    # @api.route("/auth/resource", methods=["GET"])
    def post(self):
        return "allow"

    # @api.route("/auth/topic", methods=["GET"])
    def authenticate_topic(self):
        return "allow"

    # @api.route("/auth/user", methods=["GET"])
    def authenticate_user(self):
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

if __name__== "__main__":
    app.run(debug=True,port=8080)