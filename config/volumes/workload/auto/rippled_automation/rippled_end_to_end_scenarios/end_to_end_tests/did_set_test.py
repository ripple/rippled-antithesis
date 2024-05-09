import pytest

from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_did_set_all_params(fx_rippled):
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


def test_did_set_with_no_params(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            # "Data": "A1B1",
            # "DIDDocument": "A1B1",
            # "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temEMPTY_DID")


def test_did_set_with_invalid_param(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1",
            "CustomField": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_did_set_with_only_data(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            # "DIDDocument": "A1B1",
            # "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_only_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            # "Data": "A1B1",
            "DIDDocument": "A1B1",
            # "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_only_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            # "Data": "A1B1",
            # "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_no_data(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            # "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_no_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            # "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_no_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            # "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_on_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=False)

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
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActNotFound")


@pytest.mark.longrun
def test_did_set_and_delete_account(fx_rippled):
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
    log.info("DID object deleted")


def test_did_set_with_uri_more_than_256_bytes(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    long_string = "A" * 260
    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": long_string.encode('utf-8').hex()
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_did_set_with_data_more_than_256_bytes(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    long_string = "A" * 260
    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": long_string.encode('utf-8').hex(),
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_did_set_with_did_document_more_than_256_bytes(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    long_string = "A" * 260
    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": long_string.encode('utf-8').hex(),
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_did_set_with_empty_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_data_only(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_uri_and_data(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "",
            "DIDDocument": "A1B1",
            "URI": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_uri_and_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "",
            "URI": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_data_and_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "",
            "DIDDocument": "",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_did_set_with_empty_all_params(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "",
            "DIDDocument": "",
            "URI": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temEMPTY_DID")


def test_did_set_with_non_hex_data(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "XYZ",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_did_set_with_non_hex_did_document(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "XYZ",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_did_set_with_non_hex_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "XYZ"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_did_set_on_account_with_exact_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True,
                                          amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE)))

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
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINSUFFICIENT_RESERVE")


def test_did_set_on_account_with_just_base_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True, amount=str(int(constants.BASE_RESERVE)))

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
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINSUFFICIENT_RESERVE")


def test_did_set_on_account_with_deposit_auth_enabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=alice)

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


def test_did_set_and_enable_clawback(fx_rippled):
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


def test_did_set_with_regular_key_when_master_key_disabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    rippled_server.add_regular_key_to_account(alice)  # Generate regular key
    rippled_server.disable_master_key(alice)  # Disable master key

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])
