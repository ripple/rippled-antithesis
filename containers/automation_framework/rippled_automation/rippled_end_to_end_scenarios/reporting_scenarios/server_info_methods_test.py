#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
import time
import json
from ..utils import helper

ignore_keys = ['status', '__len__', 'job_types']


def fee_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="fee",
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="fee",
                                                              ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


def server_info_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    helper = RippledTest(host)

    # Assert default value
    channels_rippled = helper.execute_transaction(method="server_info",
                                                  ledger_index="validated")

    channels_reporting = helper.execute_transaction(method="server_info",
                                                    ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


# Excluding this from AB testing since the results are expected to be different at the moment
# def server_state_test(hostname="localhost", reporting_server_host="localhost"):
#     host = "http://" + str(hostname) + ":51234/"
#     rippled_server = RippledTest(host)
#
#     # Assert default value
#     channels_rippled = rippled_server.execute_transaction(method="server_state",
#                                                           ledger_index="validated")
#
#     channels_reporting = rippled_server.execute_transaction(method="server_state",
#                                                             ledger_index="validated")
#
#     assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


if __name__ == "__main__":
    fee_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    # server_state_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    server_info_test(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    print("Finished")
