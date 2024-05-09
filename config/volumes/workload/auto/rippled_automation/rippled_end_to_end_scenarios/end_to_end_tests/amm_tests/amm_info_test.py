from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils.amm.amm_helper import setup_env

log = log_helper.get_logger()


def test_amm_info_single_asset_instance(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, asset_1, asset_2)
    payload = {
        "tx_json": {
            "asset": constants.XRP_ASSET,
            "asset2": asset_2,
            "ledger_index": "validated"
        }
    }

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, method="amm_info")


def test_amm_info_single_asset_instance_non_numeric_xrp_value_asset(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, asset_1, asset_2)

    payload = {
        "tx_json": {
            "asset": "anystring",
            "asset2": asset_2,
            "ledger_index": "validated"
        }
    }

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, response_result="issueMalformed", method="amm_info")


def test_amm_info_two_asset_instance(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2 = {
        "currency": "CNY",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, asset_1, asset_2)
    payload = {
        "tx_json": {
            "asset": asset_1,
            "asset2": asset_2,
            "ledger_index": "validated"
        }
    }

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, method="amm_info")


def test_amm_info_two_asset_instance_both_bad_strings(fx_rippled):
    server = fx_rippled["rippled_server"]

    asset_1 = "beans"
    asset_2 = "cool"

    payload = {
        "tx_json": {
            "asset": asset_1,
            "asset2": asset_2,
            "ledger_index": "validated"
        }
    }

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, response_result="issueMalformed", method="amm_info")


def test_amm_info_has_extra_fields(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "Amount": constants.DEFAULT_AMM_XRP_CREATE,
            "": asset_1,
            "asdf": "someammid",
            "ledger_index": "validated"
        }
    }

    server.amm_create(account_1, constants.DEFAULT_AMM_XRP_CREATE, asset_1)

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, response_result="invalidParams", method="amm_info")


def test_amm_info_with_numeric_xrp_amount(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, asset_1, asset_2)

    payload = {
        "tx_json": {
            "asset": int(asset_1),
            "asset2": asset_2,
            "ledger_index": "validated"
        }
    }

    amm_info_response = server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(server, amm_info_response, response_result="issueMalformed", method="amm_info")
