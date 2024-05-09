import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_account_lines(fx_rippled):
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

    response = rippled_server.get_account_lines(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_peer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    response = rippled_server.get_account_lines(account_1.account_id, peer=account_2.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3],
                               method="account_lines")
    assert len(response["lines"]) == 1, "Peer is not filtering the lines"

    clio_response = clio_server.get_account_lines(account_1.account_id, peer=account_2.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, account_3],
                               method="account_lines")
    assert len(clio_response["lines"]) == 1, "Peer is not filtering the lines"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_ignore_default_true(fx_rippled):
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

    rippled_response1 = rippled_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not rippled_response1["lines"], "account_lines found"
    clio_response1 = clio_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not clio_response1["lines"], "account_lines found"

    assert (helper.compare_dict(rippled_response1, clio_response1,
                                ignore=constants.CLIO_IGNORES))

    rippled_response2 = rippled_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)
    assert rippled_response2["lines"], "account_lines not found"
    clio_response2 = clio_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)
    assert clio_response2["lines"], "account_lines not found"

    assert helper.compare_dict(rippled_response2, clio_response2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    rippled_response1 = rippled_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not rippled_response1["lines"], "account_lines found"
    clio_response1 = clio_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not clio_response1["lines"], "account_lines found"

    assert (helper.compare_dict(rippled_response1, clio_response1,
                                ignore=constants.CLIO_IGNORES))

    rippled_response2 = rippled_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)
    assert rippled_response2["lines"], "account_lines not found"
    clio_response2 = clio_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)
    assert clio_response2["lines"], "account_lines not found"

    assert helper.compare_dict(rippled_response2, clio_response2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_ignore_default_false(fx_rippled):
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

    rippled_response1 = rippled_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not rippled_response1["lines"], "account_lines found"
    clio_response1 = clio_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)
    assert not clio_response1["lines"], "account_lines found"

    assert helper.compare_dict(rippled_response1, clio_response1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    rippled_response1 = rippled_server.get_account_lines(account_1.account_id, ignore_default=False, verbose=False)
    assert rippled_response1["lines"], "account_lines not found"
    clio_response1 = clio_server.get_account_lines(account_1.account_id, ignore_default=False, verbose=False)
    assert clio_response1["lines"], "account_lines not found"

    assert helper.compare_dict(rippled_response1, clio_response1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True, amount="210000000")

    currency_list = ["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
                     "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
                     "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
                     "COP", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD",
                     "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "GBP", "GEL", "GGP", "GHS",
                     "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
                     "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
                     "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT",
                     "ZWD", "ZAR"]

    for currency in currency_list:
        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_2.account_id,
                "LimitAmount": {
                    "currency": currency,
                    "issuer": account_1.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
            },
            "secret": account_2.master_seed
        }

        create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_lines(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_lines(account_1.account_id, limit=40)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2], method="account_lines")

    clio_response_1 = clio_server.get_account_lines(account_1.account_id, limit=40)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2], method="account_lines")

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_lines(account_1.account_id, marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2], method="account_lines")

    clio_response_2 = clio_server.get_account_lines(account_1.account_id, marker=clio_response_1["marker"])
    test_validator.verify_test(rippled_server, clio_response_2, accounts=[account_1, account_2], method="account_lines")

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="lines")


def test_account_lines_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_lines(account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="actNotFound",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="actNotFound",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }

    response = rippled_server.execute_transaction(payload, method="account_lines")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams", method="account_lines")

    clio_response = clio_server.execute_transaction(payload, method="account_lines")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams", method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account.account_id, ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="lgrNotFound",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account.account_id,
                                                  ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="lgrNotFound",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account.account_id,
                                                ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="lgrNotFound",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account.account_id,
                                                  ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="lgrNotFound",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_lines(account_id="rH9faf13FVuaLneLSDvTf56TxgLCi1Mzo")
    test_validator.verify_test(rippled_server, response, response_result="actMalformed",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account_id="rH9faf13FVuaLneLSDvTf56TxgLCi1Mzo")
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_non_existent_peer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

    response = rippled_server.get_account_lines(account_1.account_id, peer=account_2.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.get_account_lines(account_1.account_id, peer=account_2.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_malformed_peer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account_1.account_id, peer="rn9GMRi7eaZfGguCtMFjj6dkek8zJZJ5r")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_lines",
                               response_result="actMalformed")

    clio_response = clio_server.get_account_lines(account_1.account_id, peer="rn9GMRi7eaZfGguCtMFjj6dkek8zJZJ5r")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_lines",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_limit_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account_1.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="invalidParams")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account_1.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account_1.account_id, limit=10,
                                                marker="70E84379343469A3697F57361BD0D6337EF675089EA90947953F7DA080F39888,0")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit=10,
                                                  marker="70E84379343469A3697F57361BD0D6337EF675089EA90947953F7DA080F39888,0")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_lines(account_1.account_id, limit=10,
                                                marker="C6B2819404E0AE92B464D791F6EB45E9F40CD69A6F9F3AB77B85EA3A96F5E561")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit=10,
                                                  marker="C6B2819404E0AE92B464D791F6EB45E9F40CD69A6F9F3AB77B85EA3A96F5E561")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams",
                               method="account_lines")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_lines_with_limit_less_than_10(fx_rippled):
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

    response = rippled_server.get_account_lines(account_1.account_id, limit=5)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit=5)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_lines")

    # Server is not required to honor limit value. Clio follows whereas rippled doesn't so there's no comparison.


def test_account_lines_with_limit_greater_than_400(fx_rippled):
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

    response = rippled_server.get_account_lines(account_1.account_id, limit=405)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_lines")

    clio_response = clio_server.get_account_lines(account_1.account_id, limit=405)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_lines")

    # Server is not required to honor limit value. Clio follows whereas rippled doesn't so there's no comparison.
