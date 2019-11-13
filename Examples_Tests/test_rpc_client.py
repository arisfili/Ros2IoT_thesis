#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import amqp_protocol



if __name__ == "__main__":

    host = "localhost"
    port = "5672"
    vhost = "/"
    username = "aris"
    password = "aris1993"
    rpc_name ="ubuntu/bridge_srv"
    debug = False
    hz = 2

    conn_params = amqp_protocol.ConnectionParameters(
        host=host, port=port, vhost=vhost)
    conn_params.credentials = amqp_protocol.Credentials(username, password)
    conn = amqp_protocol.SharedConnection(conn_params)

    rpc_client = amqp_protocol.RpcClient(rpc_name, connection=conn)

    msg = {}
    msg2 = {}
    # msg["srv_name"] ="/rosout_agg"
    # msg["topic_type"] = 'rosgraph_msgs/Log'
    # msg["broker"] =  {"host":"localhost",
    #           "port":"5672",
    #         "vhost":"/",
    #         "username":"aris",
    #         "password":"aris1993"}
    msg2["srv_name"] = "/turtle1/set_pen"
    msg2["srv_type"] = "turtlesim/SetPen"
    msg2["bridge"] = "start"
    msg["srv_name"] = "/turtle1/set_pen"
    msg["bridge"] = "stop"

    rpc_client.debug = True
    # rate =amqp_protocol.rate.Rate(hz)
    resp = rpc_client.call(msg2)
    resp2 = rpc_client.call(msg)
    #resp2 = rpc_client.call(msg2)



