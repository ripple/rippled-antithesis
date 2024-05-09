from custom_metric_exporter import PrometheusMetricCollector
from random import randrange
import time

"""
Demo file to send metric to prometheus server
In this example, metric "random_number" is repeatedly generated and sent the localhost endpoint, 
which prometheus scrapes 
"""

if __name__ == '__main__':
    prometheus_handle = PrometheusMetricCollector()
    prometheus_handle.initilize_metrics_collection()

    while True:
        metric = "{}:{}".format("random_number", randrange(10))
        print("metric -> {}".format(metric))
        prometheus_handle.send_metric(metric=metric, labels="version:1.8,rel:beta")
        time.sleep(5)