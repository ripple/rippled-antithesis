import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper, ctid
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


def test_tx(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], binary=True)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")
    assert response["tx"], "Transaction not found"

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], binary=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")
    assert response["tx"], "Transaction not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_binary_true_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], binary=True, api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")
    assert response["tx_blob"], "Transaction not found"

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], binary=True, api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")
    assert response["tx_blob"], "Transaction not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_min_max_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    max_ledger = rippled_server.ledger_current()
    min_ledger = max_ledger - 700

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                 max_ledger=max_ledger)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                   max_ledger=max_ledger)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_unfound_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.tx(tx_id="D433DD46B40C473E42D28665CFE05DE37BBF2B9D2C58E40115D359587A16896E")
    test_validator.verify_test(rippled_server, response, method="tx", response_result="txnNotFound")

    clio_response = clio_server.tx(tx_id="D433DD46B40C473E42D28665CFE05DE37BBF2B9D2C58E40115D359587A16896E")
    test_validator.verify_test(clio_server, clio_response, method="tx", response_result="txnNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_invalid_ledger_index_max_ledger_index_min(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    max_ledger = payment_response["tx_json"]["Sequence"] - 10

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=max_ledger - 10,
                                 max_ledger=max_ledger)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=max_ledger - 10,
                                   max_ledger=max_ledger)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_out_of_range_min_max_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    max_ledger = rippled_server.ledger_current()
    min_ledger = max_ledger - 1100

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                 max_ledger=max_ledger)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx",
                               response_result="excessiveLgrRange")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                   max_ledger=max_ledger)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx",
                               response_result="excessiveLgrRange")

    assert helper.compare_dict(response, clio_response, ignore=["request", "type", "inLedger",
                                                                "warnings"]), "clio response differs from rippled response"


def test_tx_min_ledger_greater_than_max_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    min_ledger = rippled_server.ledger_current()
    max_ledger = min_ledger - 100

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                 max_ledger=max_ledger)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx",
                               response_result="invalidLgrRange")

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], min_ledger=min_ledger,
                                   max_ledger=max_ledger)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="tx",
                               response_result="invalidLgrRange")

    assert helper.compare_dict(response, clio_response, ignore=["inLedger", "type", "request",
                                                                "warnings"]), "clio response differs from rippled response"


def test_tx_with_valid_min_max_ledger_and_invalid_tx(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    max_ledger = rippled_server.ledger_current()
    min_ledger = max_ledger - 700

    response = rippled_server.tx(tx_id="C53ECF838647FA5A4C780377025FEC7999AB4182590510CA461444B207AB74A9",
                                 min_ledger=min_ledger, max_ledger=max_ledger)
    test_validator.verify_test(rippled_server, response, method="tx", response_result="txnNotFound")

    clio_response = clio_server.tx(tx_id="C53ECF838647FA5A4C780377025FEC7999AB4182590510CA461444B207AB74A9",
                                   min_ledger=min_ledger, max_ledger=max_ledger)
    test_validator.verify_test(clio_server, clio_response, method="tx", response_result="txnNotFound")

    assert helper.compare_dict(response, clio_response, ignore=["inLedger", "type", "request",
                                                                "warnings"]), "clio response differs from rippled response"


def test_tx_with_invalid_binary(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], binary="gfh")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], binary="gfh")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_invalid_binary_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"], binary="gfh", api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.tx(tx_id=payment_response["tx_json"]["hash"], binary="gfh", api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # TODO: Uncomment this after Rippled issue: https://github.com/XRPLF/rippled/issues/4543 is fixed


def test_tx_without_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }

    response = rippled_server.execute_transaction(payload, method="tx")
    test_validator.verify_test(rippled_server, response, method="tx", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="tx")
    test_validator.verify_test(clio_server, clio_response, method="tx", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_ctid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="tx")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="tx")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_max_ledger_and_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']
    max_ledger = tx['inLedger']
    min_ledger = max_ledger - 20

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "max_ledger": max_ledger,
            "min_ledger": min_ledger
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="tx")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_unfound_ctid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ctid": "C005523E00000002"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, response_result="txnNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, response_result="txnNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_with_unassociated_network_ctid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice])

    ledger_seq = tx['inLedger']
    tx_index = tx["meta"]["TransactionIndex"]
    network_id = 1
    non_existent_ctid = ctid.encodeCTID(ledger_seq, tx_index, network_id)

    payload = {
        "tx_json": {
            "ctid": non_existent_ctid
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, method='tx', response_result='unknown')

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, method='tx', response_result='unknown')

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_unfound_ctid_with_max_ledger_and_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ctid": "C005523E00000002",
            "max_ledger": 1010900,
            "min_ledger": 1010501
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, response_result="txnNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, response_result="txnNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # assert response["searched_all"], "searched_all is true: {}".format(response)
    # assert clio_response["searched_all"], "searched_all is true: {}".format(clio_response)
    # Issue : https://github.com/XRPLF/rippled/issues/4814


def test_tx_valid_ctid_with_invalid_max_ledger_and_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "max_ledger": 1010900,
            "min_ledger": 1010501
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="tx")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_out_of_range_max_ledger_and_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "max_ledger": 1417108,
            "min_ledger": 1216108
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], response_result="excessiveLgrRange")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], response_result="excessiveLgrRange")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_max_ledger_less_than_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']
    min_ledger = tx['inLedger']
    max_ledger = min_ledger - 20

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "max_ledger": max_ledger,
            "min_ledger": min_ledger
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], response_result="invalidLgrRange")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], response_result="invalidLgrRange")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_invalid_ctid_with_valid_max_ledger_and_min_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    max_ledger = rippled_server.ledger_current()
    min_ledger = max_ledger - 20

    payload = {
        "tx_json": {
            "ctid": "C005523E00000002",
            "max_ledger": max_ledger,
            "min_ledger": min_ledger
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], response_result="txnNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice],  response_result="txnNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_malformed_binary(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "binary": "malformed"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="tx")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_malformed_ctid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ctid": "C005523E0000000"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_tx_ctid_with_lowercase_ctid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid.lower()
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response,  accounts=[gw, alice], response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response,  accounts=[gw, alice])

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4776


def test_tx_ctid_with_ctid_and_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    response = rippled_server.make_payment(gw, alice, "10000000")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    txn_hash = response['tx_json']['hash']

    tx = rippled_server.tx(txn_hash)
    test_validator.verify_test(rippled_server, tx, accounts=[gw, alice], method="tx")

    txn_ctid = tx['ctid']

    payload = {
        "tx_json": {
            "ctid": txn_ctid,
            "transaction": txn_hash
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
