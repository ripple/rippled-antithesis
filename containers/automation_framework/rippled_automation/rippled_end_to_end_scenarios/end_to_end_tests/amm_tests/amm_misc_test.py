import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.constants import PAYMENT_FLAG
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_amm_payment_simple_payment(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(bob, lp_token)
    amount = dict(lp_token, amount=constants.DEFAULT_TRANSFER_AMOUNT)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": amount,
        },
        "secret": alice.master_seed,
    }

    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_lp_tokens_back_to_amm_creator(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)

    server.create_trustline(bob, lp_token)
    server.create_trustline(alice, lp_token)
    server.make_payment(alice, bob, lp_token)

    payment_response = server.make_payment(bob, alice, lp_token)
    test_validator.verify_test(server, payment_response, accounts=[alice, bob])


def test_amm_payment_payment_submit_only_mode(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token,
        },
        "secret": alice.master_seed,
    }

    response = server.execute_transaction(payload=payload, submit_only=True)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_payment_with_more_than_balance(fx_rippled):
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

    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)
    server.create_trustline(bob, lp_token)
    value = str(int(server.get_amm_lp_token_balance(alice.account_id, asset_1, asset_2)) + 1)
    lp_token_payment = dict(lp_token, value=value)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }

    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="tecPATH_PARTIAL")


def test_amm_payment_payment_sign_master_hex(fx_rippled):
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

    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)
    lp_token_balance = server.get_amm_lp_token_balance(alice.account_id, constants.XRP_ASSET, asset_2)
    server.create_trustline(bob, lp_token)
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed_hex,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_payment_sign_master_key(fx_rippled):
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

    lp_token = server.get_amm_lp_token(constants.XRP_ASSET, asset_2)
    lp_token_balance = server.get_amm_lp_token_balance(alice.account_id, constants.XRP_ASSET, asset_2)
    server.create_trustline(bob, lp_token)
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_key,
    }

    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_payment_with_invalid_destination(fx_rippled):
    server = fx_rippled["rippled_server"]

    alice = server.create_account(fund=True)
    bob = server.create_account()

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_payment = lp_token
    server.create_trustline(bob, lp_token)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }

    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="tecNO_DST")


def test_amm_payment_payment_zero_lp_tokens(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_payment = dict(lp_token, value="0")
    server.create_trustline(bob, lp_token)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="temBAD_AMOUNT")


def test_amm_payment_payment_with_destination_tag(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "DestinationTag": 123,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_payment_with_invoice_id(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)

    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "InvoiceID": "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B",
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_amm_payment_payment_with_invalid_invoice_id(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)

    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "InvoiceID": 123,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="invalidParams")


def test_amm_payment_payment_to_self(fx_rippled):
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
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": alice.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice], response_result="temREDUNDANT")


def test_amm_payment_payment_with_no_source_address(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)

    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": "",
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="srcActMalformed")


def test_amm_payment_payment_with_no_destination_address(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": "",
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="invalidParams")


def test_amm_payment_payment_with_invalid_destination_address(fx_rippled):
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

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    lp_token_payment = lp_token

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": "invalid_address",
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob], response_result="invalidParams")


def test_amm_payment_payment_10_million_lp_tokens(fx_rippled):
    server = fx_rippled["rippled_server"]

    amount_to_transfer = "10000000"
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": str(15e6)}

    server.amm_create(alice, asset_1, asset_2)

    lp_token = server.get_amm_lp_token(asset_1, asset_2)
    server.create_trustline(bob, lp_token)
    lp_token_payment = dict(lp_token, value=amount_to_transfer)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": lp_token_payment,
        },
        "secret": alice.master_seed,
    }
    response = server.execute_transaction(payload=payload)
    test_validator.verify_test(server, response, accounts=[alice, bob])


def test_swap_through_amm_to_self(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    eth = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth)

    eth_alice_payment = dict(eth, value="1000")
    server.make_payment(gw, alice, eth_alice_payment)

    eth_self_payment = dict(eth, value="5")
    response = server.make_payment(alice, alice, eth_self_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice])


def test_swap_through_amm_to_self_no_default_ripple(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    eth = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    payload = {
        "tx_json": {
            "TransactionType": "AMMCreate",
            "Account": gw.account_id,
            "Fee": constants.DEFAULT_AMM_CREATE_FEE,
            "TradingFee": constants.DEFAULT_AMM_TOKEN_CREATE,
            "Amount": eth,
            "Amount2": constants.DEFAULT_AMM_XRP_CREATE,
        }
    }

    response = server.execute_transaction(secret=gw.master_seed, payload=payload)

    server.create_trustline(alice, eth)

    eth_alice_payment = dict(eth, value="1000")
    server.make_payment(gw, alice, eth_alice_payment)

    eth_self_payment = dict(eth, value="5")
    response = server.make_payment(alice, alice, eth_self_payment, send_max="10000000")
    test_validator.verify_test(server, response, response_result='tecPATH_DRY', accounts=[alice])


def test_swap_through_amm_to_another_account(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    eth1 = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth1, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth1)
    server.create_trustline(bob, eth1)

    eth1_alice_payment = dict(eth1, value="1000")
    server.make_payment(gw, alice, eth1_alice_payment)

    eth1_bob_payment = dict(eth1, value="5")
    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice])


def test_swap_globally_frozen_asset(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    eth1 = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth1, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth1)
    server.create_trustline(bob, eth1)

    eth1_alice_payment = dict(eth1, value="1000")
    server.make_payment(gw, alice, eth1_alice_payment)

    eth1_bob_payment = dict(eth1, value="5")
    server.set_global_freeze(gw)
    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice], response_result='tecPATH_PARTIAL')


def test_swap_individually_frozen_asset(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    eth1 = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth1, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth1)
    server.create_trustline(bob, eth1)

    eth1_alice_payment = dict(eth1, value="1000")
    server.make_payment(gw, alice, eth1_alice_payment)

    eth1_bob_payment = dict(eth1, value="5")
    alice_payment = dict(eth1, issuer=alice.account_id)
    server.freeze_trustline(gw, alice_payment)

    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice])


def test_swap_self_has_no_trustline(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)

    eth = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth, constants.DEFAULT_AMM_XRP_CREATE)

    eth_alice_payment = dict(eth, value="1000")
    server.make_payment(gw, alice, eth_alice_payment)

    eth_bob_payment = dict(eth, value="5")
    response = server.make_payment(alice, alice, eth_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice], response_result='tecPATH_DRY')


def test_swap_destination_account_has_no_trustline(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    eth1 = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth1, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth1)
    # server.create_trustline(bob, eth1) # destination has no trustline for received tokens

    eth1_alice_payment = dict(eth1, value="1000")
    server.make_payment(gw, alice, eth1_alice_payment)

    eth1_bob_payment = dict(eth1, value="5")
    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, accounts=[alice], response_result='tecPATH_DRY')


def test_swap_through_amm_to_another_account_with_deposit_auth_enabled(fx_rippled):
    server = fx_rippled["rippled_server"]
    gw = server.create_account(fund=True)
    alice = server.create_account(fund=True)
    bob = server.create_account(fund=True)

    eth1 = {
        "currency": "ETH",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    server.set_default_ripple(gw)
    server.amm_create(gw, eth1, constants.DEFAULT_AMM_XRP_CREATE)

    server.create_trustline(alice, eth1)
    server.create_trustline(bob, eth1)
    server.enable_deposit_auth(bob)

    eth1_alice_payment = dict(eth1, value="1000")
    server.make_payment(gw, alice, eth1_alice_payment)

    eth1_bob_payment = dict(eth1, value="5")
    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response, response_result='tecNO_PERMISSION')

    server.disable_deposit_auth(bob)
    eth1_bob_payment = dict(eth1, value="1")
    response = server.make_payment(alice, bob, eth1_bob_payment, send_max="10000000")
    test_validator.verify_test(server, response)


def test_create_offer_fulfilled_by_amm(fx_rippled):
    """
    gw is an issuer of ETH and has created an AMM with XRP/ETH at 10ETH per XRP
    Alice makes an offer for 2 ETH for 20 XRP
    """
    rippled = fx_rippled["rippled_server"]

    gw = rippled.create_account(fund=True)
    alice = rippled.create_account(fund=True)

    eth = {"currency": "ETH", "issuer": gw.account_id}

    rippled.set_default_ripple(gw)
    rippled.create_trustline(alice, eth)

    xrp_offer_amount = str(20_000000)
    eth_offer_amount = dict(eth, value=2)

    eth_buy_offer = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": xrp_offer_amount,
            "TakerPays": eth_offer_amount
        },
        "secret": alice.master_seed
    }

    amm_xrp_pool = str(20_000000)
    amm_eth_pool = dict(eth, value=4)

    rippled.amm_create(gw, amm_xrp_pool, amm_eth_pool)
    offer_response = rippled.execute_transaction(payload=eth_buy_offer)
    test_validator.verify_test(rippled, offer_response, offer_crossing=True, accounts=[alice])


@pytest.mark.skip(reason="Waiting to merge on develop: https://github.com/XRPLF/rippled/pull/4968/")
def test_payment_amm_synthetic_order_fill_usd_usd_different_issuer(fx_rippled):
    server = fx_rippled["rippled_server"]
    accounts = {
        "bitstamp": (bitstamp := server.create_account(fund=True, amount=str(5000_000000))),
        "gatehub": (gatehub := server.create_account(fund=True, amount=str(5000_000000))),
        "trader": (trader := server.create_account(fund=True, amount=str(5000_000000))),
    }

    server.set_default_ripple(bitstamp)
    server.set_default_ripple(gatehub)

    usd_bs = {
            "currency": "USD",
            "issuer": bitstamp.account_id,
        }
    usd_gh = {
            "currency": "USD",
            "issuer": gatehub.account_id,
        }
    btc_gh = {
        "currency": "BTC",
        "issuer": gatehub.account_id,
    }

    server.account_set(gatehub, TransferRate=int(1.2 * 1000000000))
    server.account_set(bitstamp, TransferRate=int(1.15 * 1000000000))

    server.create_trustline(trader, usd_gh)
    server.create_trustline(trader, usd_bs)
    server.create_trustline(trader, btc_gh)

    iou_payments = 100_000
    server.make_payment(gatehub, trader, dict(usd_gh, value=iou_payments))
    server.make_payment(gatehub, trader, dict(btc_gh, value=iou_payments))
    server.make_payment(bitstamp, trader, dict(usd_bs, value=iou_payments))

    server.amm_create(trader,
                      asset_1=dict(usd_gh, value=273),
                      asset_2=dict(usd_bs, value=3),
                      )

    usd_bs_to_btc_gh_offer = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": trader.account_id,
            "TakerPays": dict(usd_bs, value="1"),
            "TakerGets": dict(btc_gh, value="0.1"),
        },
        "secret": trader.master_seed
    }

    btc_gh_to_usd_gh_offer = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": trader.account_id,
            "TakerPays": dict(btc_gh, value="0.1"),
            "TakerGets": dict(usd_gh, value="1"),
        },
        "secret": trader.master_seed
    }

    usd_bs_btc_gh_response = server.execute_transaction(payload=usd_bs_to_btc_gh_offer, issuer=trader.account_id)
    test_validator.verify_test(server, usd_bs_btc_gh_response, offer_crossing=False)

    btc_gh_usd_gh_response = server.execute_transaction(payload=btc_gh_to_usd_gh_offer, issuer=trader.account_id)
    test_validator.verify_test(server, btc_gh_usd_gh_response, offer_crossing=False)

    payment = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": trader.account_id,
            "Destination": trader.account_id,
            "Amount": dict(usd_gh, value="272.455089820359"),
            "SendMax": dict(usd_bs, value="50"),
            "Flags": PAYMENT_FLAG["tfPartialPayment"],
            "Paths": [
                [usd_gh],
                [btc_gh, usd_gh]
            ],
        },
        "secret": trader.master_seed
    }

    amm_id = server.get_amm_id(usd_bs, usd_gh, verbose=False)
    payment_response = server.execute_transaction(payload=payment)
    test_validator.verify_test(server, payment_response)

    lp_token = server.get_amm_lp_token(usd_bs, usd_gh, verbose=False)
    amm_balance = {
        accounts["gatehub"].account_id: {
            "USD": "96.7543114220382",
        },
        accounts["bitstamp"].account_id: {
            "USD": "8.464739069120721"
        },
        accounts["trader"].account_id: {
            lp_token["currency"]: "-28.61817604250837"
        }
    }

    for trustline_info in server.get_trustline_info(amm_id):
        assert amm_balance[trustline_info['account']][trustline_info['currency']] == trustline_info["balance"], \
            "AMM trustlines balances incorrect."


@pytest.mark.skip(reason="Waiting to merge on develop: https://github.com/XRPLF/rippled/pull/4968/")
def test_payment_amm_synthetic_order_fill_usd_btc_same_issuer(fx_rippled):
    server = fx_rippled["rippled_server"]
    accounts = {
        "bitstamp": (bitstamp := server.create_account(fund=True, amount=str(5000_000000))),
        "gatehub": (gatehub := server.create_account(fund=True, amount=str(5000_000000))),
        "trader": (trader := server.create_account(fund=True, amount=str(5000_000000))),
    }

    server.set_default_ripple(bitstamp)
    server.set_default_ripple(gatehub)

    usd_bs = {
            "currency": "USD",
            "issuer": bitstamp.account_id,
        }
    btc_bs = {
            "currency": "BTC",
            "issuer": bitstamp.account_id,
        }
    btc_gh = {
        "currency": "BTC",
        "issuer": gatehub.account_id,
    }

    server.account_set(gatehub, TransferRate=int(1.2 * 1000000000))
    server.account_set(bitstamp, TransferRate=int(1.15 * 1000000000))

    server.create_trustline(trader, btc_bs)
    server.create_trustline(trader, usd_bs)
    server.create_trustline(trader, btc_gh)

    iou_payments = 100_000
    server.make_payment(bitstamp, trader, dict(btc_bs, value=iou_payments))
    server.make_payment(gatehub, trader, dict(btc_gh, value=iou_payments))
    server.make_payment(bitstamp, trader, dict(usd_bs, value=iou_payments))

    server.amm_create(trader,
                      asset_1=dict(btc_bs, value=273),
                      asset_2=dict(usd_bs, value=3),
                      )

    usd_bs_to_btc_gh_offer = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": trader.account_id,
            "TakerPays": dict(usd_bs, value="1"),
            "TakerGets": dict(btc_gh, value="0.1"),
        },
        "secret": trader.master_seed
    }

    btc_gh_to_btc_bs_offer = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": trader.account_id,
            "TakerPays": dict(btc_gh, value="0.1"),
            "TakerGets": dict(btc_bs, value="1"),
        },
        "secret": trader.master_seed
    }

    usd_bs_btc_gh_response = server.execute_transaction(payload=usd_bs_to_btc_gh_offer, issuer=trader.account_id)
    test_validator.verify_test(server, usd_bs_btc_gh_response, offer_crossing=False)

    btc_gh_btc_bs_response = server.execute_transaction(payload=btc_gh_to_btc_bs_offer, issuer=trader.account_id)
    test_validator.verify_test(server, btc_gh_btc_bs_response, offer_crossing=False)

    payment = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": trader.account_id,
            "Destination": trader.account_id,
            "Amount": dict(btc_bs, value="272.455089820359"),
            "SendMax": dict(usd_bs, value="50"),
            "Flags": PAYMENT_FLAG["tfPartialPayment"],
            "Paths": [
                [btc_bs],
                [btc_gh, btc_bs]
            ],
        },
        "secret": trader.master_seed
    }

    amm_id = server.get_amm_id(usd_bs, btc_bs, verbose=False)
    payment_response = server.execute_transaction(payload=payment)
    test_validator.verify_test(server, payment_response)

    lp_token = server.get_amm_lp_token(usd_bs, btc_bs, verbose=False)
    amm_balance = {
        accounts["bitstamp"].account_id: {
            "BTC": "96.7543114220382",
            "USD": "8.464739069120721"
        },
        accounts["trader"].account_id: {
            lp_token["currency"]: "-28.61817604250837"
        }
    }

    for trustline_info in server.get_trustline_info(amm_id):
        assert amm_balance[trustline_info['account']][trustline_info['currency']] == trustline_info["balance"], \
            "AMM trustlines balances incorrect."
