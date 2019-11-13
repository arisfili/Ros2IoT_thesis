from wampy.peers.clients import Client
# from wampy.mixins import
from wampy.peers.routers import Crossbar
import wampy.roles as subscriber
import time

# class wampyapp(Client):
#
#     @subscriber(topic = "topic1")
#     def clb (self,topicdata):
#         print topicdata



if __name__ == "__main__":
    cros = Crossbar()
    cros.start()
    client = Client(url= "ws://127.0.0.1:8080/ws",realm= "realm1")
    # client2 = Client(url="ws://127.0.0.1:8080/ws", realm="realm2")
    client.start()
    # client2.start()
    # client.publish(topic = "topic1", message = {'foo':"bar"})
    start = time.time()
    stop = start
    while (stop - start) < 5:
        print(stop - start)
        client.publish(topic="topic1", message={'foo': "bar"})
        client.publish(topic="topic2", message={'foo': "bar"})
        time.sleep(1)
        stop = time.time()
