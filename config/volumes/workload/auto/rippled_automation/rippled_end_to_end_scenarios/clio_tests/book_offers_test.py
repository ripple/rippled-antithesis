import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_book_offers(fx_rippled):
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

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_lower_case_in_currency_code(fx_rippled):
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
                "currency": "gKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    for offer_count in range(1, 5):
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
        response = rippled_server.get_book_offers(response=offer_create_response, limit=offer_count)
        test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

        clio_response = clio_server.get_book_offers(response=offer_create_response, limit=offer_count)
        test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")
        assert helper.compare_dict(response, clio_response,
                                   ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_ledger_hash(fx_rippled):
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
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account, destination_account])

    response = rippled_server.get_book_offers(response=offer_create_response,
                                              ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_book_offers(response=offer_create_response,
                                                ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_ledger_index(fx_rippled):
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
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account, destination_account])

    response = rippled_server.get_book_offers(response=offer_create_response,
                                              ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_book_offers(response=offer_create_response,
                                                ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_non_existent_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "taker": destination_account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_malformed_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": "r9cZA1mLK5R5Am25ArfXFmqgNwjZgnfk5",
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_limit_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    taker = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": taker.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": account.account_id
            },
            "ledger_index": "validated",
            "limit": 0
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, taker])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, taker], response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4541


def test_book_offers_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    taker = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": taker.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": account.account_id
            },
            "ledger_index": "validated",
            "limit": "10"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, taker], response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, taker], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "AAA"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_non_existent_taker_gets_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "INR",
                "issuer": destination_account.account_id
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_taker_gets_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "INR",
                "issuer": "rB7LiohHNiAnP4t1QK2RNL4YGat57sCDM"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_gets_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP",
                "issuer": "r97U4iT9m8Q2FeYnAQ1gFKGFDoKe8E7Rh"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_gets_currency_non_xrp_and_no_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "INR"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_empty_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "ZZZ",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account])


def test_book_offers_with_non_existent_taker_pays_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_invalid_taker_pays_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": "rB7LiohHNiAnP4t1QK2RNL4YGat57sCDM"
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="book_offers",
                               response_result="srcIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="book_offers",
                               response_result="srcIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_pays_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "XRP",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="srcIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="srcIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_pays_currency_non_xrp_and_no_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "JOD"
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="book_offers",
                               response_result="srcIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="book_offers",
                               response_result="srcIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_empty_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="book_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="book_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_without_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_without_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="book_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="book_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_malformed_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "aa",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="srcCurMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="srcCurMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_malformed_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "aa"
            },
            "taker_pays": {
                "currency": "JOD",
                "issuer": destination_account.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account], method="book_offers",
                               response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="book_offers", response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_same_taker_gets_and_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "taker": account.account_id,
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "XRP"
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="book_offers",
                               response_result="badMarket")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="book_offers",
                               response_result="badMarket")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_issuer_account_global_freeze(fx_rippled):
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

    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_2.account_id,
            "Flags": 0,
            "SetFlag": 7,
            "Sequence": rippled_server.get_account_sequence(account_1)
        },
        "secret": account_2.master_seed
    }

    global_freeze_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, global_freeze_response, accounts=[account_1, account_2])

    account_info_response = rippled_server.get_account_info(account_id=account_2.account_id)
    test_validator.verify_test(rippled_server, account_info_response, accounts=[account_1, account_2])

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_gets_issuer_account_global_freeze(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerPays": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_1.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_1.account_id,
            "Flags": 0,
            "SetFlag": 7,
            "Sequence": rippled_server.get_account_sequence(account_1)
        },
        "secret": account_1.master_seed
    }

    global_freeze_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, global_freeze_response, accounts=[account_1, account_2])

    account_info_response = rippled_server.get_account_info(account_id=account_1.account_id)
    test_validator.verify_test(rippled_server, account_info_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "taker_gets": {
                "currency": "GKO",
                "issuer": account_1.account_id
            },
            "taker_pays": {
                "currency": "USD",
                "issuer": account_2.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_taker_account_global_freeze(fx_rippled):
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

    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_1.account_id,
            "Flags": 0,
            "SetFlag": 7,
            "Sequence": rippled_server.get_account_sequence(account_1)
        },
        "secret": account_1.master_seed
    }

    global_freeze_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, global_freeze_response, accounts=[account_1, account_2])

    account_info_response = rippled_server.get_account_info(account_id=account_1.account_id)
    test_validator.verify_test(rippled_server, account_info_response, accounts=[account_1, account_2])

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_offer_owner_as_taker_gets_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "2"
            },
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

    payload = {
        "tx_json": {
            "taker_gets": {
                "currency": "USD",
                "issuer": account_1.account_id
            },
            "taker_pays": {
                "currency": "GKO",
                "issuer": account_2.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_multiple_offers_by_owner(fx_rippled):
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "3"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "4"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "GKO",
                "issuer": account_2.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")
    assert response["offers"][0]["owner_funds"], "owner_funds not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")
    assert clio_response["offers"][0]["owner_funds"], "owner_funds not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_issuer_transfer_rate_not_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account_root": account_2.account_id,
            "ledger_index": "validated",
            "TransferRate": 100
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "AccountRoot", "AccountRoot not found"

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

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_trustline_freeze_between_offer_owner_and_taker_gets_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Create a trust line between account_1 and account_2
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
    trust_line_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, trust_line_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_lines(account_2.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    # Create an offer with account_1 as offer owner and account_2 as issuer
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    # Freeze the trust line between offer owner and issuer
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "Flags": 1048576,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    freeze_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, freeze_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_lines(account_2.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "USD",
                "issuer": account_2.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_book_offers_with_unfunded_offers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": "20000000",
            "TakerPays": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": "20000000",
            "TakerPays": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "taker_gets": {
                "currency": "XRP"
            },
            "taker_pays": {
                "currency": "USD",
                "issuer": account_2.account_id
            },
            "ledger_index": "validated"
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")
    assert response["offers"][0]["owner_funds"], "owner_funds not found: {}".format(response)
    assert response["offers"][1]["taker_gets_funded"], "taker_gets_funded not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="book_offers")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="book_offers")
    assert clio_response["offers"][0]["owner_funds"], "owner_funds not found: {}".format(response)
    assert clio_response["offers"][1]["taker_gets_funded"], "taker_gets_funded not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
