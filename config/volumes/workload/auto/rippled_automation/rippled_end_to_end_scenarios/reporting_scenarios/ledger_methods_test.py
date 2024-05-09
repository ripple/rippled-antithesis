#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
from ..utils import helper

ignore_keys = ['warnings']


def test_ledger_index(hostname, reporting_server_host):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    ledger_rippled = rippled_server.execute_transaction(method="ledger",
                                                        ledger_index="1452683",
                                                        full=True,
                                                        accounts=True,
                                                        transactions=True)

    ledger_reporting = reporting_server.execute_transaction(method="ledger",
                                                            ledger_index="1452683",
                                                            full=True,
                                                            accounts=True,
                                                            transactions=True)

    assert (helper.compare_dict(ledger_rippled, ledger_reporting, ignore_keys))


# FC4FCC31E965909261AAFC5FA44420647211738BAA989DEED9A326569BFAAE92
def test_ledger_hash(hostname, reporting_server_host):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    ledger_rippled = rippled_server.execute_transaction(method="ledger",
                                                        ledger_index="validated",
                                                        )

    ledger_reporting = reporting_server.execute_transaction(method="ledger",
                                                            ledger_index="validated")

    assert (helper.compare_dict(ledger_rippled, ledger_reporting, ignore_keys))


# I have tested these manually but they are very flaky tests since they might choose different ledgers based on timing
#
# def test_ledger_closed(hostname, reporting_server_host):
#     host = "http://" + str(hostname) + ":51234/"
#     reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
#     rippled_server = RippledTest(host)
#     reporting_server = RippledTest(reporting_server_host)
#     pass
#
#
# def test_ledger_current(hostname, reporting_server_host):
#     host = "http://" + str(hostname) + ":51234/"
#     reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
#     rippled_server = RippledTest(host)
#     reporting_server = RippledTest(reporting_server_host)


def test_ledger_data(hostname, reporting_server_host):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)


def test_ledger_entry(hostname, reporting_server_host):
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)


if __name__ == "__main__":
    test_ledger_index(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    print("Finished")
