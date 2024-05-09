import time

import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.price_oracle import price_oracle_test_data as test_data

log = log_helper.get_logger()


@pytest.fixture(scope="session")
def create_max_valid_accounts_with_one_oracle_each(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    log.info(f"Creating {constants.MAX_ACCOUNT_COUNT_FOR_PRICE_ORACLE_AGGREGATE} accounts")
    accounts = [rippled_server.create_account(fund=True, verbose=False) for _ in range(constants.MAX_ACCOUNT_COUNT_FOR_PRICE_ORACLE_AGGREGATE)]

    log.info(f"Creating a PriceOracle for each of the {constants.MAX_ACCOUNT_COUNT_FOR_PRICE_ORACLE_AGGREGATE} accounts")
    for account in accounts:
        rippled_server.oracle_set(account, verbose=False)

    return accounts


@pytest.mark.smoke
def test_oracle_get_aggregate_price_with_one_price_data_without_trim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    for account in [alice, bob]:
        rippled_server.oracle_set(account)

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_one_price_data_and_min_trim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 1
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_one_price_data_and_max_trim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)
    account_4 = rippled_server.create_account(fund=True)

    for account in [account_1, account_2, account_3, account_4]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": account_1.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": account_2.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": account_3.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": account_4.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 25
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[account_1, account_2, account_3, account_4], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1370")
def test_oracle_get_aggregate_price_with_one_price_data_and_decimal_trim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 1.2
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_one_price_data_and_trim_threshold(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 1,
            "trim_threshold": 100
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_max_price_data_without_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_max_price_data_and_min_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 1
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_max_price_data_and_max_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 25
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_max_price_data_and_trim_threshold(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 1,
            "trim_threshold": 100
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_over_max_price_data_without_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each
    extra_account = rippled_server.create_account(fund=True)
    rippled_server.oracle_set(extra_account)

    # Add one more account to go over the max limit
    accounts.append(extra_account)

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_over_max_price_data_and_min_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each
    extra_account = rippled_server.create_account(fund=True)
    rippled_server.oracle_set(extra_account)

    # Add one more account to go over the max limit
    accounts.append(extra_account)

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 1
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_over_max_price_data_and_max_trim(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each
    extra_account = rippled_server.create_account(fund=True)
    rippled_server.oracle_set(extra_account)

    # Add one more account to go over the max limit
    accounts.append(extra_account)

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 25
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_oracle_get_aggregate_price_with_over_max_price_data_and_trim_threshold(fx_rippled, create_max_valid_accounts_with_one_oracle_each):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    accounts = create_max_valid_accounts_with_one_oracle_each
    extra_account = rippled_server.create_account(fund=True)
    rippled_server.oracle_set(extra_account)

    # Add one more account to go over the max limit
    accounts.append(extra_account)

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
            "trim": 1,
            "trim_threshold": 100
        }
    }

    for account in accounts:
        oracle_payload = {
            "account": account.account_id,
            "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        }
        payload["tx_json"]["oracles"].append(oracle_payload)

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=accounts, method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_one_price_data_and_over_max_trim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 26
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_one_price_data_and_invalid_trim_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": None
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1371")
@pytest.mark.parametrize("trim", ["", -1, "abc"])
def test_oracle_get_aggregate_price_with_one_price_data_and_malformed_trim_field(fx_rippled, trim):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": trim
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_matching_token_pair(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": "ABC",
            "quote_asset": "DEF",
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_base_asset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_quote_asset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_oracles(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_oracle_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_without_oracle_document_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1372")
@pytest.mark.parametrize("base_asset", [None, "Invalid", 123, -1, 0, 1.2, test_data.INVALID_NON_STANDARD_CURRENCY_CODE, "H", "HB", "HBAR", "",
                                        test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_oracle_get_aggregate_price_with_invalid_base_asset_field_inputs(fx_rippled, base_asset):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": base_asset,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1373")
@pytest.mark.parametrize("quote_asset", [None, "Invalid", 123, -1, 0, 1.2, test_data.INVALID_NON_STANDARD_CURRENCY_CODE, "H", "HB", "HBAR", "",
                                         test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_oracle_get_aggregate_price_with_invalid_quote_asset_field_inputs(fx_rippled, quote_asset):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": quote_asset,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=False)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": carol.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": carol.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.parametrize("account", [None, "", 1, 1.2, -1, "abc"])
def test_oracle_get_aggregate_price_with_invalid_account_fields(fx_rippled, account):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for test_account in [alice, bob]:
        rippled_server.oracle_set(test_account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": account,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": account,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.parametrize("oracle_document_id", ["", -1, "abc"])
def test_oracle_get_aggregate_price_with_invalid_oracle_document_id_fields(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": oracle_document_id
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": oracle_document_id
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1373")
@pytest.mark.parametrize("oracle_document_id", [None, (test_data.DEFAULT_ORACLE_DOCUMENT_ID + 1), 2.3])
def test_oracle_get_aggregate_price_with_valid_oracle_document_id_fields(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": oracle_document_id
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": oracle_document_id
                }
            ],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="objectNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_with_empty_oracles_list(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    for account in [alice, bob]:
        rippled_server.oracle_set(account)
    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [],
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price", response_result="oracleMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_after_two_updates_on_token_pair(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    # Generate PriceOracle only for one account. Other account will need custom Price Oracle.
    rippled_server.oracle_set(bob)

    payload_1 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_UPDATE_ASSET_PRICE,
                    "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                    "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                    "Scale": test_data.DEFAULT_SCALE
                }
            },
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": "ETH",
                        "QuoteAsset": "XDC",
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_1 = rippled_server.execute_transaction(payload_1)
    test_validator.verify_test(rippled_server, response_1, accounts=[alice])

    # First update
    payload_2 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE + 1,
                    "BaseAsset": "ETH",
                    "QuoteAsset": "XDC"
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[alice])

    # Second update
    payload_2 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE + 2,
                    "BaseAsset": "ETH",
                    "QuoteAsset": "XDC"
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[alice])

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 1,
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_oracle_get_aggregate_price_after_three_updates_on_token_pair(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    # Generate PriceOracle only for one account. Other account will need custom Price Oracle.
    rippled_server.oracle_set(bob)

    payload_1 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_UPDATE_ASSET_PRICE,
                    "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                    "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                    "Scale": test_data.DEFAULT_SCALE
                }
            },
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": "ETH",
                        "QuoteAsset": "XDC",
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_1 = rippled_server.execute_transaction(payload_1)
    test_validator.verify_test(rippled_server, response_1, accounts=[alice])

    # First update
    payload_2 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE + 1,
                    "BaseAsset": "ETH",
                    "QuoteAsset": "XDC"
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[alice])

    # Second update
    payload_2 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE + 2,
                    "BaseAsset": "ETH",
                    "QuoteAsset": "XDC"
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[alice])

    # Third update
    payload_2 = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE + 2,
                    "BaseAsset": "ETH",
                    "QuoteAsset": "XDC"
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[alice])

    payload = {
        "tx_json": {
            "base_asset": test_data.DEFAULT_BASE_ASSET,
            "quote_asset": test_data.DEFAULT_QUOTE_ASSET,
            "oracles": [
                {
                    "account": alice.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                },
                {
                    "account": bob.account_id,
                    "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
                }
            ],
            "trim": 1,
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], method="get_aggregate_price")

    clio_response = clio_server.execute_transaction(payload=payload, method="get_aggregate_price")
    test_validator.verify_test(clio_server, response, accounts=[alice, bob], method="get_aggregate_price")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
