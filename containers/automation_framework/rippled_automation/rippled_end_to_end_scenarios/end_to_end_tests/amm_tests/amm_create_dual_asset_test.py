import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

log = log_helper.get_logger()


@pytest.mark.smoke
def test_create_two_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_require_default_rippling_set(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

    payload = {
        "tx_json": {
            "TransactionType": "AMMCreate",
            "Account": account_1.account_id,
            "Fee": constants.DEFAULT_AMM_CREATE_FEE,
            "TradingFee": constants.DEFAULT_AMM_TRADING_FEE,
            "Amount": asset_1,
            "Amount2": asset_2,
        }
    }

    response = server.execute_transaction(secret=account_1.master_seed, payload=payload)
    test_validator.verify_test(server, response, response_result="terNO_RIPPLE")


def test_create_two_asset_from_nonexistent_account(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=False)

    asset_1 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }
    asset_2 = {
        "currency": "CNY",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }
    payload = {
                "tx_json": {
                    "TransactionType": "AMMCreate",
                    "Account": account_1.account_id,
                    "Fee": constants.DEFAULT_AMM_CREATE_FEE,
                    "TradingFee": constants.DEFAULT_AMM_TRADING_FEE,
                    "Amount": asset_1,
                    "Amount2": asset_2,
                }
    }

    response = server.execute_transaction(secret=account_1.master_seed, payload=payload)
    test_validator.verify_test(server, response, response_result="srcActNotFound")


def test_create_two_asset_xrp_tkn_amm_creator_not_token_issuer(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    server.set_default_ripple(alice)

    asset_1 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(gw, asset_1)
    server.create_trustline(gw, asset_2)
    server.make_payment(alice, gw.account_id, asset_1)
    server.make_payment(alice, gw.account_id, asset_2)

    response = server.amm_create(gw, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_zero_tkn(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": "0"}
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT}
    asset_3 = {"currency": "USD", "issuer": account_1.account_id, "value": "0"}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="temBAD_AMM_TOKENS")
    response = server.amm_create(account_1, asset_2, asset_1)
    test_validator.verify_test(server, response, response_result="temBAD_AMM_TOKENS")
    response = server.amm_create(account_1, asset_1, asset_3)
    test_validator.verify_test(server, response, response_result="temBAD_AMM_TOKENS")


def test_create_two_asset_zero_tkn_integer(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": 00}
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": 00}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="temBAD_AMM_TOKENS")


def test_create_two_asset_zero_tkn_string(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": "00"}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": "00"}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="invalidParams")


def test_create_two_asset_negative_tkn(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    negative_value = int(constants.DEFAULT_AMM_TOKEN_CREATE) * -1
    for sign in [1, -1]:
        value_1 = str(negative_value * sign)
        value_2 = str(negative_value * -sign)
        asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": value_1}
        asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": value_2}

        response = server.amm_create(account_1, asset_1, asset_2)
        test_validator.verify_test(server, response, response_result="temBAD_AMOUNT")


def test_create_two_asset_negative_tkn_both_negative(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    negative_value = str((int(constants.DEFAULT_AMM_TOKEN_CREATE) * -1))

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": negative_value}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": negative_value}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="temBAD_AMOUNT")


def test_create_two_asset_both_assets_same_tkn(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="temBAD_AMM_TOKENS")


def test_create_two_asset_duplicate_amm(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)

    test_validator.verify_test(server, response)
    response = server.amm_create(account_1, asset_1, asset_2)

    test_validator.verify_test(server, response, response_result="tecDUPLICATE")


def test_create_two_asset_account_has_multiple_amms(fx_rippled):
    server = fx_rippled["rippled_server"]
    account_1 = server.create_account(fund=True, amount=80000000)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_3 = {"currency": "XBT", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response_1 = server.amm_create(account_1, asset_1, asset_2)
    response_2 = server.amm_create(account_1, asset_1, asset_3)
    response_3 = server.amm_create(account_1, asset_2, asset_3)

    test_validator.verify_test(server, response_1)
    test_validator.verify_test(server, response_2)
    test_validator.verify_test(server, response_3)


def test_create_two_asset_another_account_creates_existing_amm(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response_1 = server.amm_create(account_1, asset_1, asset_2)
    response_2 = server.amm_create(account_2, asset_1, asset_2)

    test_validator.verify_test(server, response_1)
    test_validator.verify_test(server, response_2, response_result="tecDUPLICATE")


def test_create_two_asset_insufficient_token_balance(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    server.set_default_ripple(gw)

    asset_1 = {"currency": "USD", "issuer": gw.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": gw.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(alice, asset_1)
    server.create_trustline(alice, asset_2)

    asset_1_payment = dict(asset_1, value="1000")
    asset_2_payment = dict(asset_2, value="1000")

    server.make_payment(gw, alice, asset_1_payment)
    server.make_payment(gw, alice, asset_2_payment)

    asset_1_payment = dict(asset_1, value="1001")

    response = server.amm_create(alice, asset_1_payment, asset_2_payment)
    test_validator.verify_test(server, response, response_result="tecUNFUNDED_AMM")


def test_create_two_asset_cant_cover_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    fee = str(int(server.get_account_balance(account_1.account_id)) + 1)

    response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
    test_validator.verify_test(server, response, response_result="terINSUF_FEE_B")


def test_create_two_asset_invalid_hex_currency(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    hex0 = "0000415500000000DEADBEEFECB0BAC600000000"
    hex1 = "0000415500000000CAFEBABEECB0BAC600000000"

    asset_1 = {"currency": hex0, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": hex1, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_valid_hex_currency(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    hex0 = "1212415500000000DEADBEEFECB0BAC600000000"
    hex1 = "1234415500000000CAFEBABEECB0BAC600000000"

    asset_1 = {"currency": hex0, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": hex1, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_non_ascii_currency(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    a1 = "#˚∆"
    a2 = "∆∆∆"

    asset_1 = {"currency": a1, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": a2, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="invalidParams")


def test_create_two_asset_currency_with_symbols(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    a1 = "(o)"
    a2 = "O))"

    asset_1 = {"currency": a1, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": a2, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_xrp_token_nonexistent_issuer(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=False)

    asset_1 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    payload = {
        "tx_json": {
            "TransactionType": "AMMCreate",
            "Account": alice.account_id,
            "Fee": constants.DEFAULT_AMM_CREATE_FEE,
            "TradingFee": constants.DEFAULT_AMM_TRADING_FEE,
            "Amount": asset_1,
            "Amount2": asset_2,
        }
    }

    response = server.execute_transaction(secret=alice.master_seed, payload=payload)
    test_validator.verify_test(server, response, response_result="srcActNotFound")


def test_create_two_asset_require_nonzero_xrp_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    zero_fees = ["-0", "0"]

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for fee in zero_fees:
        response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
        test_validator.verify_test(server, response, response_result="telINSUF_FEE_P")


def test_create_two_asset_create_bad_xrp_fees(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    bad_fees = ["-100000000000000000", "-1"]

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for fee in bad_fees:
        response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
        test_validator.verify_test(server, response, response_result="temBAD_FEE")


def test_create_two_asset_create_huge_bad_negative_xrp_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    fee = "-100000000000000001"

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2, fee=fee)

    test_validator.verify_test(server, response, response_result="invalidParams")


def test_create_two_asset_create_trading_fee_required(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    payload = {
                "tx_json": {
                    "TransactionType": "AMMCreate",
                    "Account": account_1.account_id,
                    "Fee": constants.DEFAULT_AMM_CREATE_FEE,
                    # "TradingFee": trading_fee,
                    "Amount": asset_1,
                    "Amount2": asset_2,
                }
            }
    response = server.execute_transaction(secret=account_1.master_seed, payload=payload)
    test_validator.verify_test(server, response, response_result="invalidParams")


def test_create_two_asset_create_zero_trading_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    trading_fee = "0"

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
    test_validator.verify_test(server, response)


def test_create_two_asset_create_trading_fee_over_max(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    trading_fee = str(int(constants.MAX_AMM_TRADING_FEE) + 1)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
    test_validator.verify_test(server, response, response_result="temBAD_FEE")


def test_create_two_asset_create_bad_trading_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    bad_trading_fees = ["-100000000", "-1", "-0", "badfee"]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for trading_fee in bad_trading_fees:
        response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
        test_validator.verify_test(server, response, response_result="invalidParams")


def test_create_two_asset_create_trading_fee_above_max(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    trading_fee = str(int(constants.MAX_AMM_TRADING_FEE) + 1)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)

    test_validator.verify_test(server, response, response_result="temBAD_FEE")


def test_create_two_asset_both_unfrozen_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.set_global_freeze(account_1)
    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response, response_result="tecFROZEN")

    server.unset_global_freeze(account_1)
    response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, response)


def test_create_two_asset_from_lp_tokens(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }
    usa = {
        "currency": "USA",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
        }

    response = server.amm_create(gw, usd, usa)

    lp_token = server.get_amm_lp_token(usd, usa)
    server.create_trustline(alice, usd)
    server.create_trustline(alice, lp_token)

    lp_payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    usd_payment = dict(usd, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    server.make_payment(gw, alice.account_id, usd_payment)
    server.make_payment(gw, alice.account_id, lp_payment)

    response = server.amm_create(alice, usd_payment, lp_payment)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_create_two_asset_both_assets_lp_tokens(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_1 = {
        "currency": "USA",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_2 = {
        "currency": "USB",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_3 = {
        "currency": "USC",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, asset_1, asset_2)
    server.amm_create(account_1, asset_1, asset_3)

    lp_token_1 = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_2 = server.get_amm_lp_token(asset_1, asset_3)

    server.create_trustline(account_2, lp_token_1)
    server.create_trustline(account_2, lp_token_2)

    lp_value = constants.DEFAULT_AMM_TOKEN_CREATE
    lp_token_1_payment = dict(lp_token_1, value=lp_value)
    lp_token_2_payment = dict(lp_token_2, value=lp_value)

    server.make_payment(account_1, account_2.account_id, lp_token_1_payment)
    server.make_payment(account_1, account_2.account_id, lp_token_2_payment)

    response = server.amm_create(account_2, lp_token_1_payment, lp_token_2_payment)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_create_two_asset_from_clawbackable_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)

    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT
    }
    cny_asset = {
        "currency": "CNY",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT
    }

    server.account_set(gw, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    amm_create_response = server.amm_create(gw, usd_asset, cny_asset)
    test_validator.verify_test(server, amm_create_response, response_result='tecNO_PERMISSION')
