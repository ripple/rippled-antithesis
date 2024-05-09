#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
import time
import json
from ..utils import helper
from ..utils import log_helper
from ..utils import test_validator

ignore_keys = ['warnings', 'ledger_index', '__len__', 'ledger_hash', 'ledger_index_max', 'ledger_index_min',
               'used_postgres']


def test_account_channel(hostname="localhost", reporting_server_host="localhost"):
    # Setup a connection to the rippled_regular server

    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    reporting_server = RippledTest(reporting_server_host)
    rippled_server = RippledTest(host)

    # Create and fund account 1
    account_1 = reporting_server.create_account(fund=True, amount=400000000)
    time.sleep(4)
    # Adding regular key to the account
    reporting_server.add_regular_key_to_account(account_1)
    time.sleep(4)

    # Create and fund account 2
    account_2 = reporting_server.create_account(fund=True, amount=400000000)
    time.sleep(4)

    for i in range(20):
        print(i)
        response = reporting_server.execute_transaction(method="submit",
                                                        secret=account_1._regular_key_seed,
                                                        TransactionType="PaymentChannelCreate",
                                                        Account=account_1.account_id,
                                                        Destination=account_2.account_id,
                                                        Amount=1,
                                                        SettleDelay=80,
                                                        PublicKey=account_1.public_key_hex)

    # PaymentChannelClaim
    time.sleep(10)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="account_channels",
                                                          account=account_1.account_id,
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="account_channels",
                                                              account=account_1.account_id,
                                                              ledger_index="validated")

    helper.compare_dict(channels_rippled, channels_reporting, ignore_keys)
    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))
    # assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))

    # Assert limit as 10
    channels_rippled = rippled_server.execute_transaction(method="account_channels",
                                                          account=account_1.account_id,
                                                          limit=10,
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="account_channels",
                                                              account=account_1.account_id,
                                                              limit=10,
                                                              ledger_index="validated")
    helper.compare_dict(channels_rippled, channels_reporting, ignore_keys)
    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))
    # assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))

    # Assert limit as 20
    channels_rippled = rippled_server.execute_transaction(method="account_channels",
                                                          account=account_1.account_id,
                                                          limit=20,
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="account_channels",
                                                              account=account_1.account_id,
                                                              limit=20,
                                                              ledger_index="validated")
    helper.compare_dict(channels_rippled, channels_reporting, ignore_keys)
    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))
    # assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def test_account_currencies():
    pass


def test_account_info(hostname="localhost", reporting_server_host="localhost"):
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Create and fund account 1
    account_1 = reporting_server.create_account(fund=True, amount=400000000)
    time.sleep(4)
    # Adding regular key to the account
    reporting_server.add_regular_key_to_account(account_1)
    time.sleep(4)

    # Create and fund account 2
    account_2 = reporting_server.create_account(fund=True, amount=40000000)
    time.sleep(4)

    for i in range(20):
        print(i)
        response = reporting_server.execute_transaction(method="submit",
                                                        secret=account_1._regular_key_seed,
                                                        TransactionType="PaymentChannelCreate",
                                                        Account=account_1.account_id,
                                                        Destination=account_2.account_id,
                                                        Amount=10,
                                                        SettleDelay=80,
                                                        PublicKey=account_1.public_key_hex)

    # PaymentChannelClaim
    time.sleep(20)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="account_info",
                                                          account=account_1.account_id,
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="account_info",
                                                              account=account_1.account_id,
                                                              ledger_index="validated")

    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))


def test_account_lines():
    pass


def test_account_objects(hostname="localhost", reporting_server_host="localhost"):
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Create and fund account 1
    account_1 = reporting_server.create_account(fund=True, amount=400000000)
    time.sleep(4)
    # Adding regular key to the account
    reporting_server.add_regular_key_to_account(account_1)
    time.sleep(4)

    # Create and fund account 2
    account_2 = reporting_server.create_account(fund=True, amount=40000000)
    time.sleep(4)

    for i in range(20):
        print(i)
        response = reporting_server.execute_transaction(method="submit",
                                                        secret=account_1._regular_key_seed,
                                                        TransactionType="PaymentChannelCreate",
                                                        Account=account_1.account_id,
                                                        Destination=account_2.account_id,
                                                        Amount=10,
                                                        SettleDelay=80,
                                                        PublicKey=account_1.public_key_hex)

    # PaymentChannelClaim
    time.sleep(10)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="account_objects",
                                                          account=account_1.account_id,
                                                          ledger_index="validated")

    channels_reporting = reporting_server.execute_transaction(method="account_objects",
                                                              account=account_1.account_id,
                                                              ledger_index="validated")

    helper.compare_dict(channels_rippled, channels_reporting, ignore_keys)
    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))
    # assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def test_account_offers(hostname="localhost", reporting_server_host="localhost"):
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    reporting_server = RippledTest(reporting_server_host)

    # Create and fund account 1
    account_1 = reporting_server.create_account()

    # Create and fund account 1
    account_2 = reporting_server.create_account()

    # Sleep for one ledger close to confirm account creation
    time.sleep(9)
    for i in range(20):
        print(i)
        response = reporting_server.execute_transaction(method="submit",
                                                        secret=account_1.master_seed,
                                                        TransactionType="OfferCreate",
                                                        Account=account_1.account_id,
                                                        TakerGets=i,
                                                        TakerPays={"currency": "GKO",
                                                                   "issuer": account_2.account_id,
                                                                   "value": "2"}
                                                        )
        # PaymentChannelClaim
        time.sleep(10)

        # Assert default value
        channels_rippled = rippled_server.execute_transaction(method="account_offers",
                                                              account=account_1.account_id,
                                                              ledger_index="validated")

        channels_reporting = reporting_server.execute_transaction(method="account_offers",
                                                                  account=account_1.account_id,
                                                                  ledger_index="validated")

        helper.compare_dict(channels_rippled, channels_reporting, ignore_keys)
        assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))
        # assert (json.dumps(channels_rippled, sort_keys=True) == json.dumps(channels_reporting, sort_keys=True))


def test_account_tx(hostname="localhost", reporting_server_host="localhost"):
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    reporting_server_host = "http://" + str(reporting_server_host) + ":51234/"
    rippled_server = RippledTest(host)
    reporting_server = RippledTest(reporting_server_host)

    # Create and fund account 1
    account_1 = reporting_server.create_account(fund=True, amount=400000000)
    time.sleep(4)
    # Adding regular key to the account
    reporting_server.add_regular_key_to_account(account_1)
    time.sleep(4)

    # Create and fund account 2
    account_2 = reporting_server.create_account(fund=True, amount=40000000)
    time.sleep(4)

    # for i in range(1):
    #     print(i)
    #     response = reporting_server.execute_transaction(method="submit",
    #                                               secret=account_1.master_seed,
    #                                               TransactionType="Payment",
    #                                               Flags="2147483648",
    #                                               Account=account_1.account_id,
    #                                               Destination=account_2.account_id,
    #                                               Amount=10)
    #
    # # PaymentChannelClaim
    # time.sleep(20)

    # Assert default value
    channels_rippled = rippled_server.execute_transaction(method="account_tx",
                                                          account=account_1.account_id,
                                                          ledger_index="validated",
                                                          ledger_index_min=-1)

    channels_reporting = reporting_server.execute_transaction(method="account_tx",
                                                              account=account_1.account_id,
                                                              ledger_index="validated",
                                                              ledger_index_min=-1)
    assert (helper.compare_dict(channels_rippled, channels_reporting, ignore_keys))

    def test_gateway_balances():
        pass

    def test_noripple_check():
        pass


if __name__ == "__main__":
    # test_account_channel(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    # test_account_info(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    # test_account_objects(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    test_account_tx(hostname='10.30.97.222', reporting_server_host='10.30.96.163')

    # test_account_offers(hostname='10.30.97.222', reporting_server_host='10.30.96.163')

    print("Passed")
