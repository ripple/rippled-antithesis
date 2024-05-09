from copy import copy

import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_deposit_single_asset_deposit_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, xrp_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    token_amount = constants.DEFAULT_AMM_TOKEN_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, token_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_token_low_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1")

    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    token_amount = constants.DEFAULT_AMM_TOKEN_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, token_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_token_high_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1000")

    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    token_amount = constants.DEFAULT_AMM_TOKEN_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, token_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_xrp_low_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1")

    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, xrp_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_xrp_high_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1000")

    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, xrp_amount)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_insufficient_token_balance(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    server.make_payment(gw, alice, payment)
    alice_deposit = dict(payment, value=str(int(payment["value"]) + 1))

    deposit_response = server.amm_deposit(alice, asset_1, asset_2, alice_deposit)
    test_validator.verify_test(server, deposit_response, response_result="tecUNFUNDED_AMM")


def test_deposit_single_asset_deposit_token_flag_missing(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2_pay = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_CREATE)

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2_pay)

    amount = asset_2_pay

    payload = {
        "secret": bob.master_seed,
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount,
            "Asset": asset_1,
            "Asset2": asset_2,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "TransactionType": "AMMDeposit",
        },
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temMALFORMED")


def test_deposit_single_asset_deposit_token_wrong_mode_flag(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2_pay = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_CREATE)

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2_pay)

    amount = asset_2_pay

    payload = {
        "secret": bob.master_seed,
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount,
            "Asset": asset_1,
            "Asset2": asset_2,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "TransactionType": "AMMDeposit",
        },
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temMALFORMED")


def test_deposit_single_asset_deposit_xrp_wrong_deposit_mode(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_out = dict(lp_token, value="1000")
    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfLimitLPToken"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_out,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temMALFORMED")


def test_deposit_single_asset_deposit_xrp_and_token_transposed(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    server.amm_create(alice, amount, asset_2)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_2,
            "Amount": asset_2,
            "Asset2": asset_1,
            "Amount2": amount,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_deposit_float_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_DEPOSIT
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }

    server.amm_create(alice, asset_1, asset_2)
    amount = float(asset_1)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Amount2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="invalidParams")


def test_deposit_single_asset_deposit_zero_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    server.amm_info(constants.XRP_ASSET, asset_2)

    asset_1 = constants.XRP_ASSET
    amount = "0"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Amount2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMOUNT")


def test_deposit_single_asset_deposit_negative_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

    server.amm_create(alice, asset_1, asset_2)
    server.amm_info(constants.XRP_ASSET, asset_2)

    asset_1 = constants.XRP_ASSET
    amount = "-1000000"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Amount2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMOUNT")


def test_deposit_single_asset_deposit_more_xrp_than_available(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    asset_1 = constants.XRP_ASSET
    amount = str(int(server.get_account_balance(bob.account_id)) + 1)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Amount2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="tecINSUF_RESERVE_LINE")


def test_deposit_single_asset_double_deposit_more_tokens_than_available(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(alice, asset_2)

    server.amm_create(gw, asset_1, asset_2)

    asset_1 = constants.XRP_ASSET
    pay_usd_alice = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    server.make_payment(gw, alice, pay_usd_alice)

    asset_2_deposit = dict(asset_2, value="50")
    asset_1_deposit = constants.DEFAULT_AMM_XRP_DEPOSIT

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": asset_1_deposit,
            "Asset2": asset_2,
            "Amount2": asset_2_deposit,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="tecUNFUNDED_AMM")


def test_deposit_single_asset_deposit_zero_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    payment_amount = 2

    server.amm_create(alice, asset_1, asset_2)

    asset_2["value"] = payment_amount
    server.make_payment(alice, bob, asset_2)

    amount = copy(asset_2)
    amount["value"] = "0"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMOUNT")


def test_deposit_single_asset_deposit_negative_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    amount = copy(asset_2)
    amount["value"] = "-10"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMOUNT")


def test_deposit_single_asset_deposit_wrong_currency(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    deposit_amount = dict(asset_2, currency="CNY", value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": deposit_amount,
            "Asset2": asset_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMM_TOKENS")


def test_deposit_single_asset_deposit_wrong_issuer(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    alice_usd = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    bob_usd = {
        "currency": "USD",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(alice, bob_usd)
    server.make_payment(bob, alice, bob_usd)

    server.amm_create(alice, asset_1, alice_usd)

    bob_usd_deposit = dict(bob_usd, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": bob_usd_deposit,
            "Asset2": alice_usd,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMM_TOKENS")


def test_deposit_single_asset_request_lp_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(alice, asset_2)
    server.make_payment(gw, alice, asset_2)

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    amount = str(int(server.get_account_balance(alice.account_id)) - 20000000)
    lp_token_out = dict(lp_token, value="4000")
    deposit_response = server.amm_deposit(
        alice, asset_1, asset_2, amount, lp_token_out=lp_token_out, mode="tfOneAssetLPToken")
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_request_lp_tokens_zero_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "CNY", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    lp_token_request = dict(server.get_amm_lp_token(asset_1, asset_2), value="0")

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfOneAssetLPToken"],
            "Asset": constants.XRP_ASSET,
            "Amount": "20",
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMM_TOKENS")


def test_deposit_single_asset_request_lp_tokens_missing_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    deposit_amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    lp_token_request = ""

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfOneAssetLPToken"],
            "Asset": constants.XRP_ASSET,
            "Amount": deposit_amount,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="invalidParams")


def test_deposit_single_asset_request_more_lp_tokens_than_asset_offered(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    xrp_deposit_amount = "200000"
    lp_token_request = dict(server.get_amm_lp_token(asset_1, asset_2), value="1000")

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfOneAssetLPToken"],
            "Asset": constants.XRP_ASSET,
            "Amount": xrp_deposit_amount,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }
    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="tecAMM_FAILED")


def test_deposit_single_asset_request_more_lp_tokens_than_amm_has(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    max_deposit_amount = "2700000"
    lp_token_request = dict(server.get_amm_lp_token(asset_1, asset_2), value="20000")

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfOneAssetLPToken"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)

    test_validator.verify_test(server, deposit_response, response_result="tecAMM_FAILED")


def test_deposit_single_asset_effective_price(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    xrp_create_amount = constants.DEFAULT_AMM_XRP_CREATE
    server.amm_create(alice, xrp_create_amount, asset_2)

    eprice = "2500"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfLimitLPToken"],
            "Asset": asset_1,
            "Amount": constants.DEFAULT_AMM_XRP_DEPOSIT,
            "EPrice": eprice,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)

    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_effective_price_too_low(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    xrp_create_amount = constants.DEFAULT_AMM_XRP_CREATE
    server.amm_create(alice, xrp_create_amount, asset_2)

    eprice = "2000"

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfLimitLPToken"],
            "Asset": asset_1,
            "Amount": constants.DEFAULT_AMM_XRP_DEPOSIT,
            "EPrice": eprice,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)

    test_validator.verify_test(server, deposit_response, response_result="tecAMM_FAILED")


def test_deposit_single_asset_individual_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    server.create_trustline(bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    alice_pay_bob = dict(asset_2, value="1000")
    server.make_payment(alice, bob, alice_pay_bob)
    bob_asset_frozen = dict(asset_2, issuer=bob.account_id)

    server.freeze_trustline(alice, bob_asset_frozen)

    bob_deposit = dict(asset_2, value="20")
    deposit_response = server.amm_deposit(bob, constants.XRP_ASSET, asset_2, bob_deposit)
    test_validator.verify_test(server, deposit_response, response_result="tecFROZEN")


def test_deposit_single_asset_global_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    server.create_trustline(bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    alice_pay_bob = dict(asset_2, value="1000")
    server.make_payment(alice, bob, alice_pay_bob)
    bob_deposit = dict(alice_pay_bob, value="100")

    server.set_global_freeze(alice)
    deposit_response = server.amm_deposit(bob, constants.XRP_ASSET, asset_2, bob_deposit)
    test_validator.verify_test(server, deposit_response, response_result="tecFROZEN")

    deposit_response = server.amm_deposit(bob, constants.XRP_ASSET, asset_2, constants.DEFAULT_AMM_XRP_DEPOSIT)
    test_validator.verify_test(server, deposit_response)

    server.unset_global_freeze(alice)
    deposit_response = server.amm_deposit(bob, constants.XRP_ASSET, asset_2, bob_deposit)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_creator_can_deposit(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": asset_2,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response)


def test_deposit_single_asset_cannot_deposit_lp_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": lp_token,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMM_TOKENS")


def test_deposit_single_asset_deposit_xrp_invalid_flag(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    server.create_trustline(alice, asset_2)
    payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)
    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Account": alice.account_id,
            "Asset": asset_1,
            "Asset2": asset_2,
            "Amount": xrp_amount,
            "Fee": "20000000",
            "Flags": "33554432",
        },
        "secret": alice.master_seed,
    }
    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temINVALID_FLAG")


def test_deposit_single_asset_nonexistent_depositor(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=False)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    amount = constants.DEFAULT_AMM_TOKEN_DEPOSIT
    lp_token_out = dict(lp_token, value="4000")
    deposit_response = server.amm_deposit(
        alice, asset_1, asset_2, amount, lp_token_out=lp_token_out, mode="tfOneAssetLPToken"
    )
    test_validator.verify_test(server, deposit_response, response_result="srcActNotFound")


def test_deposit_two_asset_xrp_deposit(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    deposit_amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    deposit_amount_2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": deposit_amount,
            "Asset2": asset_2,
            "Amount2": deposit_amount_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response)


def test_deposit_two_asset_xrp_deposit_insufficient_token_balance(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    deposit_amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    bob_deposit = dict(asset_2, value=str(int(deposit_amount) + 1))

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": constants.XRP_ASSET,
            "Amount": deposit_amount,
            "Asset2": asset_2,
            "Amount2": bob_deposit,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="tecUNFUNDED_AMM")


def test_deposit_two_asset_xrp_deposit_invalid_flag(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    deposit_amount = constants.DEFAULT_AMM_XRP_DEPOSIT
    deposit_amount_2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": "1",
            "Asset": constants.XRP_ASSET,
            "Amount": deposit_amount,
            "Asset2": asset_2,
            "Amount2": deposit_amount_2,
            "Account": bob.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": bob.master_seed,
    }

    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, response_result="temINVALID_FLAG")


def test_deposit_two_asset_both_tokens_deposit(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }
    asset_2 = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }

    for asset in [asset_1, asset_2]:
        server.create_trustline(alice, asset)
        server.make_payment(gw, alice, asset)
    server.amm_create(gw, asset_1, asset_2)
    amount_1 = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    amount_2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    deposit_response = server.amm_deposit(alice, asset_1, asset_2, amount_1, amount_2, mode="tfTwoAsset")
    test_validator.verify_test(server, deposit_response)


def test_deposit_two_asset_both_tokens_deposit_no_amm(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }
    asset_2 = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }

    for asset in [asset_1, asset_2]:
        server.create_trustline(alice, asset)
        server.make_payment(gw, alice, asset)

    amount_1 = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    amount_2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    deposit_response = server.amm_deposit(alice, asset_1, asset_2, amount_1, amount_2, mode="tfTwoAsset")
    test_validator.verify_test(server, deposit_response, response_result="terNO_AMM")


def test_deposit_two_asset_deposit_wrong_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_DEPOSIT
    asset_2 = {
        "currency": "USD",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }
    asset_3 = {
        "currency": "CNY",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT,
    }

    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob, asset_2)
    server.make_payment(alice, bob, asset_3)

    server.amm_create(alice, asset_2, asset_3)

    deposit_amount = str(float(asset_2["value"]) / 2)
    amount_3 = copy(asset_3)
    amount_3["value"] = deposit_amount

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfTwoAsset"],
            "Asset": asset_2,
            "Amount": asset_1,
            "Asset2": asset_3,
            "Amount2": amount_3,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="temBAD_AMM_TOKENS")


def test_deposit_two_asset_global_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = {
        "currency": "ALI",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }
    asset_2 = {
        "currency": "BOB",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

    bpay = dict(asset_2, value=1000)

    server.amm_create(gw, asset_1, asset_2)
    server.set_global_freeze(gw)

    bdeposit = dict(bpay, value=100)

    deposit_response = server.amm_deposit(bob, asset_1, asset_2, bdeposit)
    test_validator.verify_test(server, deposit_response, response_result="tecFROZEN")


def test_deposit_two_asset_individual_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    asset_1 = {
        "currency": "ALI",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_2 = {
        "currency": "BOB",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    a_pay = dict(asset_1, value=1000)
    b_pay = dict(asset_2, value=1000)

    server.create_trustline(carol, a_pay)
    server.create_trustline(carol, b_pay)

    server.make_payment(alice, carol, a_pay)
    server.make_payment(bob, carol, b_pay)

    server.set_default_ripple(alice)
    server.set_default_ripple(bob)
    server.amm_create(carol, asset_1, asset_2)

    c_pay = dict(a_pay, issuer=carol.account_id)
    server.freeze_trustline(alice, c_pay)

    cdeposit = dict(a_pay, value=100)
    deposit_response = server.amm_deposit(carol, asset_1, asset_2, cdeposit)
    test_validator.verify_test(server, deposit_response, response_result="tecFROZEN")

    server.unfreeze_trustline(alice, c_pay)
    deposit_response = server.amm_deposit(carol, asset_1, asset_2, cdeposit)
    test_validator.verify_test(server, deposit_response)


def test_deposit_two_asset_creators_deposit_requests_more_lp_tokens_than_assets_offered(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "10"
    }
    asset_2 = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": "10"
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token_request = dict(server.get_amm_lp_token(asset_1, asset_2), value="20")

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfLPToken"],
            "Asset": asset_1,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": gw.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": gw.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response)


def test_deposit_two_asset_account_requests_more_lp_tokens_than_assets(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }
    asset_2 = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.amm_create(gw, asset_1, asset_2)
    server.create_trustline(alice, asset_1)
    server.create_trustline(alice, asset_2)

    alice_token_balance = constants.DEFAULT_AMM_TOKEN_CREATE

    alice_payment_1 = dict(asset_1, value=alice_token_balance)
    alice_payment_2 = dict(asset_2, value=alice_token_balance)

    server.make_payment(gw, alice.account_id, alice_payment_1)
    server.make_payment(gw, alice.account_id, alice_payment_2)

    lp_token_request = dict(lp_token, value="20")

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_DEPOSIT_FLAGS["tfLPToken"],
            "Asset": asset_1,
            "Asset2": asset_2,
            "LPTokenOut": lp_token_request,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, deposit_response, response_result="tecUNFUNDED_AMM")
