from __future__ import print_function
import amqp_protocol
import sys
import argparse
from ros_2_amqp_bridges.deployment_manager import BridgeDeploy










def callback(msg, meta):
    print('Received request: \nMessage -> {}\nProperties -> {}'.format(
        msg, meta['properties']))
    if msg["bridge"] == "start":
        bridge.bridge_ros_srv(msg["srv_name"], msg["srv_type"])
    elif msg["bridge"] == "stop":
        bridge.terminate_bridge(msg["srv_name"],"srv_bridges")



if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='AMQP RPC Server CLI.')
    # parser.add_argument(
    #     '--host',
    #     dest='host',
    #     help='AMQP broker host (IP/Hostname)',
    #     default='localhost')
    # parser.add_argument(
    #     '--port',
    #     dest='port',
    #     help='AMQP broker listening port',
    #     default='5672')
    # parser.add_argument(
    #     '--vhost',
    #     dest='vhost',
    #     help='Virtual host to connect to.',
    #     default='/klpanagi')
    # parser.add_argument(
    #     '--username',
    #     dest='username',
    #     help='Authentication username',
    #     default='bot')
    # parser.add_argument(
    #     '--password',
    #     dest='password',
    #     help='Authentication password',
    #     default='b0t')
    # parser.add_argument(
    #     '--debug',
    #     dest='debug',
    #     help='Enable debugging',
    #     type=bool,
    #     const=True,
    #     nargs='?')

    host = "localhost"
    port = "5672"
    vhost = "/"
    device_name = "ubuntu"
    username = device_name
    password = "ubuntu"
    rpc_name = "{}/bridge_srv".format(device_name)
    hz = 2
    debug = True
    msg = {}
    debug = True
    global bridge
    msg["broker"] = {"host": host,
                     "port": port,
                     "vhost": vhost,
                     "username": username,
                     "password": password}
    bridge = BridgeDeploy(msg["broker"])

    conn_params = amqp_protocol.ConnectionParameters(
        host=host, port=port, vhost=vhost)
    conn_params.credentials = amqp_protocol.Credentials(username, password)
    conn = amqp_protocol.SharedConnection(conn_params)

    rpc_server = amqp_protocol.RpcServer(
        rpc_name, on_request=callback, connection=conn)
    rpc_server.run()