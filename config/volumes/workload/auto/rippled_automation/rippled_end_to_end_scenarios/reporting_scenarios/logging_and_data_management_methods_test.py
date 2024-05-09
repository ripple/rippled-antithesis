#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
import time
import json


def can_delete_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="can_delete",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="can_delete",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def crawl_shards_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="crawl_shards",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="crawl_shards",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def download_shard_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="download_shard",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="download_shard",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def ledger_cleaner_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="ledger_cleaner",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="ledger_cleaner",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def ledger_request_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="ledger_request",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="ledger_request",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def log_level_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="log_level",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="log_level",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def logrotate_test(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="logrotate",
                                                          ledger_index="validated")

    channels_reporting = rippled_server.execute_transaction(method="logrotate",
                                                            ledger_index="validated")

    assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


if __name__ == "__main__":
    can_delete_test()
    crawl_shards_test()
    download_shard_test()
    ledger_cleaner_test()
    ledger_request_test()
    log_level_test()
    logrotate_test()
