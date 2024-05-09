import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_ripple_path_find(fx_rippled):
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
            "destination_account": account_2.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account_1.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ripple_path_find")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ripple_path_find")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_lower_case_in_currency_code(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "uSD",
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
            "destination_account": account_2.account_id,
            "destination_amount": {
                "currency": "uSD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account_1.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "uSD"
                }
            ],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ripple_path_find")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ripple_path_find")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_without_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="srcActMissing")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="srcActMissing")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_without_destination_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ripple_path_find",
                               response_result="dstActMissing")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ripple_path_find",
                               response_result="dstActMissing")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_without_destination_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="dstAmtMissing")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="dstAmtMissing")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_invalid_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": "raeR1nAGkMm18hHpUz1ZP6wGKLA4WCh8rX",
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": "raeR1nAGkMm18hHpUz1ZP6wGKLA4WCh8rXa",
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ripple_path_find",
                               response_result="srcActMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ripple_path_find",
                               response_result="srcActMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_destination_amount_1(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    source_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": source_account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account, source_account])

    payload = {
        "tx_json": {
            "destination_account": account.account_id,
            "destination_amount": -1,
            "source_account": source_account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, source_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, source_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_invalid_destination_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": "rNbCao7aZsKZe5iJ4a2jphifJgTtH9hJAga",
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ripple_path_find",
                               response_result="dstActMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ripple_path_find",
                               response_result="dstActMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_without_source_currency_and_send_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "send_max": constants.DEFAULT_TRANSFER_AMOUNT,
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_source_currency_and_send_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "send_max": 100000,
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_non_existent_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="srcActNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="srcActNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_non_existent_destination_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find",
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account_1.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, destination_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, destination_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_invalid_source_currencies(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "aa"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="srcCurMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="srcCurMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ripple_path_find_with_invalid_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": destination_account.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": "raeR1nAGkMm18hHpUz1ZP6wGKLA4WCh8rXa",
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account],
                               method="ripple_path_find", response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
