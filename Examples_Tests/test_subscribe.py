from amqp_protocol import amqpbase
from amqp_protocol import subscriber
import time
import json

def callback(msg, meta):
    channel = meta['channel']
    method = meta['method']
    props = meta['properties']
    print('[*] - Channel={}'.format(channel))
    print('[*] - Method={}'.format(method))
    print('[*] - Properties={}'.format(props))
    print('[*] - Data -->')
    print(json.dumps(msg, indent=2))

if __name__ == '__main__':
    hz = 2
    host = 'localhost'
    port = '5672'
    vhost = '/'
    username = 'guest'
    password = 'guest'
    topic = "task1.numbers"
    debug = True
    queue_size = 100
    data = {'aris':10}

    sub = subscriber.SubscriberSync(
        topic, on_message=callback,
        connection_params=amqpbase.ConnectionParameters(
            host=host, port=port, vhost=vhost),
        queue_size=queue_size,
        creds=amqpbase.Credentials(username, password),
        debug=debug
    )
    sub.run_threaded()
    while True:
        try:
            time.sleep(0.01)
        except KeyboardInterrupt:
            break