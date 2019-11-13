
import rosservice
import rostopic
import rosnode
from rospy import client
import rosgraph





class ParameterServerMixins(object):
    def has_param(self, param, clb=None):
        """Returns true if given ROS Parameter exists, false otherwise.

        Args:
            param (str): The ROS Parameter name.
            clb (function, optional): Callback function that is called upon response is received.
        """
        status = client.has_param(param)

        return status

    def get_param(self, param, default="", clb=None):
        """Returns the value of given ROS Parameter.

        Args:
            param (str): The ROS Parameter name.
            default (str, optional): Default value.
            clb (function, optional): Callback function that is called upon response is received.
        """
        status = client.get_param(param)

        return status


    def set_param(self, param, value, clb=None):
        """Sets the value of given ROS Parameter.

        Args:
            param (str): The ROS Parameter name.
            value (str, optional): Parameter value.
            clb (function, optional): Callback function that is called upon response is received.
        """
        status = client.set_param(param)

        return status

    def get_params_names(self, clb=None):
        """
            Retrieve list of parameter names.
        """
        status = client.get_param_names()

        return status

    def delete_param(self, param, clb=None):
        """
            Delete a parameter on the param server
        """
        client.delete_param(param)


class ServiceOperationMixins(object):
    def get_services(self, clb=None):
        """Returns a list of currently alive ROS Services."""

        ros_service_list = rosservice.get_service_list()

        return ros_service_list

    def get_service_type(self, svc_name, clb=None):
        """
        Args:
            svc (str): The ROS Service name.
            clb (function, optional): Callback function that is called upon response is received.
        """
        service_type = rosservice.get_service_type(svc_name)

        return service_type

    def get_services_for_type(self, svc_type, clb=None):
        """Returns a list of services of given type

        Args:
            svc_type (str): The ROS Service type.
            clb (function, optional): Callback function that is called upon response is received.
        """
        services_ft_list = rosservice.rosservice_find(svc_type)

        return services_ft_list


class TopicOperationsMixins(object):

    def get_topics(self, clb=None):
        """Returns a list of currently alive ROS Topics. Similar to `rostopic list`
        Args:
            topic_type (str): The Topic type.
            clb (function, optional): Callback function that is called upon response is received.
        """

        topics_list = client.get_published_topics('/')

        return topics_list



    def get_topic_type(self, topic_name, clb=None):
        """Returns a list of currently alive ROS Topics. Similar `rostopic type <topic_type>`.
        Args:
            topic_name (str): The Topic name.
            clb (function, optional): Callback function that is called upon response is received.
        """
        topic_type = rostopic.get_topic_type(topic_name)

        return topic_type




# class PublisherOperationsMixins(object):
#     def get_publishers(self, topic, clb=None):
#         """Returns a list of currently alive ROS Publishers."""
#         req = {
#             'topic': topic
#         }
#         status, data = self._call(clb, req, "/rosapi/publishers", "rosapi/Publishers")
#         data = data.get("publishers", None) if not isinstance(data, basestring) else data
#         return status, data
#
#
# class SubscriberOperationsMixins(object):
#     def get_subscribers(self, topic, clb=None):
#         """Returns a list of currently alive ROS Subscribers."""
#         req = {
#             'topic': topic
#         }
#         status, data = self._call(clb, req, "/rosapi/subscribers", "rosapi/Subscribers")
#         print(data)
#         data = data.get("subscribers", None) if not isinstance(data, basestring) else data
#         return status, data


class NodeOperationsMixins(object):

    def get_nodes(self, clb=None):
        """Returns a list of currently alive ROS Nodes."""

        node_list = rosnode.get_node_names()

        return node_list



    def get_node_details(self, node_name, clb=None):
        """Return detailes of given node. Include list of subscribers, publishers and services."""

        node_details = rosnode.get_node_info_description(node_name)

        return node_details

class ROSApi(ParameterServerMixins, ServiceOperationMixins,
             TopicOperationsMixins, NodeOperationsMixins,
             ):
    def __init__(self):
        pass

    def is_alive(self):
        if rosgraph.is_master_online():
            return True

