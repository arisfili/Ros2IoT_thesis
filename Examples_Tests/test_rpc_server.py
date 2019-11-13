#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import time
import amqp_protocol




class MyRpcServer(amqp_protocol.RpcServer):
    def __init__(self):
        pass


def callback(msg, meta):
    print('Received request: \nMessage -> {}\nProperties -> {}'.format(
        msg, meta['properties']))
    return msg


if __name__ == "__main__":

    host = "localhost"
    port = "5672"
    vhost = "/"
    username = "aris"
    password = "aris1993"
    rpc_name ="test"
    debug = False 

    conn_params = amqp_protocol.ConnectionParameters(
        host=host, port=port, vhost=vhost)
    conn_params.credentials = amqp_protocol.Credentials(username, password)
    conn = amqp_protocol.SharedConnection(conn_params)

    rpc_server = amqp_protocol.RpcServer(
        rpc_name, on_request=callback, connection=conn)

    rpc_server.run_threaded()
    time.sleep(10)
