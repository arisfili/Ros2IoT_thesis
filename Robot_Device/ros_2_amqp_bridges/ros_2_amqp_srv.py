import rospy
from amqp_protocol import RpcServer, RpcClient ,Credentials,ConnectionParameters,SharedConnection
from src.Conversions import ros_srv_req_to_dict ,ros_srv_resp_to_dict,dict_to_ros_srv_request
{% set srvPkg = ros_srv_type.split('/')[0] %}
{% set srvType = ros_srv_type.split('/')[1] %}
from {{ srvPkg }}.srv import {{ srvType }}, {{ srvType }}Request, {{ srvType }}Response

class {{ conn_name }}(object):

    def __init__(self, connection=None):
        self.ros_service_uri = '{{ ros_srv_name }}'
        self.amqp_rpc_name = '{{ amqp_rpc_name }}'
        self.amqp_broker_ip = "{{amqp_broker["host"]}}"
        self.amqp_broker_port = "{{amqp_broker["port"]}}"
        self.amqp_broker_vhost = "{{amqp_broker["vhost"]}}"
        self.username = "{{amqp_broker["username"]}}"
        self.password = "{{amqp_broker["password"]}}"
        self.rpc_name = self.amqp_rpc_name
        self.ros_service_type = {{ srvType }}
        self.ros_srv_type_str = '{{ ros_srv_type }}'
        self.ros_node_name = "ros_service{}_bridge".format(self.ros_service_uri.replace("/","_"))
        if connection:
            self.broker_conn = connection
            return
        self.conn_params = ConnectionParameters(
            vhost=self.amqp_broker_vhost,
            host=self.amqp_broker_ip,
            port=self.amqp_broker_port)
        self.conn_params.credentials = Credentials(
            self.username, self.password)

        self.broker_conn = SharedConnection(self.conn_params)


    def run(self):
        self._init_rpc_server()
        self._init_ros_service()
        self.rpc_server.run_threaded()

    def _init_rpc_server(self):
        self.rpc_server = RpcServer(self.amqp_rpc_name,on_request=self._rpc_server_callback,
                                    connection=self.broker_conn)

    def _init_ros_service(self):

        rospy.init_node(self.ros_node_name,anonymous=True)
        rospy.loginfo("waiting for ros service {} response".format(self.ros_service_uri))
        rospy.wait_for_service(self.ros_service_uri)
        self.ros_srv = rospy.ServiceProxy(self.ros_service_uri,self.ros_service_type)
        rospy.loginfo("ros service client ready")

    def _rpc_server_callback(self, msg, meta):
        try:
            srv_req = dict_to_ros_srv_request(self.ros_srv_type_str, msg)
            resp = self.ros_srv(srv_req)
        except rospy.ServiceException as exc:
            rospy.logerr('ROS Service call failed: {}'.format(exc))
            resp = {{srvType}}Response()
        data = ros_srv_resp_to_dict(resp)
        return data

if __name__ == "__main__":
    bridge = {{conn_name}}()
    bridge.run()