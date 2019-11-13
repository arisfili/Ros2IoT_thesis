import amqp_protocol
import time


class Rabbitmq():
    def __init__(self):
        self.port = None
        self.host = None
        self.username = None
        self.password = None
        self.vhost = None
        self.connection_parameters = None
        self.stat_data = None
        self.topics = None
        self.services = None
        self.nodes = None

    @property
    def port(self):
        return self.port

    @port.setter
    def port(self, value):
        self.port = value

    @property
    def host(self):
        return self.host

    @host.setter
    def host(self, value):
        self.host = value

    @property
    def username(self):
        return self.username

    @username.setter
    def username(self, value):
        self.username = value

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, value):
        self.password = value

    @property
    def vhost(self):
        return self.vhost

    @vhost.setter
    def vhost(self, value):
        self.vhost = value

    def connect(self):
        self.conn_params = amqp_protocol.ConnectionParameters(
            host=self.host, port=self.port, vhost=self.vhost)
        self.conn_params.credentials = amqp_protocol.Credentials(self.username,
                                                                 self.password)
        self.conn = amqp_protocol.SharedConnection(self.conn_params)

    def get_conn_parameters(self):
        return self.conn

    def sync_ros_topics(self,devicename):
        topic = "{}/ros_env_topic_monitor".format(devicename)
        self.sub_topics = self.sub = amqp_protocol.SubscriberSync(topic=topic
                                                                  , on_message=self.ros_topics,
                                                                  connection_params=self.conn_params,
                                                                  queue_size=20,
                                                                  creds=self.conn_params.credentials,
                                                                  debug=True
                                                                  )
        self.sub_topics.run_threaded()
        time.sleep(2)

    def sync_ros_nodes(self,devicename):
        topic = "{}/ros_env_nodes_monitor".format(devicename)
        self.sub_nodes = amqp_protocol.SubscriberSync(topic=topic
                                                      , on_message=self.ros_nodes,
                                                      connection_params=self.conn_params,
                                                      queue_size=20,
                                                      creds=self.conn_params.credentials,
                                                      debug=True
                                                      )
        self.sub_nodes.run_threaded()
        time.sleep(2)

    def sync_ros_services(self,devicename):
        topic = "{}/ros_env_services_monitor".format(devicename)
        self.sub_services = amqp_protocol.SubscriberSync(topic=topic
                                                         , on_message=self.ros_services,
                                                         connection_params=self.conn_params,
                                                         queue_size=20,
                                                         creds=self.conn_params.credentials,
                                                         debug=True
                                                         )
        self.sub_services.run_threaded()
        time.sleep(2)

    def ros_services(self, msg, meta):
        print("take data")
        self.services = msg
        self.sub_services.close()

    def ros_topics(self, msg, meta):
        print("take data")
        self.topics = msg
        self.sub_topics.close()

    def ros_nodes(self, msg, meta):
        print("take data")
        self.nodes = msg
        self.sub_nodes.close()

    def sync_device_stats(self, device_name):
        self.sub = amqp_protocol.SubscriberSync("{}/stats".format(device_name)
                                                , on_message=self.stats_data,
                                                connection_params=self.conn_params,
                                                queue_size=20,
                                                creds=self.conn_params.credentials,
                                                debug=True
                                                )
        self.sub.run_threaded()
        time.sleep(2)

    def bridge_publisher(self, topicname, topictype, devicename):
        rpc_name = "{}/bridge_pub".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg = {}
        msg["topic_name"] = topicname
        msg["topic_type"] = topictype
        msg["bridge"] = "start"
        # msg["broker"] = {"host": self.host,
        #                  "port": self.port,
        #                  "vhost": self.vhost,
        #                  "username": self.username,
        #                  "password": self.password}
        bridge = rpc_client.call(msg)

    def terminate_publisher(self,topicname,devicename):
        rpc_name = "{}/bridge_pub".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg ={}
        msg["bridge"]= "stop"
        msg["topic_name"] = topicname
        bridge = rpc_client.call(msg)



    def bridge_subscriber(self, topicname, topictype, devicename):
        rpc_name = "{}/bridge_sub".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg = {}
        msg["topic_name"] = topicname
        msg["topic_type"] = topictype
        msg["bridge"] = "start"
        # msg["broker"] = msg["broker"] = {"host": self.host,
        #                                  "port": self.port,
        #                                  "vhost": self.vhost,
        #                                  "username": self.username,
        #                                  "password": self.password}
        bridge = rpc_client.call(msg)

    def terminate_subscriber(self,topicname,devicename):
        rpc_name = "{}/bridge_sub".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg ={}
        msg["bridge"]= "stop"
        msg["topic_name"] = topicname
        bridge = rpc_client.call(msg)


    def bridge_service(self, servicename, servicetype, devicename):
        rpc_name = "{}/bridge_srv".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg = {}
        msg["srv_name"] = servicename
        msg["srv_type"] = servicetype
        msg["bridge"] = "start"
        bridge = rpc_client.call(msg)

    def terminate_service(self,servicename,devicename):
        rpc_name = "{}/bridge_srv".format(devicename)
        rpc_client = amqp_protocol.RpcClient(rpc_name, connection=self.conn)
        msg ={}
        msg["bridge"]= "stop"
        msg["srv_name"] = servicename
        bridge = rpc_client.call(msg)

    def stats_data(self, msg, meta):
        print("take data")
        self.stat_data = msg
        self.sub.close()

    def get_stats_data(self):
        return self.stat_data

    def get_topics(self):
        return self.topics

    def get_nodes(self):
        return self.nodes

    def get_services(self):
        return self.services


if __name__ == "__main__":
    rabbitmq = Rabbitmq()
    data = None
    rabbitmq.host = "localhost"
    rabbitmq.port = "5672"
    rabbitmq.vhost = "/"
    rabbitmq.username = "guest"
    rabbitmq.password = "guest"
    rabbitmq.connect()
    # device_name = "ubuntu"
    rabbitmq.sync_ros_nodes()
    data = rabbitmq.get_nodes()
    print(data)
    pass
