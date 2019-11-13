from __future__ import print_function
import os
from ConfigParser import ConfigParser
from os import environ
from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner,ApplicationSessionFactory
import multiprocessing as mp


class MyAppComponent(ApplicationRunner):

    def __init__(self,topic_name,message):

        ApplicationRunner.__init__(self,url=u"ws://127.0.0.1:8080/ws",realm=u"realm1",extra={'topic':topic_name, 'message':message})

    def run_publisher(self):
        self.run(Compo, start_reactor=True)



class Compo(ApplicationSession):


    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")
        while True:
            print(self.config.extra['topic'], self.config.extra['message'])
            self.publish(unicode(self.config.extra['topic']),self.config.extra['message'])
            yield sleep(1)






if __name__ == '__main__':
    a = MyAppComponent("topic1","hello")
    b = MyAppComponent("topic2","goodbye")
    a.run_publisher()
    b.run_publisher()
    reactor.run()


