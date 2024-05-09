import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.price_oracle import price_oracle_test_data as test_data
from ..utils import log_helper, helper
from ..utils import test_validator
from ..utils.amm.amm_helper import setup_env

log = log_helper.get_logger()


@pytest.mark.smoke
def test_account_tx(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_tx(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.get_account_tx(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_tx(account_1.account_id, api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.get_account_tx(account_1.account_id, api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    for i in range(10):
        payload = {
            "tx_json": {
                "TransactionType": "CheckCreate",
                "Account": account_1.account_id,
                "Destination": account_2.account_id,
                "SendMax": constants.DEFAULT_CHECK_MAX_SEND
            },
            "secret": account_1.master_seed
        }
        create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_tx(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.get_account_tx(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_tx(account_1.account_id, limit=5)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2], method="account_tx")

    clio_response_1 = clio_server.get_account_tx(account_1.account_id, limit=5)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response_1["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_tx(account_1.account_id, marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2], method="account_tx")

    clio_response_2 = clio_server.get_account_tx(account_1.account_id, marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response_2["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="transactions")


def test_account_tx_with_forward_true_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    for i in range(10):
        payload = {
            "tx_json": {
                "TransactionType": "CheckCreate",
                "Account": account_1.account_id,
                "Destination": account_2.account_id,
                "SendMax": constants.DEFAULT_CHECK_MAX_SEND
            },
            "secret": account_1.master_seed
        }
        create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_tx(account_1.account_id, forward=True)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.get_account_tx(account_1.account_id, forward=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_tx(account_1.account_id, limit=5, forward=True)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2], method="account_tx")

    clio_response_1 = clio_server.get_account_tx(account_1.account_id, limit=5, forward=True)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response_1["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_tx(account_1.account_id, marker=response_1["marker"], forward=True)
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2], method="account_tx")

    clio_response_2 = clio_server.get_account_tx(account_1.account_id, marker=clio_response_1["marker"], forward=True)
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1, account_2], method="account_tx")

    for transaction in clio_response_2["transactions"]:
        transaction["tx"]["inLedger"] = transaction["tx"]["ledger_index"]

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="transactions")


def test_account_tx_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "binary": False,
            "forward": False,
            "ledger_index_max": -1,
            "ledger_index_min": -1
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, method="account_tx", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_tx(account_id="r4s7P9WUU6AZ9DB315GWKtBaaDji9Zst8")
    test_validator.verify_test(rippled_server, response, method="account_tx", response_result="actMalformed")

    clio_response = clio_server.get_account_tx(account_id="r4s7P9WUU6AZ9DB315GWKtBaaDji9Zst8")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issues: https://github.com/XRPLF/rippled/issues/4541


def test_account_tx_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issues: https://github.com/XRPLF/rippled/issues/4541


def test_account_tx_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id,
                                             marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_tx(account_id=account.account_id,
                                               marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id,
                                             marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_tx(account_id=account.account_id,
                                               marker="0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_binary_true(fx_rippled):
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

    response = rippled_server.get_account_tx(account_id=account_1.account_id, binary=True)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_account_tx(account_id=account_1.account_id, binary=True)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_binary_true_and_api_version_2(fx_rippled):
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

    response = rippled_server.get_account_tx(account_id=account_1.account_id, binary=True, api_version=2)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_account_tx(account_id=account_1.account_id, binary=True, api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_binary(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, binary="fhg")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id, binary="fhg")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_binary_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, binary="fhg", api_version=2)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, binary="fhg", api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index(fx_rippled):
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

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": response["tx_json"]["Sequence"]
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account_1, account_2])

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_forward_as_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, forward=True)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id, forward=True)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_forward_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, forward="fgh")
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id, forward="fgh")
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_forward_value_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_tx(account_id=account.account_id, forward="fgh", api_version=2)
    test_validator.verify_test(rippled_server, response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, forward="fgh", api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="account_tx", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_values_out_of_tx(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    ledger_index_max = create_response["tx_json"]["Sequence"] - 10
    ledger_index_min = ledger_index_max - 10

    response = rippled_server.get_account_tx(account_1.account_id, ledger_index_max=ledger_index_max,
                                             ledger_index_min=ledger_index_min)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.get_account_tx(account_1.account_id, ledger_index_max=ledger_index_max,
                                               ledger_index_min=ledger_index_min)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["transactions"] == []

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_max_before_ledger_index_min_and_invalid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    ledger_index_min = rippled_server.ledger_current() - 10
    ledger_index_max = ledger_index_min - 10

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min,
                                             ledger_index_max=ledger_index_max)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx",
                               response_result="lgrIdxsInvalid")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min,
                                               ledger_index_max=ledger_index_max)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx",
                               response_result="lgrIdxsInvalid")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_max_before_ledger_index_min_and_valid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    ledger_index_min = rippled_server.ledger_current() - 100
    ledger_index_max = ledger_index_min - 300

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                             ledger_index_min=ledger_index_min)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="lgrIdxsInvalid")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                               ledger_index_min=ledger_index_min)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="lgrIdxsInvalid")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_max_before_ledger_index_min_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    ledger_index_min = rippled_server.ledger_current() - 100
    ledger_index_max = ledger_index_min - 300

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                             ledger_index_min=ledger_index_min, api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="invalidLgrRange")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                               ledger_index_min=ledger_index_min, api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidLgrRange")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_index_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    ledger_index_max = rippled_server.ledger_current() + 100

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_index_max_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    ledger_index_max = rippled_server.ledger_current() + 100

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                             api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx",
                               response_result="lgrIdxMalformed")

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_max=ledger_index_max,
                                               api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx",
                               response_result="lgrIdxMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_index_min(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    ledger_index_min = rippled_server.get_ledger_index_min()

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min - 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx")

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min - 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_index_min_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    ledger_index_min = rippled_server.get_ledger_index_min()

    response = rippled_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min - 100,
                                             api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx",
                               response_result="lgrIdxMalformed")

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_account_tx(account_id=account.account_id, ledger_index_min=ledger_index_min - 100,
                                               api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx",
                               response_result="lgrIdxMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account": account.account_id,
            "binary": False,
            "forward": False,
            "ledger_hash": "E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3"
        },
    }

    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx",
                               response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()
    payload = {
        "tx_json": {
            "account": account.account_id,
            "binary": False,
            "forward": False,
            "ledger_index": rippled_server.ledger_current() + 100
        },
    }

    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_tx",
                               response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_tx",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_ledger_index_min_ledger_index_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_index": rippled_server.ledger_current() - 10,
            "ledger_index_max": rippled_server.ledger_current() - 20,
            "ledger_index_min": rippled_server.ledger_current() - 30
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_ledger_index_min_ledger_index_max_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_index": rippled_server.ledger_current() - 10,
            "ledger_index_max": rippled_server.ledger_current() - 20,
            "ledger_index_min": rippled_server.ledger_current() - 30,
            "api_version": 2
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_hash_ledger_index_min_ledger_index_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx")

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_hash": clio_response["ledger_hash"],
            "ledger_index_max": tx_response["ledger_index"],
            "ledger_index_min": clio_server.ledger_current() - 20
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_hash_ledger_index_min_ledger_index_max_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx")

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_hash": clio_response["ledger_hash"],
            "ledger_index_max": tx_response["ledger_index"],
            "ledger_index_min": clio_server.ledger_current() - 20,
            "api_version": 2
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_ledger_hash_ledger_index_min_ledger_index_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx")

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_hash": clio_response["ledger_hash"],
            "ledger_index": tx_response["ledger_index"],
            "ledger_index_max": tx_response["ledger_index"],
            "ledger_index_min": clio_server.ledger_current() - 20
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_ledger_index_ledger_hash_ledger_index_min_ledger_index_max_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=create_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx")

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger")

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "binary": False,
            "forward": False,
            "ledger_hash": clio_response["ledger_hash"],
            "ledger_index": tx_response["ledger_index"],
            "ledger_index_max": tx_response["ledger_index"],
            "ledger_index_min": clio_server.ledger_current() - 20,
            "api_version": 2
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_tx")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_tx_type_AccountSet_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1.account_id),
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    clio_response = clio_server.get_account_tx(account_1.account_id, tx_type="AccountSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "AccountSet", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_CheckCreate_txn_and_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": gw.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="CheckCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx")

    assert len(clio_response["transactions"]) == 1, "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_AccountDelete_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])

    clio_response = clio_server.get_account_tx(account_1.account_id, tx_type="AccountDelete")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "AccountDelete", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_AMMBid_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, asset_1, asset_2)
    asset_1 = constants.XRP_ASSET
    lp_token = rippled_server.get_amm_lp_token(asset_1, asset_2)

    rippled_server.create_trustline(alice, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    rippled_server.make_payment(gw, alice, payment)

    bid_response = rippled_server.amm_bid(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, bid_response)

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMBid")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "AMMBid", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_AMMCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "AMMCreate", "Transaction type mismatch: {}".format(
        clio_response)


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/RIP-930")
def test_account_tx_with_tx_type_AMMDelete_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    xrp_asset = constants.XRP_ASSET
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    rippled_server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, usd_asset)
    currency = rippled_server.get_amm_lp_token(xrp_asset, usd_asset)
    trustline_limit = dict(currency, value="10000000")

    setup_env(rippled_server, number_of_accounts=520, currency=currency, trustline_limit=trustline_limit)

    rippled_server.withdraw_all(gw, xrp_asset, usd_asset)

    amm_delete_txn = {
        "tx_json": {
            "TransactionType": "AMMDelete",
            "Account": alice.account_id,
            "Asset": xrp_asset,
            "Asset2": usd_asset,
        },
    }

    amm_delete_response = rippled_server.execute_transaction(payload=amm_delete_txn, secret=alice.master_seed)
    test_validator.verify_test(rippled_server, amm_delete_response)

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMDelete")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "AMMDelete", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_AMMDeposit_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    deposit_response = rippled_server.amm_deposit(alice, asset_1, asset_2, xrp_amount)
    test_validator.verify_test(rippled_server, deposit_response)

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMDeposit")
    test_validator.verify_test(clio_server, clio_response, method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "AMMDeposit", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_AMMVote_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp, usd)
    rippled_server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd,
                               amount=constants.DEFAULT_AMM_XRP_DEPOSIT, )

    response = rippled_server.amm_vote(alice, constants.XRP_ASSET, usd)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMVote")
    test_validator.verify_test(clio_server, clio_response, method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "AMMVote", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_AMMWithdraw_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = rippled_server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(rippled_server, withdraw_response)

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="AMMWithdraw")
    test_validator.verify_test(clio_server, clio_response, method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "AMMWithdraw", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_CheckCancel_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": gw.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": gw.account_id,
            "CheckID": rippled_server.get_check_ids(gw)[0]
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="CheckCancel")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "CheckCancel", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_CheckCash_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": gw.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": alice.account_id,
            "CheckID": rippled_server.get_check_ids(gw)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="CheckCash")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "CheckCash", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_CheckCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": gw.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="CheckCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "CheckCreate", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_Clawback_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer,
                                                      flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    log.info("")
    log.info("** Add more IOU after clawback")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="Clawback")
    test_validator.verify_test(clio_server, clio_response, accounts=[issuer, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "Clawback", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_DepositPreauth_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=gw)
    rippled_server.deposit_preauthorize(account_object=gw, third_party_account=alice)

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="DepositPreauth")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "DepositPreauth", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_EscrowCancel_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": gw.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": gw.account_id,
            "Account": alice.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": alice.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)

    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="EscrowCancel")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "EscrowCancel", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_EscrowCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": gw.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="EscrowCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "EscrowCreate", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_EscrowFinish_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": gw.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": gw.account_id,
            "Account": alice.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": alice.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="EscrowFinish")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "EscrowFinish", "Transaction type mismatch: {}".format( clio_response)


def test_account_tx_with_tx_type_NFTokenAcceptOffer_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": gw.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    token_id = rippled_server.get_nft_tokens(gw.account_id)[0]

    # account to accept NFT offer
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": alice.account_id,
            "Owner": gw.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": gw.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(alice, token_id=token_id)[0]
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="NFTokenAcceptOffer")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenAcceptOffer", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_NFTokenBurn_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": gw.account_id,
            "NFTokenTaxon": 0
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": gw.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(gw.account_id)[-1]
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="NFTokenBurn")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenBurn", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_NFTokenCancelOffer_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": gw.account_id,
            "NFTokenTaxon": 0
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    token_id = rippled_server.get_nft_tokens(gw.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": gw.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": gw.account_id,
            "NFTokenOffers": [
                token_id  # should be ledger index; so should not cancel offer/remove object
            ]
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw], ignore_account_objects=True)

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="NFTokenCancelOffer")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenCancelOffer", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_NFTokenCreateOffer_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": gw.account_id,
            "NFTokenTaxon": 0
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    token_id = rippled_server.get_nft_tokens(gw.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": gw.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="NFTokenCreateOffer")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_NFTokenMint_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": gw.account_id,
            "NFTokenTaxon": 0
        },
        "secret": gw.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[gw])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="NFTokenMint")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenMint", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_OfferCancel_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": gw.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": alice.account_id,
                "value": "2"
            },
        },
        "secret": gw.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[gw, alice])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": gw.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": gw.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="OfferCancel")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "OfferCancel", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_OfferCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": gw.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": alice.account_id,
                "value": "2"
            },
        },
        "secret": gw.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="OfferCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "OfferCreate", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_Payment_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="Payment")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "Payment", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_PaymentChannelClaim_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": alice.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": gw.public_key_hex,
        },
        "secret": gw.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(gw)[0]
        },
        "secret": gw.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="PaymentChannelClaim")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "PaymentChannelClaim", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_PaymentChannelCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": alice.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": gw.public_key_hex,
        },
        "secret": gw.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="PaymentChannelCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "PaymentChannelCreate", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_PaymentChannelFund_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": alice.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": gw.public_key_hex,
        },
        "secret": gw.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(gw)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": gw.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="PaymentChannelFund")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "PaymentChannelFund", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_SetRegularKey_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "SetRegularKey",
            "Account": gw.account_id,
            "RegularKey": alice.account_id,
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    submit_blob_response = rippled_server.submit_blob(response)
    test_validator.verify_test(rippled_server, submit_blob_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="SetRegularKey")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "SetRegularKey", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_SignerListSet_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": gw.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": alice.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="SignerListSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "SignerListSet", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_TicketCreate_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": gw.account_id,
            "Sequence": rippled_server.get_account_sequence(gw),
            "TicketCount": 2
        },
        "secret": gw.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[gw])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="TicketCreate")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "TicketCreate", "Transaction type mismatch: {}".format(clio_response)


def test_account_tx_with_tx_type_TrustSet_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="TrustSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "TrustSet", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_tx_type_uppercase_TrustSet_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="TRUSTSET")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "TrustSet", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_invalid_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="account_channels")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw], method="account_tx",
                               response_result="invalidParams")


def test_account_tx_with_PaymentChannelCreate_txn_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True, amount="210000000")
    alice = rippled_server.create_account(fund=True)

    for channel_count in range(20):
        payload = {
            "tx_json": {
                "Account": gw.account_id,
                "TransactionType": "PaymentChannelCreate",
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "Destination": alice.account_id,
                "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
                "PublicKey": gw.public_key_hex,
            },
            "secret": gw.master_seed
        }

        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[gw, alice])

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="PaymentChannelCreate", limit=10)
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")

    clio_response = clio_server.get_account_tx(gw.account_id, tx_type="PaymentChannelCreate",
                                               marker=clio_response["marker"])
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_tx")


def test_account_tx_with_DIDSet_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    response = rippled_server.get_account_tx(alice.account_id)
    test_validator.verify_test(clio_server, response, accounts=[alice], method="account_tx")

    clio_response = clio_server.get_account_tx(alice.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_tx_type_DIDSet(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="DIDSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "DIDSet", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_DIDDelete_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    response = rippled_server.get_account_tx(alice.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_tx")

    clio_response = clio_server.get_account_tx(alice.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_with_tx_type_DIDDelete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="DIDDelete")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "DIDDelete", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_tx(account_id=account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_tx(account_id=account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_tx_for_OracleSet(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="OracleSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "OracleSet", "Transaction type mismatch: {}".format(
        clio_response)


def test_account_tx_for_OracleDelete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.get_account_tx(alice.account_id, tx_type="OracleDelete")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_tx")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "OracleDelete", "Transaction type mismatch: {}".format(
        clio_response)