import six

import json
from pymongo import MongoClient
import hashlib
import mongoengine as mdb
import datetime







class DeviceDb(mdb.Document):

    name = mdb.StringField(required=True,max_length=200,unique=True)
    role = mdb.StringField(required=True, max_length=200)
    token = mdb.StringField(required=True, max_length=200)
    connected = mdb.BooleanField(default=False, max_length=200)
    ip = mdb.StringField(required=False, default="", max_length=200)
    password = mdb.StringField(required=True, max_length=200)





    meta = {'collection': 'devices'}

    def to_dict(self):
        return json.loads(self.to_json())

class Users(mdb.Document):

    full_name = mdb.StringField(required= True , max_length=200)
    username = mdb.StringField(required=True,max_length=200,unique=True)
    password = mdb.StringField(required=True,max_length=200)
    devices = mdb.ListField(mdb.ReferenceField("DeviceDb", required=False,unique=True))

    meta = {'collection': 'users'}

    def to_dict(self):
        return json.loads(self.to_json())

class DeviceDbApi():

    def __init__(self):
        self.db = mdb.connect("test")




    def device_register(self ,msg):

        device_name = msg.get("name")
        model = msg.get("model")
        password = msg.get("pass")
        #print("Device Registration RPC called from: {}".format(details.caller))
        print("[*] - Device ID: {}".format(device_name))
        print("[*] - Model: {}".format(model))
        print("[*] - Password: {}".format(password))
        if device_name == None:
            print("Missing device name!")
        device_2 = DeviceDb(
            name=device_name,
            model=model,
            token=self._encrypt_string_sha512(password),
            role='robot',

        )
        try:
            device_2.save()
        except mdb.NotUniqueError as e:
            print(e)
            return {'result': False, 'error': 'Device with the same name allready exists. Must be unique.'}
        return {'result': True, 'error': ''}

    def get_all_devices(self):
        devices = []
        for device in DeviceDb.objects:
            d = device.to_dict()
            del d['token']
            devices.append(d)
        return devices


    def set_connected_devices(self, msg, details=None):
        device_name = msg['name']
        ip = msg['ip']
        connected = msg['connected']
        DeviceDb.objects(name=device_name).update(connected=connected, ip=ip,
                                                       add_to_set__ip_history=ip,
                                                       active_last=datetime.datetime.now)

    def get_conected_devices(self, msg, details=None):
        device_name = msg['name']
        device = DeviceDb.objects(name=device_name)
        d = device.to_dict()
        return d['connected']


    def delete_db(self):
        DeviceDb.objects.delete()

    def _encrypt_string_sha512(self, hash_str):
        return hashlib.sha512(hash_str.encode()).hexdigest()


if __name__ == '__main__':

    msg = {
        "full_name" :"robot2",
        "username":"aris",
        "pass" :"aris1993",

            }
    devices_2 = DeviceDbApi()
    #devices.delete_db()
    devices_2.device_register(msg)
    devices_db = devices_2.get_all_devices()
    pass
# {"full_name" :"robot2","username":"aris","password" :"aris1993"}
# {"device_name" :"robot2","username":"aris","device_password" :"aris1993"}