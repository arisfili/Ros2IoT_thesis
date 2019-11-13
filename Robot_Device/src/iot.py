class RabbitmqBase(object):
    def __init__(self):
        self.publishers = list()
        self.subscribers = list()
        self.topics = list()
        self.services = list()
        self.devices = list()




    def add_publisher(self,publisher):

        self.publishers.append(publisher)

    def get_publisher(self):

        return self.publishers

    def add_subscriber(self,subscriber):

        self.subscribers.append(subscriber)

    def get_subscribers(self):

        return self.subscribers

    def add_topic(self,topic):

        self.topics.append(topic)

    def add_service(self,srv):

        self.services.append(srv)

    @property
    def return_services(self):

        return self.services
    @property
    def return_topics(self):

        return self.topics
    @property
    def return_publishers(self):

        return self.publishers
    @property
    def return_subscribers(self):

        return self.subscribers