#!/usr/bin/env python
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest
import time
import json
from ..utils import helper

ignore_keys = ['warnings', 'ledger_index', '__len__', 'ledger_hash', 'ledger_index_max', 'ledger_index_min',
               'used_postgres']

'''
No AB testing required but verify by sending this tx to reporting server and make sure it passes

def test_sign(hostname="localhost", reporting_server_host="localhost"):
    pass

def test_sign_for(hostname="localhost", reporting_server_host="localhost"):
    pass


def test_submit():
    pass

def test_submit_multisigned():
    pass
'''

'''
This RPC call us deprecated so not testing it yet but will at the end when I have sometime 
def tx_history():
    pass
'''


def test_transaction_entry(hostname="localhost", reporting_server_host="localhost"):
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

    response = reporting_server.execute_transaction(method="submit",
                                                    secret=account_1._regular_key_seed,
                                                    TransactionType="PaymentChannelCreate",
                                                    Account=account_1.account_id,
                                                    Destination=account_2.account_id,
                                                    Amount=1,
                                                    SettleDelay=80,
                                                    PublicKey=account_1.public_key_hex)
    tx_hash = response['tx_json']['hash']
    # current_ledger = rippled_server.ledger_current()
    # ledger_range = rippled_server.ledger_entry_index(current_ledger - 100)

    # Assert default value
    transaction_rippled = rippled_server.execute_transaction(method="transaction_entry",
                                                             tx_hash=tx_hash,
                                                             ledger_index="validated")

    transaction_reporting = reporting_server.execute_transaction(method="transaction_entry",
                                                                 tx_hash=tx_hash,
                                                                 ledger_index="validated")
    helper.compare_dict(transaction_rippled, transaction_reporting, ignore_keys)


def test_tx_history(hostname="localhost", reporting_server_host="localhost"):
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

    response = reporting_server.execute_transaction(method="submit",
                                                    secret=account_1._regular_key_seed,
                                                    TransactionType="PaymentChannelCreate",
                                                    Account=account_1.account_id,
                                                    Destination=account_2.account_id,
                                                    Amount=1,
                                                    SettleDelay=80,
                                                    PublicKey=account_1.public_key_hex)
    tx_hash = response['tx_json']['hash']
    # current_ledger = rippled_server.ledger_current()
    # ledger_range = rippled_server.ledger_entry_index(current_ledger - 100)

    # Assert default value
    transaction_rippled = rippled_server.execute_transaction(method="tx",
                                                             tx_hash=tx_hash,
                                                             ledger_index="validated")

    transaction_reporting = reporting_server.execute_transaction(method="tx",
                                                                 tx_hash=tx_hash,
                                                                 ledger_index="validated")
    helper.compare_dict(transaction_rippled, transaction_reporting, ignore_keys)


if __name__ == "__main__":
    test_transaction_entry(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    test_tx_history(hostname='10.30.97.222', reporting_server_host='10.30.96.163')
    print("Passed")
