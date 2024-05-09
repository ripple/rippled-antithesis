import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import helper, log_helper, test_validator

log = log_helper.get_logger()


def test_amm_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "asset": constants.XRP_ASSET,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_single_asset_instance_non_numeric_xrp_value_asset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)

    payload = {
        "tx_json": {
            "asset": "anystring",
            "asset2": usd_asset,
            "ledger_index": "validated"
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, response_result="issueMalformed", method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, response_result="issueMalformed", method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_two_asset_instance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, usd_asset, cny_asset)

    payload = {
        "tx_json": {
            "asset": usd_asset,
            "asset2": cny_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_two_asset_instance_both_bad_strings(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    beans_asset = "beans"
    cool_asset = "cool"

    payload = {
        "tx_json": {
            "asset": beans_asset,
            "asset2": cool_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, response_result="issueMalformed", method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, response_result="issueMalformed", method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_has_extra_fields(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "Amount": constants.DEFAULT_AMM_XRP_CREATE,
            "": usd_asset,
            "asdf": "someammid",
            "ledger_index": "validated"
        }
    }

    rippled_server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, usd_asset)

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, response_result="invalidParams", method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams", method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_numeric_xrp_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)

    payload = {
        "tx_json": {
            "asset": int(xrp_asset),
            "asset2": usd_asset,
            "ledger_index": "validated"
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, response_result="issueMalformed", method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, response_result="issueMalformed", method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_only_amm_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "amm_account": rippled_server.get_amm_id(xrp_asset, usd_asset),
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_amm_account_as_issuer_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "amm_account": gw.account_id,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_malformed_amm_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm_account": "r4SX4tGLQYKyMN3F5PUWWVtHLXFdzb1UY",
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_amm_account_and_assets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "amm_account": rippled_server.get_amm_id(xrp_asset, usd_asset),
            "asset": constants.XRP_ASSET,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_only_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "account": gw.account_id,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_non_funded_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account()

    payload = {
        "tx_json": {
            "account": gw.account_id,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "account": "rP32Fk3eRYDNSz8B31CxC5Jphc8Tz6Gt8",
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actMalformed")

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4915


def test_amm_info_with_account_and_assets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "account": gw.account_id,
            "asset": constants.XRP_ASSET,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_account_amm_account_and_assets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "account": gw.account_id,
            "amm_account": rippled_server.get_amm_id(xrp_asset, usd_asset),
            "asset": constants.XRP_ASSET,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_account_and_amm_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "account": gw.account_id,
            "amm_account": rippled_server.get_amm_id(xrp_asset, usd_asset)
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "asset": {
                "currency": "XRP",
                "issuer": gw.account_id
            },
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="issueMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="issueMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset2_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "asset2": {
                "currency": "XRP",
                "issuer": gw.account_id
            },
            "asset": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="issueMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="issueMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset_and_non_funded_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account()
    alice = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "asset": usd_asset,
            "asset2": cny_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset_and_malformed_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": "rnNoxzrNk9UGC1ncKkSCz8QugyhG5tRHm",
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, usd_asset, cny_asset)

    payload = {
        "tx_json": {
            "asset": usd_asset,
            "asset2": cny_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="issueMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="issueMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset2_and_non_funded_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account()
    alice = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "asset": usd_asset,
            "asset2": cny_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_asset2_and_malformed_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": "rnNoxzrNk9UGC1ncKkSCz8QugyhG5tRHm",
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, usd_asset, cny_asset)

    payload = {
        "tx_json": {
            "asset": cny_asset,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="issueMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="issueMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_only_one_asset2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, usd_asset, cny_asset)

    payload = {
        "tx_json": {
            "asset": cny_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_account_and_only_one_asset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "account": gw.account_id,
            "asset2": usd_asset,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_malformed_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "asset": constants.XRP_ASSET,
            "asset2": usd_asset,
            "ledger_index": "malformed",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_amm_info_with_both_xrp_assets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]
    gw = rippled_server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp_asset, usd_asset)
    payload = {
        "tx_json": {
            "asset": constants.XRP_ASSET,
            "asset2": constants.XRP_ASSET,
            "ledger_index": "validated",
        }
    }

    rippled_response = rippled_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(rippled_server, rippled_response, method="amm_info", response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="amm_info")
    test_validator.verify_test(clio_server, clio_response, method="amm_info", response_result="actNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
