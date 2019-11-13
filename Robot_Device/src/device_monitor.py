from __future__ import absolute_import, division
import psutil
import socket
import time
import json

from amqp_protocol import amqpbase ,ConnectionParameters,Credentials,PublisherSync


class DeviceStatsDataModel(object):
    __slots__ = [
        'memory', 'cpu', 'disk', 'network', 'temperature', 'battery',
        'processes'
    ]

    def __init__(self):
        self.memory = {
            'used': -1,
            'total': -1,
            'available': -1,
            'free': -1,
            'active': -1,
            'inactive': -1,
            'buffers': -1,
            'cached': -1,
            'shared': -1,
            'percent': -1,
            'units': 'Gb'
        }

        self.cpu = {'num_cores': -1, 'frequency': -1, 'usage': -1}

        self.disk = {}
        self.temperature = {}
        self.battery = {}
        self.processes = {
            'all': [],
            'top3_mem': [],
            'top3_cpu': [],
            'top3_io': []
        }

        self.network = {'connections': [], 'interfaces': []}
        self.network['connections'] = {'tcp': [], 'udp': [], 'unix': []}

    def _to_dict(self):
        """Serialize message object to a dict."""
        return {
            k: getattr(self, k)
            for k in self.__slots__ if not k.startswith('_')
        }

    def _serialize(self):
        json.dumps(self._to_dict())


class DeviceMonitoringMixin(object):
    def __init__(self):
        pass

    def to_gib(self, val_bytes, factor=2**30, suffix=''):
        """ Convert a number of bytes to Gibibytes
            Ex : 1073741824 bytes = 1073741824/2**30 = 1GiB
        """
        return "%0.2f%s" % (val_bytes, suffix)

    def get_network_interfaces(self):
        return psutil.net_if_addrs()

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    def get_hostname(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostname = socket.gethostname()
        s.close()
        return hostname

    def get_cpu_usage(self, percpu=True):
        cpu = {
            'num_cores': psutil.cpu_count(logical=True),
            'frequency': psutil.cpu_freq(percpu=percpu),
            'usage': psutil.cpu_percent(percpu=percpu)
        }
        return cpu

    def get_mem_usage(self):
        memory = psutil.virtual_memory()
        mem = {
            'used': self.to_gib(memory.used, suffix=""),
            'total': self.to_gib(memory.total, suffix=""),
            'available': self.to_gib(memory.available, suffix=""),
            'free': self.to_gib(memory.free, suffix=""),
            'active': self.to_gib(memory.active, suffix=""),
            'inactive': self.to_gib(memory.inactive, suffix=""),
            'buffers': self.to_gib(memory.buffers, suffix=""),
            'cached': self.to_gib(memory.cached, suffix=""),
            'shared': self.to_gib(memory.shared, suffix=""),
            'percent': memory.percent,
            'units': "GB"
        }
        return mem

    def get_disk_usage(self):
        disks = {}
        for device in psutil.disk_partitions():
            # skip mountpoint not actually mounted (like CD drives with no disk on Windows)
            if device.fstype != "":
                usage = psutil.disk_usage(device.mountpoint)
                disks[device.mountpoint] = {
                    'used': self.to_gib(usage.used),
                    'total': self.to_gib(usage.total),
                    'percent': usage.percent
                }
        return disks

    def get_network_connections(self):
        return {
            'tcp': self.get_tcp_connections(),
            'udp': self.get_udp_connections(),
            'unix': self.get_unix_connections()
        }

    def get_tcp_connections(self):
        return psutil.net_connections(kind='tcp')

    def get_udp_connections(self):
        return psutil.net_connections(kind='udp')

    def get_unix_connections(self):
        return psutil.net_connections(kind='unix')

    def get_connections(self):
        return psutil.net_connections(kind='all')

    def get_hw_temp(self):
        return psutil.sensors_temperatures(fahrenheit=False)

    def get_battery(self):
        return psutil.sensors_battery()

    def get_top3_mem_procs(self):
        return [(p.pid, p.info) for p in sorted(
            psutil.process_iter(attrs=['name', 'memory_percent']),
            key=lambda p: p.info['memory_percent'])][-3:]

    def get_top3_cpu_procs(self):
        return [(p.pid, p.info['name'], sum(p.info['cpu_times']))
                for p in sorted(
                    psutil.process_iter(attrs=['name', 'cpu_times']),
                    key=lambda p: sum(p.info['cpu_times'][:2]))][-3:]

    def get_top3_io_procs(self):
        return [(p.pid, p.info['name']) for p in sorted(
            psutil.process_iter(attrs=['name', 'io_counters']),
            key=lambda p: p.info['io_counters'] and
                p.info['io_counters'][:2])][-3:]

    def get_procs(self):
        procs = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'username'])
            except psutil.NoSuchProcess:
                pass
            else:
                procs.append(pinfo)
        return procs


class DeviceMonitoringAgent(DeviceMonitoringMixin):
    connection_params = ConnectionParameters()

    def __init__(self, conn_params, creds, device_id ,*args,**kwargs):
        super(DeviceMonitoringAgent, self).__init__()
        if conn_params is not None:
            self.connection_params = conn_params
        hostname = self.get_hostname()
        # if device_id is None:
        #     device_id = hostname
        self.creds = creds
        self._topic = '{}/{}'.format(device_id, 'stats')
        self._pub_freq = 1  # hz
        self.publisher = PublisherSync(self._topic, connection_params=self.connection_params,
                                       creds=self.creds, debug=True)

    @property
    def freq(self):
        return self._pub_freq

    @freq.setter
    def freq(self, val):
        self._pub_freq = val

    @property
    def topic(self):
        return self._topic

    @topic.setter
    def topic(self, val):
        if isinstance(val, str):
            self._topic = val
        else:
            raise ValueError('Topic must be of type str')

    def start(self):


        try:
            while True:
                msg = DeviceStatsDataModel()
                msg.memory = self.get_mem_usage()
                msg.cpu = self.get_cpu_usage()
                msg.disk = self.get_disk_usage()
                msg.network['connections'] = self.get_network_connections()
                msg.network['interfaces'] = self.get_network_interfaces()
                msg.temperature = self.get_hw_temp()
                msg.battery = self.get_battery()
                msg.processes['all'] = self.get_procs()
                msg.processes['top3_mem'] = self.get_top3_mem_procs()
                msg.processes['top3_cpu'] = self.get_top3_cpu_procs()
                #  msg.processes['top3_io'] = self.get_top3_io_procs()

                self.publisher.publish(msg._to_dict())
                time.sleep(0.5 / self._pub_freq)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    device_name = "ubuntu"
    hz = 2
    host = 'localhost'
    port = '5672'
    vhost = '/'
    username = device_name
    password = 'ubuntu'
    debug = True
    connection_params = amqpbase.ConnectionParameters(
        host=host, port=port, vhost=vhost)
    creds = Credentials(username, password)
    dev = DeviceMonitoringAgent(creds=creds,conn_params=connection_params,device_id=device_name)
    dev.start()



