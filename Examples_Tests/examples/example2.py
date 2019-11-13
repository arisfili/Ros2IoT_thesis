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
import time


class __ApplicationSession(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        print("session attached")
        while True:
            print(u"topic1", u"topic2")
            self.publish(u"topic1", u"topic2")
            yield sleep(1)




def ApplicationRunner_process(realm, channel):
    appRunner = ApplicationRunner(url=u"ws://127.0.0.1:8080/ws", realm=realm, extra={'channel': channel})
    appRunner.run(__ApplicationSession)


if __name__ == "__main__":
    # a = mp.Process(target=ApplicationRunner_process, args=(u'realm1', 'channel'))
    # a.start()
    # time.sleep(0.1)
    AppRun = [{'process': None, 'channel': 'BTC_LTC'},
              {'process': None, 'channel': 'BTC_XMR'}]

    for app in AppRun:
        app['process'] = mp.Process(target=ApplicationRunner_process, args=(u'realm1', app['channel']))
        app['process'].start()
        time.sleep(0.1)

    AppRun[0]['process'].join()
    AppRun[1]['process'].join()