import jinja2
from os.path import dirname, join
from os import chmod
import os
from src.ros import ROSApi
import sys
import subprocess


class BridgeDeploy():
    def __init__(self, amqp_broker):
        self.this_dir = dirname(__file__)
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.this_dir), lstrip_blocks=True,
                                            trim_blocks=True)
        self.ros_env = ROSApi()
        self.amqp_broker = amqp_broker

    def bridge_broker_topics(self, topic_name, ros_topic_type):
        bridge_templ = "ros_2_amqp_sub.py"
        tpl = self.jinja_env.get_template(bridge_templ)
        amqp_topic_name = topic_name.replace("/", ".")
        bridge_name = topic_name.replace("/", "_")
        ros_topic_name = topic_name

        if not os.path.exists(os.path.join(self.this_dir, "sub_bridges")):
            os.mkdir(os.path.join(self.this_dir, "sub_bridges"))
        try:
            gen_path = join(self.this_dir, "sub_bridges", "{}.py".format(bridge_name))
            with open(gen_path, "w") as f:
                f.write(
                    tpl.render(conn_name="sub_bridge", amqp_broker=self.amqp_broker,
                               ros_topic_name=ros_topic_name, ros_topic_type=ros_topic_type,
                               amqp_topic=amqp_topic_name)
                )
            chmod(gen_path, 509)
            try:
                sys.path.append(os.path.dirname(self.this_dir))
                p=subprocess.Popen(["python", gen_path])
                self.addsubprocess(gen_path, p)
            except Exception as ex:
                print(ex)

        except Exception as e:
            print (e)

    def bridge_ros_srv(self, ros_srv_name, ros_srv_type):
        bridge_templ = "ros_2_amqp_srv.py"
        tpl = self.jinja_env.get_template(bridge_templ)
        bridge_name = ros_srv_name
        dir_name = bridge_name.replace("/", "_")
        broker_rpc_name = ros_srv_name

        if not os.path.exists(os.path.join(self.this_dir, "srv_bridges")):
            os.mkdir(os.path.join(self.this_dir, "srv_bridges"))
        try:
            gen_path = join(self.this_dir, "srv_bridges", "{}.py".format(dir_name))
            with open(gen_path, "w") as f:
                f.write(
                    tpl.render(conn_name="sub_bridge", amqp_broker=self.amqp_broker,
                               ros_srv_name=ros_srv_name, ros_srv_type=ros_srv_type,
                               amqp_rpc_name=broker_rpc_name)
                )
            chmod(gen_path, 509)
            try:
                sys.path.append(os.path.dirname(self.this_dir))
                p= subprocess.Popen(["python", gen_path])
                self.addsubprocess(gen_path, p)
            except Exception as ex:
                print(ex)

        except Exception as e:
            print (e)

    def bridge_ros_topic(self, ros_topic_name, ros_topic_type):
        bridge_templ = "ros_2_amqp_pub.py"
        tpl = self.jinja_env.get_template(bridge_templ)
        if not os.path.exists(join(self.this_dir, "pub_bridges")):
            os.mkdir(os.path.join(self.this_dir, "pub_bridges"))
        try:
            bridge_name = ros_topic_name.replace("/", "_")
            gen_path = join(self.this_dir, "pub_bridges", "{}.py".format(bridge_name))
            with open(gen_path, "w") as f:
                f.write(
                    tpl.render(conn_name="pub_bridge", amqp_broker=self.amqp_broker,
                               ros_topic_name=ros_topic_name, ros_topic_type=ros_topic_type)
                )
            chmod(gen_path, 509)
            try:
                sys.path.append(os.path.dirname(self.this_dir))
                p = subprocess.Popen(["python", gen_path], shell=False)
                self.addsubprocess(gen_path, p)
            except Exception as ex:
                print(ex)

        except Exception as e:
            print (e)

    def addsubprocess(self, gen_path, p):
        self.subprocesses = []
        self.subprocesses.append([gen_path, p])

    def terminate_bridge(self, topic_name, bridge_type):
        bridge_name = topic_name.replace("/", "_")
        path = os.path.join(self.this_dir, bridge_type, "{}.py".format(bridge_name))
        for s in self.subprocesses:
            if s[0] == path:
               s[1].terminate()
               os.remove(path)


if __name__ == "__main__":
    broker = {"host": "localhost",
              "port": "5672",
              "vhost": "/",
              "username": "aris",
              "password": "aris1993"}
    bridge = BridgeDeploy(amqp_broker=broker)
    bridge.bridge_ros_topic("task1/numbers", "std_msgs/Int16")
    bridge.terminate_bridge("task1/numbers","pub_bridges")
    # bridge.bridge_ros_topic("/rosout_agg","rosgraph_msgs/Log")
    # bridge.bridge_ros_srv("add_two_ints","rospy_tutorials/AddTwoInts")
