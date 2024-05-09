import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

log = log_helper.get_logger()


@pytest.mark.smoke
def test_bid_no_min_or_max(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    asset_1 = constants.XRP_ASSET
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    bid_response = server.amm_bid(alice, asset_1, asset_2)
    test_validator.verify_test(server, bid_response)


def test_bid_min(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)
    alice_bid = dict(lp_token, value="4")

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_max(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)

    server.create_trustline(bob, asset_2)
    server.create_trustline(bob, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)
    alice_bid = dict(lp_token, value="3")
    bob_bid = dict(lp_token, value="4")

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)
    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_with_no_lp_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_default_bid_exceeds_lp_balance(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)

    alice_payment = dict(lp_token, value="20")
    alice_bid = dict(lp_token, value="5")
    bob_payment = dict(lp_token, value="1")
    server.make_payment(gw, alice, alice_payment)
    server.make_payment(gw, bob, bob_payment)
    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_exceeds_lp_balance(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)

    alice_payment = dict(lp_token, value="10")
    bob_payment = dict(lp_token, value="4")
    server.make_payment(gw, alice, alice_payment)
    server.make_payment(gw, bob, bob_payment)

    alice_bid = dict(alice_payment, value="5")
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bob_bid = dict(bob_payment, value="5")

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmax_exceeds_lp_balance(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)

    alice_payment = dict(lp_token, value="10")
    bob_payment = dict(lp_token, value="4")
    server.make_payment(gw, alice, alice_payment)
    server.make_payment(gw, bob, bob_payment)

    alice_bid = dict(alice_payment, value="5")
    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bob_bid = dict(bob_payment, value="5")
    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmax_over_current_bid(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, asset_2)
    server.create_trustline(bob, lp_token)

    alice_bid = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    bob_bid = dict(lp_token, value=str(int(alice_bid["value"]) + 1))
    payment = dict(lp_token, value=10)

    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_bidmin_over_current_bid(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, asset_2)
    server.create_trustline(bob, lp_token)

    alice_bid = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    bob_bid = dict(lp_token, value=str(int(alice_bid["value"]) + 1))
    payment = dict(lp_token, value=10)

    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_bidmax_too_low(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, asset_2)

    alice_bid = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    bob_bid = dict(lp_token, value=str(int(alice_bid["value"]) - 1))
    payment = dict(lp_token, value="10")
    usd_payment = dict(asset_2, value="10")
    server.make_payment(gw, bob, usd_payment)

    server.amm_deposit(bob, constants.XRP_ASSET, asset_2, usd_payment)
    server.make_payment(gw, alice, payment)

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=alice_bid)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_FAILED")


def test_bid_nonexistent_bidder(fx_rippled):
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

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="srcActNotFound")


def test_bid_nonexistent_amm(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)

    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    bid_response = server.amm_bid(gw, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="terNO_AMM")


def test_bid_nonexistent_issuer(fx_rippled):
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
    asset_2["issuer"] = alice.account_id
    bid_response = server.amm_bid(gw, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="terNO_AMM")


def test_bid_initial_bidmax_then_bid(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(alice, asset_2)
    server.create_trustline(bob, asset_2)

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)

    payment = dict(lp_token, value="100")
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_max = dict(lp_token, value="10")

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_max=lp_token_max)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response)


def test_bid_bidmin_and_bidmax_equal_above_current_price(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)
    payment = dict(lp_token, value=100)
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)
    lp_token_min = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    lp_token_max = dict(lp_token, value=constants.DEFAULT_AMM_BID)

    inital_bid = dict(lp_token, value=str(int(constants.DEFAULT_AMM_BID) - 1))

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=inital_bid)
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=lp_token_min, bid_max=lp_token_max)
    test_validator.verify_test(server, bid_response)


def test_bid_bidmin_and_bidmax_equal_below_current_price(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)
    payment = dict(lp_token, value=100)
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)
    lp_token_min = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    lp_token_max = dict(lp_token, value=constants.DEFAULT_AMM_BID)

    inital_bid = dict(lp_token, value=str(int(constants.DEFAULT_AMM_BID) + 1))

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=inital_bid)
    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=lp_token_min, bid_max=lp_token_max)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_FAILED")


def test_bid_bidmin_and_bidmax_equal_at_current_price(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)
    payment = dict(lp_token, value="100")
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)

    lp_token_min = dict(lp_token, value=constants.DEFAULT_AMM_BID)
    lp_token_max = dict(lp_token, value=constants.DEFAULT_AMM_BID)

    inital_bid = dict(lp_token, value=constants.DEFAULT_AMM_BID)

    server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=inital_bid)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=lp_token_min, bid_max=lp_token_max)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_FAILED")


def test_bid_crossed_min_and_max(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(alice, lp_token)
    server.create_trustline(bob, lp_token)
    payment = dict(lp_token, value="100")
    server.make_payment(gw, alice, payment)
    server.make_payment(gw, bob, payment)
    lp_token_min = dict(lp_token, value="10")
    lp_token_max = dict(lp_token, value="1")

    bob_bid = dict(lp_token, value="5")

    server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=lp_token_min, bid_max=lp_token_max)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_zero(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    bid = "0"

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=bid)
    test_validator.verify_test(server, bid_response, response_result="temBAD_AMOUNT")


def test_bid_min_negative(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    bad_bid = -1
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=bad_bid)
    test_validator.verify_test(server, bid_response, response_result="temBAD_AMOUNT")


def test_bid_bidmin_string(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    bad_bid = "string"
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_min=bad_bid)
    test_validator.verify_test(server, bid_response, response_result="invalidParams")


def test_bid_bidmax_zero(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    bid = "0"

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_max=bid)
    test_validator.verify_test(server, bid_response, response_result="temBAD_AMOUNT")


def test_bid_bidmax_negative(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    bad_bid = -1
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_max=bad_bid)
    test_validator.verify_test(server, bid_response, response_result="temBAD_AMOUNT")


def test_bid_bidmax_string(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    bad_bid = "string"
    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, bid_max=bad_bid)
    test_validator.verify_test(server, bid_response, response_result="invalidParams")


def test_bid_flag_incorrect(fx_rippled):
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
            "TransactionType": "AMMBid",
            "Account": alice.account_id,
            "Asset": constants.XRP_ASSET,
            "Asset2": asset_2,
            "Flags": 10,
        },
    }

    bid_response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, bid_response, response_result="temINVALID_FLAG")


def test_bid_bidmax_with_lp_asset(fx_rippled):
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

    bob_payment = dict(asset_2, value="10")
    server.make_payment(alice, bob, bob_payment)
    bob_bid = dict(asset_2, value="5")

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_with_lp_asset(fx_rippled):
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
    bob_payment = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(alice, bob, bob_payment)

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_payment)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmax_with_other_amm_lp_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_3 = {
        "currency": "USD",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)
    server.amm_create(bob, asset_1, asset_3)
    bob_bid = dict(asset_3, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_with_other_amm_lp_token(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    asset_3 = {
        "currency": "USD",
        "issuer": bob.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)
    server.amm_create(bob, asset_1, asset_3)
    bob_bid = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmax_with_wrong_lp_token_issuer(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    server.create_trustline(bob, asset_2)

    server.amm_create(alice, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)

    bob_bid = dict(lp_token, issuer=bob.account_id, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_with_wrong_lp_token_issuer(fx_rippled):
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
    bob_bid = dict(asset_2, issuer=bob.account_id, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_has_no_lp_tokens(fx_rippled):
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

    bob_bid = (lp_token := server.get_amm_lp_token(asset_1, asset_2))
    server.create_trustline(bob, lp_token)

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmin_lacks_sufficient_lp_tokens(fx_rippled):
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
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    bob_payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(alice, bob, bob_payment)
    bob_bid = dict(bob_payment, value=str(int(bob_payment["value"]) + 1))

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_bidmax_lacks_sufficient_lp_tokens(fx_rippled):
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
    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    bob_payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(alice, bob, bob_payment)
    bob_bid = dict(bob_payment, value=str(int(bob_payment["value"]) + 1))

    response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_max=bob_bid)
    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_bid_outbid_zero_with_no_params(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)
    carol = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.create_trustline(carol, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    server.create_trustline(carol, lp_token)

    payment = dict(lp_token, value="1000")
    server.make_payment(alice, bob, payment)
    server.make_payment(alice, carol, payment)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response)

    bid_response = server.amm_bid(carol, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response)


def test_bid_outbid_bidmin_with_no_params(fx_rippled):
    server = fx_rippled["rippled_server"]
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)
    carol = server.create_account(fund=True)
    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.create_trustline(carol, asset_2)

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    server.create_trustline(carol, lp_token)

    payment = dict(lp_token, value="1000")
    server.make_payment(alice, bob, payment)
    server.make_payment(alice, carol, payment)

    bob_bid_min = dict(lp_token, value="100")
    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid_min)
    test_validator.verify_test(server, bid_response)

    bid_response = server.amm_bid(carol, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response)


def test_bid_outbid_with_bid_min(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    bob = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.create_trustline(carol, asset_2)

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    server.create_trustline(carol, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, bob, payment)
    server.make_payment(gw, carol, payment)

    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response)

    carol_bid = dict(payment, value="1")
    bid_response = server.amm_bid(carol, constants.XRP_ASSET, asset_2, bid_min=carol_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_outbid_with_bid_max(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    bob = server.create_account(fund=True)
    carol = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, asset_2)
    server.create_trustline(carol, asset_2)

    server.amm_create(gw, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    server.create_trustline(carol, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, bob, payment)
    server.make_payment(gw, carol, payment)

    bob_bid = dict(payment, value=str(int(payment["value"]) - 2))
    bid_response = server.amm_bid(bob, constants.XRP_ASSET, asset_2, bid_min=bob_bid)
    test_validator.verify_test(server, bid_response)

    carol_low_bid = dict(payment, value=str(int(bob_bid["value"]) - 1))
    bid_response = server.amm_bid(carol, constants.XRP_ASSET, asset_2, bid_max=carol_low_bid)
    test_validator.verify_test(server, bid_response, response_result="tecAMM_FAILED")

    carol_high_bid = dict(payment, value=str(int(bob_bid["value"]) + 1))
    bid_response = server.amm_bid(carol, constants.XRP_ASSET, asset_2, bid_max=carol_high_bid)
    test_validator.verify_test(server, bid_response)


def test_bid_authaccounts(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    auth_account = server.create_account(fund=True).account_id

    auth_account_list = [{"AuthAccount": {"Account": auth_account}}]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, lp_token)
    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, auth_accounts=auth_account_list)
    test_validator.verify_test(server, bid_response)


def test_bid_too_many_authaccounts(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    auth_accounts = [{"AuthAccount": {"Account": server.create_account(fund=True).account_id}} for i in range(5)]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, lp_token)
    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, auth_accounts=auth_accounts)
    test_validator.verify_test(server, bid_response, response_result="temMALFORMED")


def test_bid_authaccount_nonexistent(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    auth_accounts = [{"AuthAccount": {"Account": server.create_account(fund=False).account_id}}]

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)
    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(alice, lp_token)
    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    server.make_payment(gw, alice, payment)

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2, auth_accounts=auth_accounts)
    test_validator.verify_test(server, bid_response, response_result="terNO_ACCOUNT")


def test_bid_amm_deleted(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, asset_1, asset_2)

    payload = {
        "tx_json": {
            "TransactionType": "AMMWithdraw",
            "Flags": constants.AMM_WITHDRAW_FLAGS["tfWithdrawAll"],
            "Asset": constants.XRP_ASSET,
            "Asset2": asset_2,
            "Account": gw.account_id,
        },
        "secret": gw.master_seed,
    }

    server.execute_transaction(payload=payload)

    bid_response = server.amm_bid(alice, constants.XRP_ASSET, asset_2)
    test_validator.verify_test(server, bid_response, response_result="terNO_AMM")
