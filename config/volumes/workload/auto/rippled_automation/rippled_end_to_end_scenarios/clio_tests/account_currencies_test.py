import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_account_currencies(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "INR",
                "issuer": account_2.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_currencies(account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_currencies")

    clio_response = clio_server.get_account_currencies(account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload, method="account_currencies")
    test_validator.verify_test(rippled_server, response, method="account_currencies", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_currencies")
    test_validator.verify_test(clio_server, clio_response, method="account_currencies", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_currencies(account)
    test_validator.verify_test(rippled_server, response, response_result="actNotFound", accounts=[account],
                               method="account_currencies")

    clio_response = clio_server.get_account_currencies(account)
    test_validator.verify_test(clio_server, clio_response, response_result="actNotFound", accounts=[account],
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "account": "rp5zYr8M3T6E44AKw1q68gPi4jTgQPi3",
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="account_currencies")
    test_validator.verify_test(rippled_server, response, response_result="actMalformed",
                               method="account_currencies")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_currencies")
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed",
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_malformed_account_and_strict_as_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "account": "rp5zYr8M3T6E44AKw1q68gPi4jTgQPi3",
            "ledger_index": "validated",
            "strict": False
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="account_currencies")
    test_validator.verify_test(rippled_server, response, response_result="actMalformed",
                               method="account_currencies")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_currencies")
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed",
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_and_strict_as_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_currencies(account_1, destination_account=account_2, strict=False)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_currencies")

    clio_response = clio_server.get_account_currencies(account_1, destination_account=account_2, strict=False)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_malformed_strict(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_currencies(account_1, strict="fgh")
    test_validator.verify_test(rippled_server, response, method="account_currencies", accounts=[account_1, account_2])

    clio_response = clio_server.get_account_currencies(account_1, strict="fgh")
    test_validator.verify_test(clio_server, clio_response, method="account_currencies", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_currencies(account,
                                                     ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, response_result="lgrNotFound", accounts=[account],
                               method="account_currencies")

    clio_response = clio_server.get_account_currencies(account,
                                                       ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, response_result="lgrNotFound", accounts=[account],
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_currencies_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_currencies(account,
                                                     ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, response_result="lgrNotFound", accounts=[account],
                               method="account_currencies")

    clio_response = clio_server.get_account_currencies(account,
                                                       ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, response_result="lgrNotFound", accounts=[account],
                               method="account_currencies")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
