from __future__ import absolute_import

import functools
from threading import Thread, Semaphore
from collections import deque
import json
import time

from .amqpbase import (AMQPTransportSync, Credentials, ExchangeTypes,
                             MessageProperties)
from .rate import Rate


class PublisherSync(AMQPTransportSync):
    def __init__(self, topic, exchange='amq.topic', *args, **kwargs):
        """
        Constructor.

        @param topic: Topic name to publish
        @type topic: string

        """
        self._topic_exchange = exchange
        self._topic = topic
        self._name = topic
        AMQPTransportSync.__init__(self, *args, **kwargs)
        self.connect()
        self.create_exchange(self._topic_exchange, ExchangeTypes.Topic)

    def publish(self, msg, thread_safe=True):
        """
        Publish message once.
        TODO: 1) Add message publishing timestamp
              2) Add Content-Type (handled at the application layer)
              3) Add Content-Encoding (handled at the application layer)

        @param msg: Message to publish.
        @type msg: dict

        """
        content_type = None
        if isinstance(msg, dict):
            content_type = 'application/json'
            content_encoding = 'utf8'
        elif isinstance(msg, str):
            content_type = 'text/plain'
            content_encoding = 'utf8'
        if isinstance(msg, bytes):
            content_type = 'application/octet-stream'
            content_encoding = 'utf8'
        #  elif isinstance(msg, unicode):
        #  content_type = 'text/plain'

        msg_props = MessageProperties(
            content_type=content_type,
            content_encoding=content_encoding,
            timestamp=int((time.time() + 0.5) * 1000))

        if thread_safe:
            self.connection.add_callback_threadsafe(
                functools.partial(self._pub, msg, msg_props))
        else:
            self._pub(msg, msg_props)
        # self.connection.add_callback_threadsafe(
        #     functools.partial(self.connection.process_data_events))
        self.connection.process_data_events()

    def _pub(self, msg, props):
        self._channel.basic_publish(
            exchange=self._topic_exchange,
            routing_key=self._topic,
            properties=props,
            body=self._serialize_data(msg))
        self.logger.debug('[x] - Sent %r:%r' % (self._topic, msg))


    def pub_loop(self, data_bind, hz):
        """
        Publish message frequenntly.

        @param data_bind: Bind to data for publishing.
        @type data_bind: dict

        @param hz: Publishing frequency.
        @type hz: float

        """
        if hz == 0.0:  # Publish once and return
            self.publish(data_bind)
            return
        elif hz < 0:
            self.logger.exception('Frequency must be in range [0+, inf]')
            raise ValueError('Frequency must be in range [0, inf]')
        self._rate = Rate(hz)
        while True:
            try:
                self.publish(data_bind)
                self._rate.sleep()
            except KeyboardInterrupt:
                self.logger.exception('Process received keyboard interrupt')
                break

    def _serialize_data(self, data):
        """
        TODO: Make Class. Allow different implementation of serialization
            classes.
        """
        return json.dumps(data)