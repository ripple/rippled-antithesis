import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, test_validator, helper
from . import price_oracle_test_data as test_data

log = log_helper.get_logger()


@pytest.mark.smoke
def test_read_oracle(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_read_oracle_without_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID, uri=None)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_read_oracle_with_invalid_account_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=False)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": bob.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")


def test_read_oracle_with_invalid_owner_document_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": (test_data.DEFAULT_ORACLE_DOCUMENT_ID + 1)
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")


def test_read_oracle_non_existent_instance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")


@pytest.mark.parametrize("account", [None, "", 123, "InvalidAccountAddress"])
def test_read_oracle_malformed_account_inputs(fx_rippled, account):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": account,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedAddress")


@pytest.mark.parametrize("oracle_document_id", ["", "Invalid", -1])
def test_read_oracle_malformed_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedDocumentID")


@pytest.mark.parametrize("oracle_document_id", [None, 1.2])
def test_read_oracle_invalid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")


@pytest.mark.parametrize("oracle_document_id", ["1", 0])
def test_read_oracle_valid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": oracle_document_id,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_read_oracle_without_account_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedRequest")


def test_read_oracle_without_oracle_document_id_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedRequest")


def test_read_oracle_without_ledger_index_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            }
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_read_oracle_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

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
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
                "TicketSequence": rippled_server.get_ticket_sequence(alice)[0]
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])
