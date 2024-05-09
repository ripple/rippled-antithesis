import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants


@pytest.mark.smoke
def test_withdraw_single_asset_withdraw_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_xrp_low_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1")
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_xrp_high_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1000")
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw( alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_token_low_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1")
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw( alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_token_high_fee(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2, trading_fee="1000")
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw( alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_xrp_flag_missing(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temMALFORMED")


def test_withdraw_single_asset_withdraw_invalid_flag(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "Flags": 1,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temINVALID_FLAG")


def test_withdraw_single_asset_wrong_mode_flag(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL
    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfTwoAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temMALFORMED")

    asset_2["value"] = constants.DEFAULT_AMM_TOKEN_WITHDRAWAL
    payload["tx_json"]["Amount"] = asset_2
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temMALFORMED")


def test_withdraw_single_asset_xrp_and_token_transposed(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(account_2, asset_2)
    server.make_payment(alice, account_2, asset_2)

    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL
    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    payload = {
        "tx_json": {
            "TransactionType": "AMMDeposit",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfTwoAsset"],
            "Asset": asset_2,
            "Amount": asset_2,
            "Asset2": asset_1,
            "Amount2": amount,
            "Account": account_2.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": account_2.master_seed,
    }

    amm_deposit_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, amm_deposit_response)


def test_withdraw_single_asset_withdraw_float_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = str(float(constants.DEFAULT_AMM_XRP_WITHDRAWAL))

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="invalidParams")


def test_withdraw_single_asset_withdraw_zero_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = "0"

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMOUNT")


def test_withdraw_single_asset_withdraw_negative_xrp(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = f"{int(constants.DEFAULT_AMM_XRP_WITHDRAWAL) * -1}"

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMOUNT")


def test_withdraw_single_asset_withdraw_more_xrp_than_available(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amm_id = server.get_amm_id(asset_1, asset_2)
    amount = str(int(server.get_account_balance(amm_id)) + 1)

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_withdraw_more_token_than_available(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, value=11)

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_withdraw_zero_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, value="0")

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMOUNT")


def test_withdraw_single_asset_withdraw_negative_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, value="-1")

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMOUNT")


def test_withdraw_single_asset_withdraw_wrong_currency(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, currency="CNY")

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMM_TOKENS")


def test_withdraw_single_asset_withdraw_wrong_issuer(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, issuer=bob.account_id)

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfSingleAsset"],
            "Asset": asset_1,
            "Amount": amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMM_TOKENS")


def test_withdraw_single_asset_LPTokenIn(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {

        "currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_tokens_in = dict(lp_token, value=constants.DEFAULT_AMM_LP_TOKEN_WITHDRAWAL)
    amount = "10"

    withdraw_response = server.amm_withdraw(
        alice, asset_1, asset_2, amount, lp_token_in=lp_tokens_in, mode="tfOneAssetLPToken")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_LPTokenIn_too_large(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    max_deposit_amount = "4000000"

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    withdrawal_amount = str(10000)
    lp_tokens_in = dict(lp_token, value=withdrawal_amount)

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfOneAssetLPToken"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "LPTokenIn": lp_tokens_in,
            "Account": alice.account_id,
        },
        "secret": alice.master_seed,
    }
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_request_lp_tokens_zero_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_tokens_in = dict(lp_token, value=0)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = server.amm_withdraw(
        alice, asset_1, asset_2, amount, lp_token_in=lp_tokens_in, mode="tfOneAssetLPToken"
    )
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMM_TOKENS")


def test_withdraw_single_asset_request_lp_tokens_missing_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL
    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfOneAssetLPToken")
    test_validator.verify_test(server, withdraw_response, response_result="invalidParams")


def test_withdraw_single_asset_request_more_lp_tokens_than_amount(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_tokens_in = dict(lp_token, value="10000")

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2,
                                            amount,
                                            lp_token_in=lp_tokens_in,
                                            mode="tfOneAssetLPToken")
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_request_more_lp_tokens_xrp_available(fx_rippled):
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
    server.amm_deposit(bob, asset_1, asset_2, "5000000")
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    lp_tokens_in = dict(lp_token, value="10000")
    amount = "1000"
    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2,
                                            amount,
                                            lp_token_in=lp_tokens_in,
                                            mode="tfOneAssetLPToken")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_effective_price(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "1000",
        }

    usd_payment = dict(usd, value="10000")
    server.create_trustline(alice, usd)
    server.create_trustline(carol, usd)
    server.make_payment(gw, alice, usd_payment)
    server.make_payment(gw, carol, usd_payment)

    server.set_default_ripple(gw)
    server.amm_create(alice, xrp, usd)
    lpt = server.get_amm_lp_token(constants.XRP_ASSET, usd)

    carol_lpt_out = dict(lpt, value="10000")
    server.amm_deposit(carol, constants.XRP_ASSET, usd, lp_token_out=carol_lpt_out, mode="tfLPToken")

    carol_withdraw = dict(usd, value="100")
    eprice = dict(lpt, value="52")
    withdraw_response = server.amm_withdraw(
        carol, constants.XRP_ASSET, usd, carol_withdraw, eprice=eprice, mode="tfLimitLPToken")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_effective_price_asset_out_zero(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "1000"
    }

    usd_payment = dict(usd, value="10000")
    server.create_trustline(alice, usd)
    server.create_trustline(carol, usd)
    server.make_payment(gw, alice, usd_payment)
    server.make_payment(gw, carol, usd_payment)

    server.set_default_ripple(gw)
    server.amm_create(alice, xrp, usd)
    lpt = server.get_amm_lp_token(constants.XRP_ASSET, usd)

    carol_lpt_out = dict(lpt, value="10000")
    server.amm_deposit(carol, constants.XRP_ASSET, usd, lp_token_out=carol_lpt_out, mode="tfLPToken")

    carol_withdraw = dict(usd, value="0")
    eprice = dict(lpt, value="52")
    withdraw_response = server.amm_withdraw(carol, constants.XRP_ASSET, usd, carol_withdraw,
                                            eprice=eprice,
                                            mode="tfLimitLPToken")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_effective_price_too_high(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "1000",
    }

    usd_payment = dict(usd, value="10000")
    server.create_trustline(alice, usd)
    server.create_trustline(carol, usd)
    server.make_payment(gw, alice, usd_payment)
    server.make_payment(gw, carol, usd_payment)

    server.set_default_ripple(gw)
    server.amm_create(alice, xrp, usd)
    lpt = server.get_amm_lp_token(constants.XRP_ASSET, usd)

    carol_lpt_out = dict(lpt, value="10000")
    server.amm_deposit(carol, constants.XRP_ASSET,
                       usd,
                       lp_token_out=carol_lpt_out,
                       mode="tfLPToken")

    carol_withdraw = dict(usd, value="100")
    eprice = dict(lpt, value="53")
    withdraw_response = server.amm_withdraw(carol, constants.XRP_ASSET,
                                            usd,
                                            carol_withdraw,
                                            eprice=eprice,
                                            mode="tfLimitLPToken")
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_INVALID_TOKENS")


def test_withdraw_single_asset_effective_price_zero(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "1000",
    }

    usd_payment = dict(usd, value="10000")
    server.create_trustline(alice, usd)
    server.create_trustline(carol, usd)
    server.make_payment(gw, alice, usd_payment)
    server.make_payment(gw, carol, usd_payment)

    server.set_default_ripple(gw)
    server.amm_create(alice, xrp, usd)
    lpt = server.get_amm_lp_token(constants.XRP_ASSET, usd)

    carol_lpt_out = dict(lpt, value="10000")
    server.amm_deposit(carol, constants.XRP_ASSET, usd, lp_token_out=carol_lpt_out, mode="tfLPToken")

    carol_withdraw = dict(usd, value="100")
    eprice = dict(lpt, value="0")
    withdraw_response = server.amm_withdraw(
        carol, constants.XRP_ASSET, usd, carol_withdraw, eprice=eprice, mode="tfLimitLPToken"
    )
    test_validator.verify_test(server, withdraw_response, response_result="temBAD_AMOUNT")


def test_withdraw_single_asset_withdraw_all(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    max_deposit_amount = "9000000"


    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfOneAssetWithdrawAll"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
        },
        "secret": alice.master_seed,
    }
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_withdraw_all_in_same_ledger(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2, wait_for_ledger_close=False)
    max_deposit_amount = "9000000"

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfOneAssetWithdrawAll"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
        },
        "secret": alice.master_seed,
    }
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_withdraw_all_zero_amount(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    max_deposit_amount = "0"

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfOneAssetWithdrawAll"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "Account": alice.account_id,
        },
        "secret": alice.master_seed,
    }
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="tecAMM_BALANCE")


def test_withdraw_single_asset_bob_withdraw_all_zero_amount(fx_rippled):
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
    max_deposit_amount = "0"
    bob_payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    server.create_trustline(bob, asset_2)
    server.make_payment(alice, bob.account_id, bob_payment)
    bob_lp_payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(alice, bob.account_id, bob_lp_payment)
    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfOneAssetWithdrawAll"],
            "Asset": constants.XRP_ASSET,
            "Amount": max_deposit_amount,
            "Asset2": asset_2,
            "Account": bob.account_id,
        },
        "secret": bob.master_seed,
    }
    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_tfLPToken(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    lptoken = server.get_amm_lp_token(asset_1, asset_2)
    lptoken_in = dict(lptoken, value="5000")

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfLPToken"],
            "Asset": asset_1,
            "LPTokenIn": lptoken_in,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_single_asset_withdraw_global_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    server.set_global_freeze(alice)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response, response_result='tecFROZEN')


def test_withdraw_single_asset_withdraw_frozen_trustline(fx_rippled):
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
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)
    alice_asset = dict(asset_2, issuer=alice.account_id)
    server.freeze_trustline(gw, alice_asset)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response, response_result='tecFROZEN')


def test_withdraw_withdrawall_EPrice_invalid(fx_rippled):
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
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfWithdrawAll"],
            "Asset": asset_1,
            "Asset2": asset_2,
            "EPrice": "10",
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temMALFORMED")


def test_withdraw_withdrawall_removes_amm(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    payload = {
        "secret": alice.master_seed,
        "tx_json": {
            "Account": alice.account_id,
            "Asset": constants.XRP_ASSET,
            "Asset2": asset_2,
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfWithdrawAll"],
            "TransactionType": "AMMWithdraw",
        },
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response)
    amm_info_response = server.amm_info(constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, amm_info_response, response_result="actNotFound")


def test_withdraw_two_asset_withdrawal(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL
    amount2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, amount2, mode="tfTwoAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_two_asset_withdrawal_both_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USA",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_2 = {
        "currency": "DSA",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    server.amm_create(alice, asset_1, asset_2)
    amount = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)
    amount2 = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)
    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, amount2, mode="tfTwoAsset")
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_two_asset_withdraw_all(fx_rippled):
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
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfWithdrawAll"],
            "Asset": asset_1,
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_two_asset_withdraw_all_with_wrong_params(fx_rippled):
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
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfWithdrawAll"],
            "Asset": asset_1,
            "Amount": "10000000",
            "Asset2": asset_2,
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
        },
        "secret": alice.master_seed,
    }

    withdraw_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, withdraw_response, response_result="temMALFORMED")


def test_withdraw_two_asset_LimitLPToken(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    cny = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": "10000000",
    }
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": "1000",
    }

    usd_payment = dict(usd, value="10000")
    cny_payment = dict(cny, value="20000000")
    server.create_trustline(alice, usd)
    server.create_trustline(alice, cny)
    server.create_trustline(carol, usd)
    server.create_trustline(carol, cny)
    server.make_payment(gw, alice, usd_payment)
    server.make_payment(gw, alice, cny_payment)
    server.make_payment(gw, carol, usd_payment)
    server.make_payment(gw, carol, cny_payment)

    server.set_default_ripple(gw)
    server.amm_create(alice, cny, usd)
    lpt = server.get_amm_lp_token(cny, usd)

    carol_lpt_out = dict(lpt, value="10000")
    server.amm_deposit(carol, cny, usd, lp_token_out=carol_lpt_out, mode="tfLPToken")

    carol_withdraw = dict(usd, value="100")
    eprice = dict(lpt, value="52")
    withdraw_response = server.amm_withdraw(
        carol, cny, usd, carol_withdraw, eprice=eprice, mode="tfLimitLPToken"
    )
    test_validator.verify_test(server, withdraw_response)


def test_withdraw_two_asset_withdraw_global_freeze(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2 = {
        "currency": "GBP",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    server.amm_create(gw, asset_1, asset_2)
    amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    server.set_global_freeze(gw)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response, response_result='tecFROZEN')


def test_withdraw_two_asset_withdraw_frozen_trustline(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2 = {
        "currency": "GBP",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    usd = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    gbp = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    server.create_trustline(alice, asset_1)
    server.create_trustline(alice, asset_2)
    server.make_payment(gw, alice.account_id, usd)
    server.make_payment(gw, alice.account_id, gbp)
    server.amm_deposit(alice, asset_1, asset_2, usd)
    server.amm_deposit(alice, asset_1, asset_2, gbp)
    alice_gbt = dict(asset_2, issuer=alice.account_id)
    server.freeze_trustline(gw, alice_gbt)
    withdraw_amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, withdraw_amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response, response_result='tecFROZEN')


def test_withdraw_two_asset_withdraw_frozen_trustline_withdraw_nonfrozen(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    asset_2 = {
        "currency": "GBP",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    usd = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    gbp = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)
    server.create_trustline(alice, asset_1)
    server.create_trustline(alice, asset_2)
    server.make_payment(gw, alice.account_id, usd)
    server.make_payment(gw, alice.account_id, gbp)
    server.amm_deposit(alice, asset_1, asset_2, usd)
    server.amm_deposit(alice, asset_1, asset_2, gbp)
    alice_gbt = dict(asset_2, issuer=alice.account_id)
    server.freeze_trustline(gw, alice_gbt)
    withdraw_amount = dict(asset_1, value=constants.DEFAULT_AMM_TOKEN_WITHDRAWAL)

    withdraw_response = server.amm_withdraw(alice, asset_1, asset_2, withdraw_amount, mode="tfSingleAsset")
    test_validator.verify_test(server, withdraw_response)
