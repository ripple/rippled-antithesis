import pytest
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, test_validator
from rippled_automation.rippled_end_to_end_scenarios.utils import ctid

log = log_helper.get_logger()


@pytest.mark.smoke
def test_ctid(fx_rippled):
    server = fx_rippled["rippled_server"]

    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    response = server.make_payment(gw, alice, "10000000")
    txn_hash = response['tx_json']['hash']
    tx = server.tx(txn_hash)
    txn_ctid = tx['ctid']
    ledger_seq = tx['inLedger']
    decoded_ctid = ctid.decodeCTID(txn_ctid)

    assert ledger_seq == decoded_ctid['ledger_seq']


def test_ctid_in_tx(fx_rippled):
    """
    Making a tx request using the ctid and confirm you get the same response as by txn_hash
    """
    rippled = fx_rippled["rippled_server"]

    gw = rippled.create_account(fund=True)
    alice = rippled.create_account(fund=True)
    rippled.make_payment(gw, alice, "1000")

    payment_response = rippled.make_payment(gw, alice, "1000")
    txn_response = rippled.tx(payment_response['tx_json']['hash'])

    txn_ctid = txn_response['ctid']
    ledger_seq, txn_index, network_id = ctid.decodeCTID(txn_ctid).values()
    payload = {
        "tx_json": {
            "ctid": txn_ctid
        }
    }
    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    assert ctid_response == txn_response
    test_validator.verify_test(rippled, ctid_response, method='tx')


def test_ctid_blank(fx_rippled):
    """
    Making a tx request using the ctid field but it's empty
    """
    rippled = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "ctid": ""
        }
    }

    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled, ctid_response, method='tx', response_result='invalidParams')


def test_ctid_malformed(fx_rippled):
    """
    Making a tx request using a nonsense ctid and confirm error is returned
    """

    rippled = fx_rippled["rippled_server"]
    payload = {
        "tx_json": {
            "ctid": "badctid"
        }
    }

    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled, ctid_response, method='tx', response_result='invalidParams')


def test_ctid_correct_but_non_existent(fx_rippled):
    """
    Making a tx request using syntactically valid but nonexistent CTID returns an error
    """
    rippled = fx_rippled["rippled_server"]
    ledger_index = int(rippled.get_last_closed_ledger_index())
    number_of_txns = len(rippled.get_ledger_transactions(ledger_index=ledger_index))
    bad_txn_index = number_of_txns + 1
    network_id = rippled.get_network_id()
    non_existent_ctid = ctid.encodeCTID(ledger_index, bad_txn_index, network_id)

    payload = {
        "tx_json": {
            "ctid": non_existent_ctid
        }
    }

    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    log.info(ctid_response)
    test_validator.verify_test(rippled, ctid_response, method='tx', response_result='txnNotFound')


#  https://github.com/XRPLF/rippled/issues/4735
def test_ctid_wrong_network_id(fx_rippled):
    """
    Making a tx request using an incorrect network_id.
    Incorrect in that the network ID is wrong so the txn should not be found.
    If the network this test is run on is >1024, the response will be "wrong network"
    """
    rippled = fx_rippled["rippled_server"]

    gw = rippled.create_account(fund=True)
    alice = rippled.create_account(fund=True)

    response = rippled.make_payment(gw, alice, "10000000")
    txn_hash = response['tx_json']['hash']
    tx = rippled.tx(txn_hash)
    ledger_seq = tx['inLedger']
    tx_index = tx["meta"]["TransactionIndex"]
    network_id = 1
    non_existent_ctid = ctid.encodeCTID(ledger_seq, tx_index, network_id)

    payload = {
        "tx_json": {
            "ctid": non_existent_ctid
        }
    }

    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled, ctid_response, method='tx', response_result='unknown')


def test_ctid_with_lowercase_ctid(fx_rippled):
    """
    tx method with ctid with lowercase letters
    """
    rippled = fx_rippled["rippled_server"]

    gw = rippled.create_account(fund=True)
    alice = rippled.create_account(fund=True)
    rippled.make_payment(gw, alice, "1000")

    payment_response = rippled.make_payment(gw, alice, "1000")
    txn_response = rippled.tx(payment_response['tx_json']['hash'])

    txn_ctid = txn_response['ctid']
    ledger_seq, txn_index, network_id = ctid.decodeCTID(txn_ctid).values()
    payload = {
        "tx_json": {
            "ctid": txn_ctid.lower()
        }
    }
    # Error response may change: https://github.com/XRPLF/rippled/issues/4776
    ctid_response = rippled.execute_transaction(payload=payload, method="tx", verbose=True)
    test_validator.verify_test(rippled, ctid_response, method='tx', response_result='invalidParams')
