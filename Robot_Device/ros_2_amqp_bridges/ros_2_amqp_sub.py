import rospy
from amqp_protocol import Credentials,ConnectionParameters,SharedConnection,SubscriberSync
from src.Conversions import dict_to_ros_msg
{% set msgPkg = ros_topic_type.split('/')[0] %}
{% set msgType = ros_topic_type.split('/')[1] %}
from {{ msgPkg }}.msg import {{ msgType }}

class {{conn_name}}(object):

    def __init__(self):
        self.ros_topic = "{{ros_topic_name}}"
        self.amqp_topic = "{{amqp_topic}}"
        self.amqp_broker_host = "{{amqp_broker["host"]}}"
        self.amqp_broker_port = "{{amqp_broker["port"]}}"
        self.amqp_broker_username = "{{amqp_broker["username"]}}"
        self.amqp_broker_password = "{{amqp_broker["password"]}}"
        self.amqp_broker_vhost  = "{{amqp_broker["vhost"]}}"
        self.ros_message_type = {{msgType}}
        self.ros_node_name = "broker_topic{}_bridge".format(self.amqp_topic.replace(".","_"))
        self._debug = False


        self.broker_conn_params = ConnectionParameters(host=self.amqp_broker_host,
                                                       port = self.amqp_broker_port,
                                                       vhost= self.amqp_broker_vhost)
        self.broker_conn_params.credentials = Credentials(username=self.amqp_broker_username,
                                                          password = self.amqp_broker_password)
        self.broker_conn = SharedConnection(self.broker_conn_params)

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self,val):
        self._debug = val

    def run(self):
        self._init_rabbitmq_subscriber()
        self._init_ros_publisher()
        rospy.loginfo("bridge rabbitmq topic <{}> to ros topic {}".format(self.amqp_topic,self.ros_topic))
        while not rospy.is_shutdown():
            rospy.sleep(0.01)

    def _init_rabbitmq_subscriber(self):
        self.sub = SubscriberSync(self.amqp_topic,on_message=self._rabbitmq_callback,
                                  connection=self.broker_conn,queue_size=20,debug=self.debug)

        rospy.loginfo("rabbitmq subscriber to topic {} ready".format(self.amqp_topic))
        self.sub.run_threaded()


    def _init_ros_publisher(self):
        rospy.init_node(self.ros_node_name)
        self.ros_pub = rospy.Publisher(self.ros_topic,self.ros_message_type,queue_size=20)
        rospy.loginfo("ros publisher to  topic {} ready".format(self.ros_topic))

    def _rabbitmq_callback(self,msg,meta):
        try:
            ros_msg = dict_to_ros_msg("{{ros_topic_type}}",msg)
            self.ros_pub.publish(ros_msg)
        except Exception as e:
            rospy.logerr("could not convert dict to ros message".format(str(e)))

if __name__ == "__main__":
    bridge = {{conn_name}}()
    bridge.run()
