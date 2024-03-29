#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Highly inspired from: https://github.com/uts-magic-lab/rosduct
"""

from __future__ import print_function

import roslib.message
import rospy
import re
import base64

ROS_DATATYPE_MAP = {
    'bool': ['bool'],
    'int': ['int8', 'byte', 'uint8', 'char',
            'int16', 'uint16', 'int32', 'uint32',
            'int64', 'uint64', 'float32', 'float64'],
    'float': ['float32', 'float64'],
    'str': ['string'],
    'unicode': ['string'],
    'long': ['uint64']
}

PRIMITIVE_TYPES = [bool, int, float]
STRING_TYPES = [str]
LIST_TYPES = [list, tuple]

ROS_TIME_TYPES = ['time', 'duration']
ROS_PRIMITIVE_TYPES = ['bool', 'byte', 'char', 'int8', 'uint8', 'int16',
                       'uint16', 'int32', 'uint32', 'int64', 'uint64',
                       'float32', 'float64', 'string']
ROS_HEADER_TYPES = ['Header', 'std_msgs/Header', 'roslib/Header']
ROS_BINARY_TYPES_REGEX = re.compile(r'(uint8|char)\[[^\]]*\]')
ROS_BINARY_TYPES_REGEX_2 = r'(uint8|char)\[[^\]]*\]'
LIST_BRACKETS = re.compile(r'\[[^\]]*\]')


def _to_ros_type(_type, _value):
    if _is_ros_binary_type(_type):
        #  print("Type {0} is binary type".format(_type))
        _value = _to_ros_binary(_type, _value)
    elif _type in ROS_TIME_TYPES:
        #  print("Type {0} is time type".format(_type))
        _value = _to_ros_time(_type, _value)
    elif _type in ROS_PRIMITIVE_TYPES:
        #  print("Type {0} is primitive type".format(_type))
        _value = _to_ros_primitive(_type, _value)
    elif _is_type_an_array(_type):
        #  print("Type {0} is array type".format(_type))
        _value = _convert_to_ros_array(_type, _value)
    else:
        _value = dict_to_ros_msg(_type, _value)
    return _value


def _to_ros_binary(_type, _value):
    #  print("To ROS Binary: {}, {}".format(_type, type(_value)))
    # Convert to utf8 string if data format is unicode. ROS does not accept unicodes.
    if isinstance(_value, unicode):
        _value = _value.encode('utf8')
    binary_value_as_string = _value
    if type(_value) in STRING_TYPES:
        binary_value_as_string = base64.standard_b64decode(_value)
    else:
        binary_value_as_string = str(bytearray(_value))
    return binary_value_as_string


def _to_ros_time(_type, _value):
    time = None

    if _type == 'time' and _value == 'now':
        time = rospy.get_rostime()
    else:
        if _type == 'time':
            time = rospy.rostime.Time()
        elif _type == 'duration':
            time = rospy.rostime.Duration()
        if 'secs' in _value:
            setattr(time, 'secs', _value['secs'])
        if 'nsecs' in _value:
            setattr(time, 'nsecs', _value['nsecs'])
    return time


def _to_ros_primitive(_type, _value):
    if _type == "string" and isinstance(_value, unicode):
        _value = _value.encode('utf8')
    elif _type in ["float32", "float64"]:
        if _value == None:
            _value = float('Inf')
        #  if math.isnan(_value) or math.isinf(_value):
            #  print("IS Inf or NaN")
    return _value


def _convert_to_ros_array(_type, list_value):
    list_type = LIST_BRACKETS.sub('', _type)
    return [_to_ros_type(list_type, value) for value in list_value]


def _from_ros_type(_type, _value):
    if _is_ros_binary_type(_type):
        #  print("Data is ROS binary type")
        _value = _from_ros_binary(_value)
    elif _type in ROS_TIME_TYPES:
        _value = _from_ros_time(_value)
    elif _type in ROS_PRIMITIVE_TYPES:
        #  print("Data is ROS primitive type")
        _value = _value
    elif _is_type_an_array(_type):
        #  print("Data is Array")
        _value = _from_ros_array(_type, _value)
    else:
        _value = _ros_to_dict(_value)
    return _value


def _is_ros_binary_type(_type):
    """Check if the field is a binary array one, fixed size or not
    Args:
        _type (str): The ROS message field type.
        _val (str|int|char|...): The ROS message field value.
    """
    c = re.search(ROS_BINARY_TYPES_REGEX, _type) is not None
    #  print("IS ROS BINARY: {}, {}".format(_type, c))
    return c


def _from_ros_binary(_value):
    """ROS encodes buffers (uint8[]) into base64 strings.
    Args:
        _type (str): Data to serialize.
    """
    _value = base64.standard_b64encode(_value)
    return _value


def _from_ros_time(_value):
    _value = {
        'secs': _value.secs,
        'nsecs': _value.nsecs
    }
    return _value


def _from_ros_primitive(_type, _value):
    return _value


def _from_ros_array(_type, _value):
    list_type = LIST_BRACKETS.sub('', _type)
    return [_from_ros_type(list_type, value) for value in _value]


def _get_message_fields(message):
    """ From here: http://wiki.ros.org/msg -> 4. Client Library Support
    In Python, the generated Python message file (e.g. std_msgs.msg.String) provides
    nearly all the information you might want about a .msg file. You can examine the
    __slots__ and _slot_types and other fields to introspect information about messages.
    """
    return zip(message.__slots__, message._slot_types)


def _is_type_an_array(_type):
    return LIST_BRACKETS.search(_type) is not None


def _dict_to_ros(message, dictionary):
    """Take in the message type and a Python dictionary and returns
    a ROS message.
    Args:
        message_type (str): The ROS Message type, e.g. ``std_msgs/String``
        dictionary (dict): The dictionary to transform to ROS Message
    Example:
        message_type = "std_msgs/String"
        dict_message = { "data": "Hello, Robot" }
        ros_message = dict_to_ros(message_type, dict_message)
    """
    message_fields = dict(_get_message_fields(message))

    for field_name, _value in dictionary.items():
        if field_name in message_fields:
            _type = message_fields[field_name]
            _value = _to_ros_type(_type, _value)
            setattr(message, field_name, _value)
        else:
            err = 'ROS message has no field named "{1}"'\
                .format(field_name)
            #  err = 'ROS message type "{0}" has no field named "{1}"'\
                #  .format(message_type, field_name)
            raise ValueError(err)
    return message

def _ros_to_dict(message):
    """Take in a ROS message and returns a Python dictionary.
    Example:
        ros_message = std_msgs.msg.String(data="Hello, Robot")
        dict_message = ros_to_dict(ros_message)
    """
    dictionary = {}
    message_fields = _get_message_fields(message)
    for field_name, _type in message_fields:
        _value = getattr(message, field_name)
        dictionary[field_name] = _from_ros_type(_type, _value)
    return dictionary

def _srv_type_to_instance(service_type, request=False, response=False):
    srv_cls = get_service_class(service_type, reload_on_error=False)
    srv = srv_cls()
    if request:
        _cls = srv._request_class
    elif response:
        _cls = srv._response_class
    _instance = _cls()
    return _instance

def dict_to_ros_msg(message_type, dictionary):
    """Transform a dict object into a ROS Message, given it's type.
    Args:
        - message_type (str): The ROS Message type.
        - dictionary (dict): Dictionary to convert to ROS Message
    Example:
    >> dict_to_ros_msg("std_msgs/String", {})
    """
    message_class = get_message_class(message_type)
    message = message_class()
    return _dict_to_ros(message, dictionary)

def ros_msg_to_dict(message):
    """Convert a ROS Message into a dict.
    Args:
        - message (ROS Message)
    """
    return _ros_to_dict(message)

def get_message_class(message_type):
    """Return an instance of given message type.
    Exports roslib.message.get_message_class(message_type) under this module.
    http://docs.ros.org/diamondback/api/roslib/html/python/roslib.message-module.html
    Args:
        - message_type: The message type, e.g 'std_msgs/String'
    """
    return roslib.message.get_message_class(message_type)

def get_service_class(service_type, reload_on_error=False):
    """Return an instance of given message type.
    Exports roslib.message.get_message_class(message_type) under this module.
    http://docs.ros.org/diamondback/api/roslib/html/python/roslib.message-module.html
    Args:
        - service_type: The service type.
    """
    return roslib.message.get_service_class(service_type, reload_on_error=reload_on_error)

def dict_to_ros_srv_response(service_type, dictionary):
    srv_obj = _srv_type_to_instance(service_type, response=True)
    return _dict_to_ros(srv_obj, dictionary)

def dict_to_ros_srv_request(service_type, dictionary):
    srv_obj = _srv_type_to_instance(service_type, request=True)
    return _dict_to_ros(srv_obj, dictionary)

def ros_srv_req_to_dict(srv_req):
    return _ros_to_dict(srv_req)

def ros_srv_resp_to_dict(srv_resp):
    return _ros_to_dict(srv_resp)

def fill_ros_message(message, dictionary):
    """Take in the ROS Message instance and a Python dictionary and fills.
    Dictionary values are applied to the corresponding ROS Message
    properties.
    Args:
        message_type (str): The ROS Message type, e.g. ``std_msgs/String``
        dictionary (dict): The dictionary to transform to ROS Message
    Example:
        message_type = "std_msgs/String"
        dict_message = { "data": "Hello, Robot" }
        ros_message = dict_to_ros(message_type, dict_message)
    """
    return _dict_to_ros(message, dictionary)


if __name__ == "__main__":
    srv_req = dict_to_ros_srv_request('std_srvs/Trigger', {})
    print(srv_req)
    srv_resp = dict_to_ros_srv_response('std_srvs/Trigger',
                                        {'success': True, 'message': 'Do it!'})
    print(srv_resp)
    d = ros_srv_req_to_dict(srv_req)
    print(d)
    d = ros_srv_resp_to_dict(srv_resp)
    print(d)

    from sensor_msgs.msg import Image
    message = Image()
#
    print("------------------<sensor_msgs/Image>-------------------")
    from PIL import Image
    im = Image.open('Lenna.png')
    width, height = im.size

    message.height = height
    message.width = width
    message.step = width
    message.data = str(list(im.getdata()))

    print("From sensor_msgs/Image to dict...")
    _dict = ros_msg_to_dict(message)
    print("From dict to sensor_msgs/Image...")
    msg = dict_to_ros_msg("sensor_msgs/Image", _dict)
    print("Fill ROS Message instance of sensor_msgs/Image...")
    msg = fill_ros_message(message, _dict)
    print("-------------------------------------------------------")