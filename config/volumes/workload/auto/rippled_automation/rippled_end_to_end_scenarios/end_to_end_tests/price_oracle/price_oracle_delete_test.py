import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, test_validator
from . import price_oracle_test_data as test_data
from .. import constants

log = log_helper.get_logger()


@pytest.mark.smoke
def test_delete_oracle(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_delete_oracle_without_oracle_document_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_delete_oracle_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActMissing")


def test_delete_oracle_twice(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecNO_ENTRY")


def test_delete_oracle_using_invalid_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=False)

    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], response_result="badSecret")


def test_delete_oracle_using_non_existent_oracle_document_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID + 1
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecNO_ENTRY")


@pytest.mark.parametrize("account", [None, "", 123, "InvalidAccountAddress"])
def test_delete_oracle_malformed_account_inputs(fx_rippled, account):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": account,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActMalformed")


@pytest.mark.parametrize("oracle_document_id", [None, "", "Invalid", -1, 1.2])
def test_delete_oracle_invalid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": oracle_document_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("oracle_document_id", ["1", 0])
def test_delete_oracle_valid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=oracle_document_id)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": oracle_document_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_delete_oracle_multisigned(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry":
                        {
                            "Account": bob.account_id,
                            "SignerWeight": 1
                        }
                }
            ]
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "SigningPubKey": "",
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "account": bob.account_id,
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[alice, bob])


def test_delete_oracle_with_regular_key_when_master_key_disabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    rippled_server.add_regular_key_to_account(alice)  # Generate regular key
    rippled_server.disable_master_key(alice)  # Disable master key

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_delete_oracle_on_account_with_deposit_auth_enabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=alice)

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.longrun
def test_delete_oracle_and_delete_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

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
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])


def test_delete_oracle_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": alice.account_id,
            "Sequence": rippled_server.get_account_sequence(alice),
            "TicketCount": 1
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "TicketSequence": rippled_server.get_ticket_sequence(alice)[0]
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])
