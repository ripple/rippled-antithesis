import argparse
import distro
import logging
import os
import time
import requests
import socket
import sys
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import start_http_server

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper

log = log_helper.get_logger()
logging.info("")


class PrometheusMetricCollector(object):
    PUSH_GATEWAY_SERVER = "http://172.16.0.69:9091"  # public: 34.222.118.252

    JOB_NAME = "custom_exporter"
    METRIC_HELP_NOTE = "rippled automation metrics"
    KEEP_CONNECTION_ALIVE = None
    CONNECTION_STOP_MSG = "STOP"
    KEY_LABEL_DELIMITER = "/"
    SERVER_HOST = "localhost"
    SERVER_PORT = 8000  # HTTP server endpoint port
    SOCKET_PORT = 65432  # Port to listen on from client
    INSTANCE_NAME = '-'.join(item for item in distro.linux_distribution() if item)


    def __init__(self):
        self.metrics = {}
        self.labels_key_value = {}

    def initilize_metrics_collection(self):
        """
        Initialize metric collector, starting prometheus target (pull endpoint)
        """
        try:
            start_http_server(PrometheusMetricCollector.SERVER_PORT)
            log.debug("Started HTTP Server on {}:{}".format(PrometheusMetricCollector.SERVER_HOST,
                                                            PrometheusMetricCollector.SERVER_PORT))
            REGISTRY.register(self)
        except OSError as e:
            return

    def parse_data(self, data):
        """
        Parse data sent from the client stream
        @param data: data to be parsed and sent to the listener socket
        @return key: key part of the metric
        @return val: value part of the metric
        """
        try:
            key, value = data.split(':')
            if not value:
                raise Exception("Value missing in <key:value>")
        except Exception as e:
            raise ValueError("Error: Pass metric as <key:value>")

        return key.strip(), value

    def collect(self):
        """
        Method to feed data as prometheus scrapes for metrics
        """
        for key, value in self.metrics.items():
            if self.metrics[key] is not None:
                if self.labels_key_value:
                    label_str = ','.join(
                        "{}:{}".format(label_key, label_value) for label_key, label_value in
                        self.labels_key_value.items())
                    log.info("{}{{{}}} {}".format(key, label_str, value))
                    g = GaugeMetricFamily(key, PrometheusMetricCollector.METRIC_HELP_NOTE,
                                          labels=self.labels_key_value.keys())
                    g.add_metric([label_value for label_key, label_value in self.labels_key_value.items()], value)
                    self.metrics[key] = None
                    self.labels_key_value = {}
                else:
                    log.info("{} {}".format(key, value))
                    g = GaugeMetricFamily(key, PrometheusMetricCollector.METRIC_HELP_NOTE)
                    g.add_metric([], value)
                    self.metrics[key] = None
                yield g

    def push_metric_to_gateway(self, push_gateway_server, metric, labels=None):
        """
        Method to support variable endpoints (host with changing client IPs, like CI runners) using push gateway
        @param push_gateway_server: push gateway server
        @param metric: message to be parsed and sent to the push gateway
        """
        key, value = self.parse_data(metric)
        data = '{} {}\n'.format(key, value)

        url = '{}/metrics/job/{}/instance/{}'.format(push_gateway_server, PrometheusMetricCollector.JOB_NAME,
                                                     PrometheusMetricCollector.INSTANCE_NAME)
        if labels:
            label_key_values = labels.split(',')
            for label_key_value in label_key_values:
                label_key, label_value = self.parse_data(label_key_value)
                url += "/{}/{}".format(label_key, label_value)

            label_str = ','.join(
                "{}:{}".format(label_key_value.split(':')[0], label_key_value.split(':')[1]) for label_key_value in
                label_key_values)
            log.info("{}{{{}}} {}".format(key, label_str, value))
        else:
            log.info("{} {}".format(key, value))

        response = requests.post(url=url, data=data)
        time.sleep(20)
        response = requests.delete(url=url)

    def listen(self):
        """
        Socket open to listen to data, that can be pushed to prometheus
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((PrometheusMetricCollector.SERVER_HOST, PrometheusMetricCollector.SOCKET_PORT))
            s.listen()

            PrometheusMetricCollector.KEEP_CONNECTION_ALIVE = True
            while PrometheusMetricCollector.KEEP_CONNECTION_ALIVE:
                conn, addr = s.accept()
                with conn:
                    log.info("\nConnected by: ".format(addr))
                    while True:
                        data = conn.recv(1024)
                        data_str = data.decode('utf-8')

                        if data_str:
                            log.info("Received: {}".format(data_str))
                            if data_str == PrometheusMetricCollector.CONNECTION_STOP_MSG:
                                PrometheusMetricCollector.KEEP_CONNECTION_ALIVE = False
                            else:
                                if PrometheusMetricCollector.KEY_LABEL_DELIMITER in data_str:
                                    metric = data_str.split(PrometheusMetricCollector.KEY_LABEL_DELIMITER)[0]
                                    labels = data_str.split(PrometheusMetricCollector.KEY_LABEL_DELIMITER)[1]
                                else:
                                    metric = data_str
                                    labels = None

                                try:
                                    key, value = metric.split(':')
                                except Exception as e:
                                    log.error("Error: {}".format(e))

                                if key and value is not None:
                                    log.info("{} {}".format(key, value))
                                    self.metrics[key] = value

                                    if labels:
                                        label_key_values = labels.split(',')
                                        for label_key_value in label_key_values:
                                            key, value = self.parse_data(label_key_value)
                                            self.labels_key_value[key] = value

                        else:
                            break

    def send_data(self, msg, labels=None):
        """
        send data to the listening socket
        @param msg: message to be parsed and sent to the stream
        @param labels: Optional labels like "release:1.8,version=beta"
        """
        if msg == PrometheusMetricCollector.CONNECTION_STOP_MSG:
            send_msg = PrometheusMetricCollector.CONNECTION_STOP_MSG
            log.info("Pushing message to STOP listener")
        else:
            key, value = self.parse_data(msg)
            send_msg = "{}:{}".format(key, str(value))

            if labels:
                send_msg = "{}{}{}".format(send_msg, PrometheusMetricCollector.KEY_LABEL_DELIMITER, labels)

                label_str = ','.join(
                    "{}:{}".format(label_key, label_value) for label_key, label_value in self.labels_key_value.items())
                log.info("Pushing metric {}{{{}}} {}".format(key, label_str, value))
            else:
                log.info("Pushing metric {} {}".format(key, value))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PrometheusMetricCollector.SERVER_HOST, PrometheusMetricCollector.SOCKET_PORT))
            s.sendall(bytes(send_msg, encoding='utf-8'))

    def send_metric(self, metric, labels=None, push_gateway_mode=False):
        """
        Generic method to send metric
        @param metric: key:value in metric
        @param labels: Optional labels like "release:1.8,version=beta"
        @param push_gateway_mode: forcefully use push gateway
        """
        # Find if this script is running in docker
        path = '/proc/self/cgroup'
        docker_run = (os.path.exists('/.dockerenv') or
                      os.path.isfile(path) and any('docker' in line for line in open(path)))

        key, value = self.parse_data(metric)
        try:
            if isinstance(value, str):
                value = int(value)
        except Exception as e:
            return

        if docker_run or push_gateway_mode:
            log.debug("Pushing metric to gateway server: {}".format(PrometheusMetricCollector.PUSH_GATEWAY_SERVER))
            self.push_metric_to_gateway(PrometheusMetricCollector.PUSH_GATEWAY_SERVER,
                                        "{}:{}".format(key, value), labels=labels)
        else:
            log.debug("Pushing metric to endpoint: {}:{}".format(PrometheusMetricCollector.SERVER_HOST,
                                                                 PrometheusMetricCollector.SERVER_PORT))

            self.metrics[key] = value
            if labels:
                label_key_values = labels.split(',')
                for label_key_value in label_key_values:
                    label_key, label_value = self.parse_data(label_key_value)
                    self.labels_key_value[label_key] = label_value


def main(metric, labels, listen_mode=False, stop_mode=False, push_gateway_server=None):
    cc = PrometheusMetricCollector()
    if listen_mode:
        cc.initilize_metrics_collection()
        cc.listen()
    elif stop_mode:
        cc.send_data(PrometheusMetricCollector.CONNECTION_STOP_MSG)
    elif metric:
        if push_gateway_server:
            cc.push_metric_to_gateway(push_gateway_server, metric, labels)
        else:
            cc.send_data(metric, labels)
    else:
        raise Exception("Missing parameter")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--listen', help="Start rippled automation exporter in listen mode",
                        action="store_true", default=False)
    parser.add_argument('--stop', help="Stop rippled automation exporter from listen mode",
                        action="store_true", default=False)
    parser.add_argument('--sendMetric', help="Add metric <key:value>", default=None)
    parser.add_argument('--labels', help="Optional labels like release:1.8,version=beta", default=None)
    parser.add_argument('--pushGatewayServer',
                        help="Push gateway server (eg. {})".format(PrometheusMetricCollector.PUSH_GATEWAY_SERVER))

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(1)
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_arguments()
    main(args.sendMetric, args.labels, args.listen, args.stop, args.pushGatewayServer)
