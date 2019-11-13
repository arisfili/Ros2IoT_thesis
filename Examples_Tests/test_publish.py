from amqp_protocol import amqpbase
from amqp_protocol import publisher
from amqp_protocol import rate

if __name__ == '__main__':
    hz = 2
    host = 'localhost'
    port = '5672'
    vhost = '/'
    username = "aris"
    password = 'aris1993'
    topic = 'test'
    debug = True

    data = {'aris':10}

    pub = publisher.PublisherSync(
        topic,
        connection_params=amqpbase.ConnectionParameters(
            host=host, port=port, vhost=vhost),
        creds=amqpbase.Credentials(username, password),
        debug=debug)

    rate = rate.Rate(hz)
    while True:
        # Publish once
        pub.publish(data,thread_safe=True)
        rate.sleep()