import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


def test_transaction_entry(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"],
            "ledger_index": tx_response["ledger_index"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="transaction_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="transaction_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_transaction_entry_with_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"],
            "ledger_index": tx_response["ledger_index"],
            "api_version": 2
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="transaction_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="transaction_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_transaction_entry_without_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": destination_account.account_id,
                "value": "2"
            },
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="notYetImplemented")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="transaction_entry")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4551


def test_transaction_entry_with_unfound_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": destination_account.account_id,
                "value": "2"
            },
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": "CA5EA49D092C558E5DE3209B7BC7E8DAE50355C41B6BE737C4ED35300B6017B2",
            "ledger_index": tx_response["ledger_index"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="transactionNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="transactionNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_transaction_entry_without_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response,
                               method="transaction_entry", response_result="fieldNotFoundTransaction")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response,
                               method="transaction_entry", response_result="fieldNotFoundTransaction")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_transaction_entry_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": destination_account.account_id,
                "value": "2"
            },
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"],
            "ledger_index": rippled_server.ledger_current() + 100
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_transaction_entry_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": destination_account.account_id,
                "value": "2"
            },
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"],
            "ledger_hash": "E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="transaction_entry", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
