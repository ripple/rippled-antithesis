import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils.amm.amm_helper import amm_vote_setup_voters

log = log_helper.get_logger()


@pytest.mark.smoke
def test_vote(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, xrp, usd)
    server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd, amount=constants.DEFAULT_AMM_XRP_DEPOSIT,)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd)
    test_validator.verify_test(server, response)


def test_vote_nonexistent_account(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=False)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, xrp, usd)

    response = server.amm_vote(bob, constants.XRP_ASSET, usd)
    test_validator.verify_test(server, response, response_result='srcActNotFound')


def test_vote_no_lp_tokens(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, xrp, usd)
    response = server.amm_vote(bob, constants.XRP_ASSET, usd)

    test_validator.verify_test(server, response, response_result="tecAMM_INVALID_TOKENS")


def test_vote_four_vote_ratio(fx_rippled):
    server = fx_rippled['rippled_server']
    accounts = {
        account_name: server.create_account(fund=True)
        for account_name in "gw alice bob carol dave".split()
    }

    xrp = str(int(constants.DEFAULT_AMM_XRP_CREATE) * 100)
    usd = {
        "currency": "USD",
        "issuer": accounts['gw'].account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    usd_amt = dict(usd, value=1000000)
    server.amm_create(accounts['gw'], usd_amt, 1000000)

    server.create_trustline(accounts['alice'], usd)
    server.create_trustline(accounts['bob'], usd)
    server.create_trustline(accounts['carol'], usd)
    server.create_trustline(accounts['dave'], usd)

    lp_token = server.get_amm_lp_token(xrp, usd)

    server.make_payment(accounts['gw'], accounts['alice'].account_id, usd_amt)
    server.make_payment(accounts['gw'], accounts['bob'].account_id, usd_amt)
    server.make_payment(accounts['gw'], accounts['carol'].account_id, usd_amt)
    server.make_payment(accounts['gw'], accounts['dave'].account_id, usd_amt)

    server.create_trustline(accounts['alice'], lp_token)
    server.create_trustline(accounts['bob'], lp_token)
    server.create_trustline(accounts['carol'], lp_token)
    server.create_trustline(accounts['dave'], lp_token)

    lp_balance = int(server.get_amm_lp_token(xrp, usd)['value'])
    lp_pay_amount = lp_balance // len(accounts)
    server.get_account_lines(accounts['alice'].account_id)
    lp_pay = dict(lp_token, value=lp_pay_amount)

    server.make_payment(accounts['gw'], accounts['alice'].account_id, lp_pay)
    server.make_payment(accounts['gw'], accounts['bob'].account_id, lp_pay)
    server.make_payment(accounts['gw'], accounts['carol'].account_id, lp_pay)
    server.make_payment(accounts['gw'], accounts['dave'].account_id, lp_pay)

    server.amm_vote(accounts['alice'], constants.XRP_ASSET, usd)
    server.amm_vote(accounts['bob'], constants.XRP_ASSET, usd)
    server.amm_vote(accounts['carol'], constants.XRP_ASSET, usd)
    response = server.amm_vote(accounts['dave'], constants.XRP_ASSET, usd)
    test_validator.verify_test(server, response)


def test_vote_eight_votes_already(fx_rippled):
    server = fx_rippled['rippled_server']
    n = 8
    alice, _, xrp, asset_2, accounts = amm_vote_setup_voters(server, n=n)
    server.amm_create(alice, xrp, asset_2)

    asset_1 = constants.XRP_ASSET

    deposit_amount = dict(asset_2, value=constants.DEFAULT_AMM_TOKEN_DEPOSIT)

    for i in range(n):
        log.info(f"Vote: #{i+1}")
        server.amm_deposit(accounts[i], asset_1=asset_1, amount=deposit_amount, asset_2=asset_2)
        response = server.amm_vote(accounts[i], asset_1, asset_2)

        test_validator.verify_test(server, response)


def test_vote_ninth_vote_holds_more_tokens(fx_rippled):
    server = fx_rippled['rippled_server']
    n = 7
    gw, alice, xrp, usd, accounts = amm_vote_setup_voters(server, n=n)

    server.amm_create(gw, xrp, usd)

    for i in range(n):
        server.amm_deposit(accounts[i], asset_1=constants.XRP_ASSET, amount=usd, asset_2=usd)
        log.debug(f"Vote: #{i+1}")
        response = server.amm_vote(accounts[i], constants.XRP_ASSET, usd)

    largest_amm_deposit = dict(usd, value='50')

    server.create_trustline(alice, usd)
    server.make_payment(gw, alice, largest_amm_deposit)

    server.amm_deposit(alice, asset_1=constants.XRP_ASSET, amount=largest_amm_deposit, asset_2=usd)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd)
    test_validator.verify_test(server, response)


def test_vote_for_fee_above_max_fee_allowed(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=True)

    trading_fee = str(int(constants.MAX_AMM_TRADING_FEE) + 1)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, xrp, usd)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd, trading_fee)
    test_validator.verify_test(server, response, response_result='temBAD_FEE')


def test_vote_for_nonexistent_amm(fx_rippled):
    server = fx_rippled['rippled_server']
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    cny = {
        "currency": "CNY",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.create_trustline(bob, usd)
    server.amm_create(alice, xrp, usd)

    payment = dict(usd, value='1000')
    server.make_payment(alice, bob.account_id, payment)

    deposit_amount = str(1000 - int(constants.DEFAULT_AMM_TOKEN_CREATE))
    deposit = dict(usd, value=deposit_amount)
    server.amm_deposit(bob, asset_1=constants.XRP_ASSET, amount=deposit, asset_2=usd)

    response = server.amm_vote(bob, constants.XRP_ASSET, cny)
    test_validator.verify_test(server, response, response_result='terNO_AMM')


def test_vote_string_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, xrp, usd)
    server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd, amount=constants.DEFAULT_AMM_XRP_DEPOSIT)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd, trading_fee='500')
    test_validator.verify_test(server, response)


def test_vote_bad_string_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, xrp, usd)
    server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd, amount=constants.DEFAULT_AMM_XRP_DEPOSIT)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd, trading_fee="string")
    test_validator.verify_test(server, response, response_result="invalidParams")


def test_vote_negative_fee(fx_rippled):
    server = fx_rippled['rippled_server']
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(gw, xrp, usd)

    server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd, amount=constants.DEFAULT_AMM_XRP_DEPOSIT)

    response = server.amm_vote(alice, constants.XRP_ASSET, usd, trading_fee=-1)
    test_validator.verify_test(server, response, response_result="invalidParams")
