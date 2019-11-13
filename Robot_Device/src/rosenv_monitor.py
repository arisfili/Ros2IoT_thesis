from src.ros import ROSApi
from amqp_protocol import PublisherSync
from amqp_protocol import amqpbase
import json
import time


class RosEnvMonitor(ROSApi):

    def __init__(self, conn_params, credentials,devicename):
        super(RosEnvMonitor, self).__init__()
        self.topics = []
        self.srv = []
        self.srv_type_list=[]
        self.nodes = []
        self.conn_parameters = conn_params
        self.creds = credentials
        self.publisher_topics = PublisherSync("{}/ros_env_topic_monitor".format(devicename), connection_params=self.conn_parameters,
                                             creds=self.creds, debug=True)
        self.publisher_nodes = PublisherSync("{}/ros_env_nodes_monitor".format(devicename), connection_params=self.conn_parameters,
                                             creds=self.creds, debug=True)
        self.publisher_services = PublisherSync("{}/ros_env_services_monitor".format(devicename), connection_params=self.conn_parameters,
                                                creds=self.creds, debug=True)

    def start(self):
        if self.is_alive():
            try:
                while True:
                    self.topics = self.get_topics()
                    self.srv = self.get_services()
                    for s in self.srv:
                        self.srv_type = self.get_service_type(s)
                        self.srv_type_list.append(self.srv_type)
                    self.ros_services = zip(self.srv,self.srv_type_list)
                    self.nodes = self.get_nodes()
                    self.publisher_nodes.publish(self._to_dict(self.nodes,"nodes"))
                    self.publisher_services.publish(self._to_dict(self.ros_services,"services"))
                    self.publisher_topics.publish(self._to_dict(self.topics,"topics"))
            except KeyboardInterrupt:
                return
        else:
            print ("ros master is offline")

    def _to_dict(self,list,key):
        dict = {}
        dict[key] =list
        return dict



if __name__ == '__main__':
    devicename = "ubuntu"
    hz = 2
    host = 'localhost'
    port = '5672'
    vhost = '/'
    username = devicename
    password = 'ubuntu'
    topic = 'test'
    debug = False
    connection_params = amqpbase.ConnectionParameters(
        host=host, port=port, vhost=vhost)
    creds = amqpbase.Credentials(username, password)
    ros = RosEnvMonitor(connection_params, creds,devicename)
    ros.start()
