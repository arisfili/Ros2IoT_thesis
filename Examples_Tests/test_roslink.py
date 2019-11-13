
from src.roslink import Roslink



if __name__ == "__main__":
    hz = 2
    host = 'localhost'
    port = '5672'
    vhost = '/'
    username = 'guest'
    password = 'guest'
    bridge = Roslink(hz=hz,host=host,port=port,vhost=vhost,username=username,password=password)
    bridge.sync_ros_topics()

    pass