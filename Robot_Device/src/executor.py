from wampy.peers.clients import Client
from wampy.peers.routers import Crossbar

class ExecutorBase(object):

    def __init__(self, url = "ws://127.0.0.1:8080/ws", port = 8080, realm = "realm1"):

        self.url = url
        self.remote_port = port
        self.realm = realm
        self._connected = False
        self._id_counter = 0
        self._publishers = {}
        self._publishers_count = {}
        self._subscribers = {}

    def gen_id(self):
        """Generate a new ID.

        Current implementation uses an auto-incremental method.

        Returns:
            Incremental ID:
        """
        self._id_counter += 1
        return self._id_counter

class Executor(ExecutorBase,Client):

    def __init__(self,  *args, **kwargs):

        ExecutorBase.__init__(self, *args, **kwargs)
        Client.__init__(self,url=self.url)




class ExecutorManager(Crossbar):
    '''''
    Starts crossbar.io and stops it anytime
    '''

    def __init__(self, *args, **kwargs):

        Crossbar.__init__(self,*args, **kwargs)

    def start(self):
        self.start()

    def stop(self):
        self.stop()










