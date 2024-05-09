import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_account_offers(fx_rippled):
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
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_offers(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_offers")

    clio_response = clio_server.get_account_offers(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_account_offers_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True, amount="210000000")
    account_2 = rippled_server.create_account(fund=True)

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
                "TransactionType": "OfferCreate",
                "Account": account_1.account_id,
                "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
                "TakerPays": {
                    "currency": currency,
                    "issuer": account_2.account_id,
                    "value": "2"
                },
            },
            "secret": account_1.master_seed
        }
        offer_create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_offers(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_offers")

    clio_response = clio_server.get_account_offers(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_offers(account_1.account_id, limit=40)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2], method="account_offers")

    clio_response_1 = clio_server.get_account_offers(account_1.account_id, limit=40)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2], method="account_offers")

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_offers(account_1.account_id, marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2], method="account_offers")

    clio_response_2 = clio_server.get_account_offers(account_1.account_id, marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1, account_2], method="account_offers")

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="offers")


def test_account_offers_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_offers(account.account_id,
                                                   ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id,
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_offers(account.account_id,
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_offers(account.account_id)
    test_validator.verify_test(rippled_server, response, method="account_offers", accounts=[account],
                               response_result="actNotFound")

    clio_response = clio_server.get_account_offers(account.account_id)
    test_validator.verify_test(clio_server, clio_response, method="account_offers", accounts=[account],
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }

    response = rippled_server.execute_transaction(payload, method="account_offers")
    test_validator.verify_test(rippled_server, response, method="account_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_offers")
    test_validator.verify_test(clio_server, clio_response, method="account_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_offers(account_id="rpP2JgiMyTF5jR5hLG3xHCPi1knBb1v9c")
    test_validator.verify_test(rippled_server, response, method="account_offers", response_result="actMalformed")

    clio_response = clio_server.get_account_offers(account_id="rpP2JgiMyTF5jR5hLG3xHCPi1knBb1v9c")
    test_validator.verify_test(clio_server, clio_response, method="account_offers", response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_limit_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="invalidParams")

    clio_response = clio_server.get_account_offers(account.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_limit_less_than_10(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit=5)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_offers(account.account_id, limit=5)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_limit_greater_than_400(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit=405)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_offers(account.account_id, limit=405)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_offers(account.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit=10,
                                                 marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(rippled_server, response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_offers(account.account_id, limit=10,
                                                   marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(clio_server, clio_response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_offers_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_offers(account.account_id, limit=10,
                                                 marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166")
    test_validator.verify_test(rippled_server, response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_offers(account.account_id, limit=10,
                                                   marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166")
    test_validator.verify_test(clio_server, clio_response, method="account_offers", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
