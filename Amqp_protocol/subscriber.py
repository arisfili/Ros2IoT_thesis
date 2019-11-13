from __future__ import absolute_import
from .amqpbase import AMQPTransportAsync,AMQPTransportSync,ConnectionParameters,Credentials,SharedConnection,MessageProperties,ExchangeTypes

from threading import Thread, Semaphore
from collections import deque
import json
import time


class SubscriberSync(AMQPTransportSync):

    FREQ_CALC_SAMPLES_MAX = 100

    def __init__(self,
                 topic,
                 on_message=None,
                 exchange='amq.topic',
                 queue_size=10,
                 message_ttl=60000,
                 overflow='drop-head',
                 *args,
                 **kwargs):

        self._name = topic
        AMQPTransportSync.__init__(self, *args, **kwargs)
        self._topic = topic
        self._topic_exchange = exchange
        self._queue_name = None
        self._queue_size = queue_size
        self._message_ttl = message_ttl
        self._overflow = overflow
        self.connect()
        if on_message is not None:
            self.onmessage = on_message
        self.create_exchange(self._topic_exchange, ExchangeTypes.Topic)
        # Create a queue. Set default idle expiration time to 5 mins
        self._queue_name = self.create_queue(
            queue_size=self._queue_size,
            message_ttl=self._message_ttl,
            overflow_behaviour=self._overflow,
            expires=300000)
        # Bind queue to the Topic exchange
        self.bind_queue(self._topic_exchange, self._queue_name, self._topic)
        self._last_msg_ts = None
        self._msg_freq_fifo = deque(maxlen=self.FREQ_CALC_SAMPLES_MAX)
        self._hz = 0
        self._sem = Semaphore()

    @property
    def hz(self):

        return self._hz

    def run(self):

        self._consume()

    def run_threaded(self):

        self.loop_thread = Thread(target=self.run)
        self.loop_thread.daemon = True
        self.loop_thread.start()

    def close(self):
        if self._channel.is_closed:
            self.logger.info('Invoked close() on an already closed channel')
            return False
        self.delete_queue(self._queue_name)
        super(SubscriberSync, self).close()

    def _consume(self, reliable=False):

        self._channel.basic_consume(
            self._queue_name,
            self._on_msg_callback_wrapper,
            exclusive=False,
            auto_ack=(not reliable))
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt as exc:
            # Log error with traceback
            self.logger.error(exc, exc_info=True)

    def _on_msg_callback_wrapper(self, ch, method, properties, body):
        try:
            msg = self._deserialize_data(body)
        except Exception:
            self.logger.error("Could not deserialize data", exc_info=True)
            # Do not invoke the onmessage callback
            return

        self._sem.acquire()
        self._calc_msg_frequency()
        self._sem.release()

        if self.onmessage is not None:
            meta = {'channel': ch, 'method': method, 'properties': properties}
            self.onmessage(msg, meta)

    def _calc_msg_frequency(self):
        ts = time.time()
        if self._last_msg_ts is not None:
            diff = ts - self._last_msg_ts
            if diff < 10e-3:
                self._last_msg_ts = ts
                return
            else:
                hz = 1.0 / float(diff)
                self._msg_freq_fifo.appendleft(hz)
                hz_list = [s for s in self._msg_freq_fifo if s != 0]
                _sum = sum(hz_list)
                self._hz = _sum / len(hz_list)
        self._last_msg_ts = ts

    def _deserialize_data(self, data):


        return json.loads(data)
