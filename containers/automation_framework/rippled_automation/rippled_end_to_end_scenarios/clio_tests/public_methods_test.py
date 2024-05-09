import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/RIP-388")
def test_clio_transaction_methods_submit_only_mode(fx_rippled):
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
    response = rippled_server.execute_transaction(payload=payload, method="sign")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    submit_blob_response = rippled_server.submit_blob(response)
    test_validator.verify_test(rippled_server, submit_blob_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    submit_blob_response = clio_server.submit_blob(response)
    test_validator.verify_test(clio_server, submit_blob_response, accounts=[account_1, account_2])


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/RIP-388?filter=-4")
def test_clio_transaction_methods_submit_multisigned(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Generate regular key for account
    rippled_server.add_regular_key_to_account(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.regular_key_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    # accounts for signing txns
    account_3 = rippled_server.create_account()
    account_4 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_2.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_3.account_id,
                        "SignerWeight": 2
                    }
                },
                {
                    "SignerEntry": {
                        "Account": account_4.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        },
        "account": account_3.account_id,
        "secret": account_3.master_seed
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = clio_server.execute_transaction(payload=sign_for_response, method="submit_multisigned")
    test_validator.verify_test(clio_server, multisign_response,
                               accounts=[account_1, account_2])


def test_clio_server_info_methods_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="fee")
    test_validator.verify_test(rippled_server, response, accounts=[], method="fee")

    clio_response = clio_server.execute_transaction(payload=payload, method="fee")
    test_validator.verify_test(clio_server, clio_response, accounts=[], method="fee")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_clio_server_info_methods_manifest(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "public_key": "nHUFE9prPXPrHcG3SkwP1UzAQbSphqyQkQK9ATXLZsfkezhhda3p"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(rippled_server, response, method="manifest")

    clio_response = clio_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(clio_server, clio_response, method="manifest")

    assert helper.compare_dict(response, clio_response,
                               ignore=["details", "manifest"]), "clio response differs from rippled response"


def test_clio_utility_methods_random(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="random")
    test_validator.verify_test(rippled_server, response, accounts=[], method="random")

    clio_response = clio_server.execute_transaction(payload=payload, method="random")
    test_validator.verify_test(clio_server, clio_response, accounts=[], method="random")

    assert helper.compare_dict(response, clio_response, ignore=["random", "validated",
                                                                "warnings"]), "clio response differs from rippled response"


def test_clio_ledger_methods_ledger_closed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_closed")
    test_validator.verify_test(rippled_server, response, method="ledger_closed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_closed")
    test_validator.verify_test(clio_server, clio_response, method="ledger_closed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_clio_ledger_methods_ledger_current(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_current")
    test_validator.verify_test(rippled_server, response, method="ledger_current")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_current")
    test_validator.verify_test(clio_server, clio_response, method="ledger_current")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_clio_utility_methods_ping(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ping")
    test_validator.verify_test(rippled_server, response, method="ping")

    clio_response = clio_server.execute_transaction(payload=payload, method="ping")
    test_validator.verify_test(clio_server, clio_response, method="ping")

    assert helper.compare_dict(response, clio_response,
                               ignore=["role", "unlimited", "warnings"]), "clio response differs from rippled response"


def test_clio_server_info(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_server_info()
    test_validator.verify_test(clio_server, clio_response, method="server_info")
