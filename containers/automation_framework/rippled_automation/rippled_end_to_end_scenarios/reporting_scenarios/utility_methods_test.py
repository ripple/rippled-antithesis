#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
from ..utils import helper

ignore_keys = ['random', '__len__', 'warnings']


def json_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="json",
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="json",
                                                              ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


def ping_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="ping",
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="ping",
                                                              ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


def random_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="random",
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="random",
                                                              ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


if __name__ == "__main__":
    json_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    ping_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    random_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    print("Finished")
