import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


def test_ledger_without_params(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger()
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_ledger_hash(fx_rippled):
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
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_ledger_hash_and_api_version_2(fx_rippled):
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
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(ledger_hash=clio_response["ledger_hash"], api_version=2)
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_hash=clio_response["ledger_hash"], api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_ledger_index_validated(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(ledger_index="validated")
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    ledger_index = clio_server.ledger_current() - 10

    response = rippled_server.get_ledger(ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_transactions_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger(transactions=True)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert clio_response["ledger"]["transactions"], "transactions not found: {}".format(clio_response)

    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_transactions_true_and_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    ledger_index = clio_server.ledger_current() - 10

    response = rippled_server.get_ledger(transactions=True, ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_true_and_transactions_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger(transactions=True)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, expand=True)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert "transactions" in clio_response["ledger"], "transactions not found: {}".format(clio_response)

    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_expand_true_transactions_true_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    ledger_index = clio_server.ledger_current() - 10

    response = rippled_server.get_ledger(transactions=True, api_version=2, ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, api_version=2, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response = rippled_server.get_ledger(transactions=True, expand=True, api_version=2, ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, expand=True, api_version=2, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert "transactions" in clio_response["ledger"], "transactions not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_true_ledger_index_and_transactions_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    ledger_index = clio_server.ledger_current() - 10

    response = rippled_server.get_ledger(transactions=True, ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response = rippled_server.get_ledger(transactions=True, expand=True, ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions=True, expand=True, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert "transactions" in clio_response["ledger"], "transactions not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_true_ledger_hash_and_transactions_true(fx_rippled):
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
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(transactions=True, expand=True, ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(transactions=True, expand=True, ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert clio_response["ledger"]["transactions"], "transactions not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_true_offer_create_ledger_hash_and_transactions_true(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=offer_create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(transactions=True, expand=True, owner_funds=True,
                                         ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(transactions=True, expand=True, owner_funds=True,
                                           ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert clio_response["ledger"]["transactions"], "transactions not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_binary_and_transactions_true(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=offer_create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(transactions=True, expand=True, binary=True,
                                         ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(transactions=True, expand=True, binary=True,
                                           ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert clio_response["ledger"]["transactions"][0]["tx_blob"], "transactions tx_blob not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_binary_transactions_true_and_api_version_2(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=offer_create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(transactions=True, expand=True, binary=True,
                                         ledger_index=tx_response["ledger_index"], api_version=2)
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(transactions=True, expand=True, binary=True,
                                           ledger_index=tx_response["ledger_index"], api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert clio_response["ledger"]["transactions"][0]["tx_blob"], "transactions tx_blob not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_expand_false_binary_and_transactions_true(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=offer_create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    response = rippled_server.get_ledger(transactions=True, expand=False, binary=True,
                                         ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(rippled_server, response, method="ledger", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(transactions=True, expand=False, binary=True,
                                           ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    assert clio_response["ledger"]["transactions"], "transactions tx_blob not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_queue_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "queue": True
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response)

    # Not validating with method ledger as it gets rippled response which differs with Clio
    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_full_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "full": True
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")

    # Not validating with method ledger as it gets rippled response which differs with Clio
    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_accounts_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "accounts": True
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")

    # Not validating with method ledger as it gets rippled response which differs with Clio
    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_diff_true(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger(diff=True)
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    assert clio_response["ledger"]["diff"], "diff not found: {}".format(clio_response)

    # Not comparing as ledger is expected to differ from rippled response


def test_ledger_with_malformed_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(ledger_index="ghgj")
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="invalidParams")

    clio_response = clio_server.get_ledger(ledger_index="ghgj")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(ledger_index=rippled_server.ledger_current() + 10)
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="lgrNotFound")

    clio_response = clio_server.get_ledger(ledger_index=rippled_server.ledger_current() + 10)
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_hash": "E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3"
        }
    }

    response = rippled_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_with_malformed_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(ledger_hash="CC1E28B1041CD1DE4F1A2D6455435174D7B0EFDEE22A35B6018CB74BA2BBC1B")
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="invalidParams")

    clio_response = clio_server.get_ledger(
        ledger_hash="CC1E28B1041CD1DE4F1A2D6455435174D7B0EFDEE22A35B6018CB74BA2BBC1B")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_full_as_true_without_server_as_admin(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "accounts": False,
            "full": True,
            "transactions": False,
            "expand": False,
            "owner_funds": False
        }
    }

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")

    # Not validating with method ledger as it gets rippled response which differs with Clio
    # Not validating forwarded parameter as the response gets truncated on framework level


def test_ledger_accounts_as_true_without_server_as_admin(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "accounts": True,
            "full": False,
            "transactions": False,
            "expand": False,
            "owner_funds": False
        }
    }
    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")

    # Not validating with method ledger as it gets rippled response which differs with Clio
    # Not validating forwarded parameter as the response gets truncated on framework level


def test_ledger_with_ledger_index_lower_than_min_range(fx_rippled):
    clio_server = fx_rippled["clio_server"]
    rippled_server = fx_rippled["rippled_server"]

    ledger_index = clio_server.get_ledger_index_min() - 10

    response = rippled_server.get_ledger(ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="lgrNotFound")

    clio_response = clio_server.get_ledger(ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_full_as_false(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "full": False
        },
    }

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")


def test_ledger_full_as_malformed_value(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "full": "fgh"
        },
    }

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")


def test_ledger_accounts_as_false(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "accounts": False
        },
    }

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, response_result="notSupported")


def test_ledger_accounts_as_malformed_value(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "accounts": "fgh"
        },
    }

    clio_response = clio_server.execute_transaction(payload, method="ledger")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="notSupported")


def test_ledger_transactions_as_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(transactions="fgh")
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(transactions="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                        ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # TODO: Uncomment this after Rippled issue: https://github.com/XRPLF/rippled/issues/4832 is fixed


def test_ledger_expand_as_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(expand="fgh")
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(expand="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                        ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # TODO: Uncomment this after Rippled issue: https://github.com/XRPLF/rippled/issues/4832 is fixed


def test_ledger_owner_funds_as_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(owner_funds="fgh")
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(owner_funds="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                        ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4832


def test_ledger_binary_as_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(binary="fgh")
    test_validator.verify_test(rippled_server, response, method="ledger")

    clio_response = clio_server.get_ledger(binary="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                        ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4832


def test_ledger_queue_as_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger(queue="fgh")
    test_validator.verify_test(rippled_server, response, method="ledger", response_result="invalidParams")

    clio_response = clio_server.get_ledger(queue="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_diff_as_malformed_value(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger(diff="fgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger", response_result="invalidParams")
