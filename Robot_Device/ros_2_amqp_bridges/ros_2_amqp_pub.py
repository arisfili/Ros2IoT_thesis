import rospy
from amqp_protocol import PublisherSync
from amqp_protocol import amqpbase
from src.Conversions import ros_msg_to_dict
from amqp_protocol.publisher import PublisherSync
{% set msgPkg = ros_topic_type.split('/')[0] %}
{% set msgType = ros_topic_type.split('/')[1] %}
from {{ msgPkg }}.msg import {{ msgType }}

class {{conn_name}}(object):

    def __init__(self):
        self.ros_topic = "{{ros_topic_name}}"
        self.amqp_topic = self.ros_topic.replace("/",".")
        self.amqp_broker_host = "{{amqp_broker["host"]}}"
        self.amqp_broker_port = "{{amqp_broker["port"]}}"
        self.amqp_broker_username = "{{amqp_broker["username"]}}"
        self.amqp_broker_password = "{{amqp_broker["password"]}}"
        self.amqp_broker_vhost  = "{{amqp_broker["vhost"]}}"
        self.ros_message_type = {{msgType}}
        self.ros_node_name = "ros_topic{}_bridge".format(self.ros_topic.replace("/","_"))
        self._debug = False

        self.broker_conn_params = amqpbase.ConnectionParameters(host=self.amqp_broker_host,
                                                                port=self.amqp_broker_port,
                                                                vhost=self.amqp_broker_vhost)
        self.broker_conn_params.credentials = amqpbase.Credentials(self.amqp_broker_username, self.amqp_broker_password)
        self.broker_conn = amqpbase.SharedConnection(self.broker_conn_params)

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self,val):
        self._debug = val

    def run(self):
        self._init_ros_subscriber()
        self._init_rabbitmq_publisher()
        rospy.loginfo("bridge ros topic <{}> to amqp topic {}".format(self.ros_topic,self.amqp_topic))
        while not rospy.is_shutdown():
            pass
            # self.broker_conn.sleep(0.01)



    def _init_ros_subscriber(self):
        if self._debug:
            log_level = rospy.DEBUG
        else:
            log_level = rospy.INFO
        rospy.init_node(self.ros_node_name,anonymous=True,log_level=log_level)
        rospy.Subscriber(self.ros_topic,self.ros_message_type,self._ros_callback)
        rospy.loginfo("ros subscriber for topic <{}> ready".format(self.ros_topic))


    def _init_rabbitmq_publisher(self):
        self.broker_pub = PublisherSync(self.amqp_topic, connection=self.broker_conn,debug=True)
        rospy.loginfo("rabbitmq publisher for topic <{}> ready".format(self.amqp_topic))


    def _ros_callback(self,msg):
        try:
            data = ros_msg_to_dict(msg)
        except Exception as e:
            rospy.logerr("ros msg conversion error <{}>".format(e))
        self._publish(data)

    def _publish(self,data):
        if not isinstance(data,dict):
            raise ValueError("broker publish data should be type of dict")
        try:
            self.broker_pub.publish(data,thread_safe=True)
            rospy.loginfo("broker publish message")
        except Exception as e:
            rospy.logerr("exception <{}> while trying to publish messsage".format(e))

if __name__ == '__main__':
    bridge = {{conn_name}}()
    bridge.run()