from __future__ import print_function
from src.ros import ROSApi
from src.iot import RabbitmqBase
from src import publisher
from src import subscriber
from src import amqpbase
import json

def callback(msg, meta):
    channel = meta['channel']
    method = meta['method']
    props = meta['properties']
    print('[*] - Channel={}'.format(channel))
    print('[*] - Method={}'.format(method))
    print('[*] - Properties={}'.format(props))
    print('[*] - Data -->')
    print(json.dumps(msg, indent=2))

class Roslink (object):

    def __init__(self,hz,host,port,vhost,username,password):
        self.hz = hz
        self.host = host
        self.port = port
        self.vhost = vhost
        self.username = username
        self.password = password
        self.debug = True
        self.queue_size = 100
        self.roscore = ROSApi()
        self.rabbitmqcore = RabbitmqBase()
        self.ros_topics = self.roscore.get_topics()
        self.ros_services = self.roscore.get_services()
        self.ros_services = self.roscore.get_services()
        pass







    def sync_ros_topics (self):

        for ros_t in self.ros_topics:
            topic_name , topic_type = ros_t
            self.rabbitmqcore.add_topic(topic_name)
            pub = publisher.PublisherSync(topic_name,connection_params =
            amqpbase.ConnectionParameters(host =self.host , port=self.port ,vhost=self.vhost),
                                          creds=amqpbase.Credentials(self.username,self.password),
                                          debug=self.debug)
            self.rabbitmqcore.add_publisher(pub)
            sub = subscriber.SubscriberSync(
                topic_name, on_message=callback,
                connection_params=amqpbase.ConnectionParameters(
                    host=self.host, port=self.port, vhost=self.vhost),
                queue_size=self.queue_size,
                creds=amqpbase.Credentials(self.username, self.password),
                debug=self.debug
            )
            self.rabbitmqcore.add_subscriber(sub)







    def sync_ros_services(self):

        for r_srv in self.ros_services:
            srv_name = r_srv
            srv_type = self.roscore.get_service_type(srv_name)
            self.rabbitmqcore.add_service(srv_name)



