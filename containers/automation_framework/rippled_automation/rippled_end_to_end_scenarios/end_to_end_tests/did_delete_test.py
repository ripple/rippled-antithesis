import pytest

from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_did_delete_did_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_delete_non_did_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecNO_ENTRY")


def test_did_delete_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=False)

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActNotFound")


@pytest.mark.longrun
def test_did_delete_and_delete_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])
    ledger_index = rippled_server.get_did_ledger_index(response, verbose=False)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(alice)

    bob = rippled_server.create_account(fund=True)
    # Delete source account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "secret": alice.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[alice, bob])

    ledger_entry_response = rippled_server.get_ledger_entry(index=ledger_index,
                                                            verbose=False)
    assert ledger_entry_response["error"] == "entryNotFound", "DID not deleted"
    log.info("")
    log.info("As expected, DID doesn't exit")


def test_did_delete_with_regular_key_when_master_key_disabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    rippled_server.add_regular_key_to_account(alice)  # Generate regular key
    rippled_server.disable_master_key(alice)  # Disable master key

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_delete_after_clawback(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    account_set_response = rippled_server.account_set(alice, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    account_set_response = rippled_server.account_set(alice, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[alice])
