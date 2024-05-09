import pytest

from . import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils.validators import did_validator

log = log_helper.get_logger()


@pytest.mark.smoke
@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_all_params_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


def test_did_update_none_on_account_with_all_params_preset(fx_rippled):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temEMPTY_DID")

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_only_uri_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_only_did_document_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_data_and_uri_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_data_and_did_document_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_on_account_with_uri_and_did_document_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "ABC123"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"]])
def test_did_update_with_empty_val_on_account_with_all_params_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = ""

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["Data", "URI", "DIDDocument"]])
def test_did_update_with_empty_val_on_account_with_all_params_preset_negative(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = ""

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temEMPTY_DID")

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_with_more_256_bytes_on_account_with_all_params_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    long_string = "A" * 260
    for param in to_update:
        update_payload["tx_json"][param] = long_string.encode('utf-8').hex()

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


@pytest.mark.parametrize("to_update", [["URI"], ["Data"], ["DIDDocument"], ["Data", "URI"], ["Data", "DIDDocument"], ["URI", "DIDDocument"], ["Data", "URI", "DIDDocument"]])
def test_did_update_with_non_hex_data_on_account_with_all_params_preset(fx_rippled, to_update):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }

    log.info("")
    log.info(f"Updating: {to_update}...")
    for param in to_update:
        update_payload["tx_json"][param] = "XYZ"

    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)


def test_did_update_on_account_with_regular_key_when_master_key_disabled(fx_rippled):
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

    update_payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "ABC123",
            "DIDDocument": "ABC123",
            "URI": "ABC123"
        },
        "secret": alice.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload=update_payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    did_validator.validate_updated_did_object(rippled_server=rippled_server, initial_payload=payload, did_update_response=response)
