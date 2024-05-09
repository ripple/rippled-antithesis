import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

log = log_helper.get_logger()


@pytest.mark.smoke
def test_create_single_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response, accounts=[alice])


def test_create_single_asset_require_default_rippling_set(fx_rippled):
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

    create_amm_response = server.execute_transaction(secret=account_1.master_seed, payload=payload)
    test_validator.verify_test(server, create_amm_response, response_result="terNO_RIPPLE")


def test_create_single_asset_from_nonexistent_account(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=False)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
                "currency": "USD",
                "issuer": alice.account_id,
                "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

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

    amm_response = server.execute_transaction(secret=alice.master_seed, payload=payload)
    test_validator.verify_test(server, amm_response, accounts=[alice], response_result="srcActNotFound")


def test_create_single_asset_xrp_tkn_amm_creator_not_token_issuer(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_2.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(account_1, asset_2)
    server.make_payment(account_2, account_1.account_id, asset_2)
    server.set_default_ripple(account_2)

    amm_create_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response)


def test_create_single_asset_zero_tkn(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": "0"}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)

    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMOUNT")


def test_create_single_asset_zero_tkn_integer(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": 00}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMOUNT")

# REVIEW: Should this be invalid params?
def test_create_single_asset_zero_tkn_string_equivalent_zero(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "CNY", "issuer": account_1.account_id, "value": "00"}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="invalidParams")


def test_create_single_asset_zero_xrp(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = "0"
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMOUNT")


def test_create_single_asset_negative_xrp(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    negative_xrp = str((int(constants.DEFAULT_AMM_XRP_CREATE) * -1))

    asset_1 = negative_xrp
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMOUNT")


def test_create_single_asset_negative_tkn(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    negative_tkn = str((int(constants.DEFAULT_AMM_TOKEN_CREATE) * -1))

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": negative_tkn}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMOUNT")


def test_create_single_asset_both_assets_xrp(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = "10"
    asset_2 = "10"

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)

    test_validator.verify_test(server, create_amm_response, response_result="temBAD_AMM_TOKENS")


def test_create_single_asset_duplicate_amm(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response)

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="tecDUPLICATE")


def test_create_single_asset_account_has_multiple_amms(fx_rippled):
    server = fx_rippled["rippled_server"]

    account_1 = server.create_account(fund=True, amount=50_000_000)
    #  With 50 XRP, the account ends up with 16 XRP and the reserve is 14, so with 40 XRP, it's not enough to create 2 AMMs

    asset_1 = int(constants.DEFAULT_AMM_XRP_CREATE)
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}
    asset_3 = {"currency": "CNY", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response_1 = server.amm_create(account_1, asset_1, asset_2)
    create_amm_response_2 = server.amm_create(account_1, asset_1, asset_3)

    test_validator.verify_test(server, create_amm_response_1)
    test_validator.verify_test(server, create_amm_response_2)


def test_create_single_asset_another_account_creates_existing_amm(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response_1 = server.amm_create(account_1, asset_1, asset_2)
    create_amm_response_2 = server.amm_create(account_2, asset_1, asset_2)

    test_validator.verify_test(server, create_amm_response_1)
    test_validator.verify_test(server, create_amm_response_2, response_result="tecDUPLICATE")


def test_create_single_asset_creator_insufficient_balance(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = str(int(server.get_account_balance(account_1.account_id)) + 1)
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="tecUNFUNDED_AMM")


def test_create_single_asset_cant_cover_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    fee = str(int(server.get_account_balance(account_1.account_id)) + 1)

    create_amm_response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
    test_validator.verify_test(server, create_amm_response, response_result="terINSUF_FEE_B")


def test_create_single_asset_invalid_hex_currency(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    hex0 = "0000415500000000DEADBEEFECB0BAC600000000"

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": hex0, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response)


def test_create_single_asset_valid_hex_currency(fx_rippled):
    server = fx_rippled['rippled_server']

    account_1 = server.create_account(fund=True)

    hex0 = "1234415500000000DEADBEEFECB0BAC600000000"

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": hex0, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response)


def test_create_single_asset_non_ascii_currency(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "∆∆∆", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response, response_result="invalidParams")


def test_create_single_asset_currency_with_symbols(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    a2 = "(o)"
    asset_2 = {"currency": a2, "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT}
    amm_create_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, amm_create_response)


def test_create_single_asset_nonexistent_token_issuer(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.wallet_propose()

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_2["account_id"], "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="tecUNFUNDED_AMM")


def test_create_single_asset_require_nonzero_xrp_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    zero_fees = ["-0", "0"]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for fee in zero_fees:
        create_amm_response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
        test_validator.verify_test(server, create_amm_response, response_result="telINSUF_FEE_P")


def test_create_single_asset_bad_xrp_fees(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    bad_fees = ["-100000000000000000", "-1"]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for fee in bad_fees:
        create_amm_response = server.amm_create(account_1, asset_1, asset_2, fee=fee)
        test_validator.verify_test(server, create_amm_response, response_result="temBAD_FEE")


def test_create_single_asset_huge_bad_negative_xrp_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    fee = "-100000000000000001"

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2, fee=fee)

    test_validator.verify_test(server, create_amm_response, response_result="invalidParams")


def test_create_single_asset_trading_fee_required(fx_rippled):
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
                    "Amount": asset_1,
                    "Amount2": asset_2,
                }
            }
    create_amm_response = server.execute_transaction(secret=account_1.master_seed, payload=payload)
    test_validator.verify_test(server, create_amm_response, response_result="invalidParams")


def test_create_single_asset_zero_trading_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    trading_fee = "0"

    create_amm_response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
    test_validator.verify_test(server, create_amm_response)


def test_create_single_asset_bad_trading_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    bad_trading_fees = ["-100000000", "-1", "-0", "badfee"]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    for trading_fee in bad_trading_fees:
        create_amm_response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
        test_validator.verify_test(server, create_amm_response, response_result="invalidParams")


def test_create_single_asset_trading_fee_above_max(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    trading_fee = str(int(constants.MAX_AMM_TRADING_FEE) + 1)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    create_amm_response = server.amm_create(account_1, asset_1, asset_2, trading_fee=trading_fee)
    test_validator.verify_test(server, create_amm_response, response_result="temBAD_FEE")


def test_create_single_asset_with_frozen_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.set_global_freeze(account_1)
    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="tecFROZEN")


def test_create_single_asset_with_unfrozen_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": account_1.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.set_global_freeze(account_1)
    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response, response_result="tecFROZEN")

    server.unset_global_freeze(account_1)
    create_amm_response = server.amm_create(account_1, asset_1, asset_2)
    test_validator.verify_test(server, create_amm_response)


def test_create_single_asset_from_lptokens(fx_rippled):
    server = fx_rippled['rippled_server']
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    asset_2 = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(account_1, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(account_2, lp_token)

    lpt_payment = dict(lp_token, value=2)
    server.make_payment(account_1, account_2.account_id, lpt_payment)

    create_amm_response = server.amm_create(account_2, constants.DEFAULT_AMM_XRP_CREATE, lpt_payment)
    test_validator.verify_test(server, create_amm_response, response_result="tecAMM_INVALID_TOKENS")


def test_create_single_asset_from_clawbackable_asset(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)

    xrp_asset = constants.DEFAULT_AMM_XRP_CREATE
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE
    }

    server.account_set(gw, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    amm_create_response = server.amm_create(gw, xrp_asset, usd_asset)
    test_validator.verify_test(server, amm_create_response, response_result='tecNO_PERMISSION')
