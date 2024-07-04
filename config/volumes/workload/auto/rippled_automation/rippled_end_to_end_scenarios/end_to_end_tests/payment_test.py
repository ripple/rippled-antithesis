#!/usr/bin/env python
import os
import sys
import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_xrp_simple_payment(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


@pytest.mark.smoke
def test_xrp_payment_submit_only_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, submit_only=True)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_with_more_than_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": str(int(rippled_server.get_account_balance(account_1.account_id)) + 1),
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_PAYMENT")


def test_xrp_payment_sign_master_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed_hex
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_sign_master_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_key
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_with_invalid_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_DST_INSUF_XRP")


def test_xrp_payment_from_non_preauth_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_2)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_xrp_payment_from_preauth_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_2)
    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_zero_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": "0",
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_xrp_payment_decimal_value_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    amount_to_transfer = "10.5"
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": str(int(float(amount_to_transfer) * 1000000))
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_non_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": "10000",
                "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_DRY")


def test_xrp_payment_with_destination_tag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "DestinationTag": 123,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_with_invoice_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "InvoiceID": "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_xrp_payment_with_invalid_invoice_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "InvoiceID": 123,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_xrp_payment_to_self(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_1.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="temREDUNDANT")


def test_xrp_payment_with_no_source_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": "",
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="srcActMalformed")


def test_xrp_payment_with_no_destination_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": "",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_xrp_payment_with_invalid_destination_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": "invalid_address",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_xrp_payment_10_million_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    amount_to_transfer = "10000000000000"
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": constants.TEST_GENESIS_ACCOUNT_ID,
            "Destination": account_2.account_id,
            "Amount": amount_to_transfer,
        },
        "secret": constants.TEST_GENESIS_ACCOUNT_SEED
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_2.account_id,
            "Destination": constants.TEST_GENESIS_ACCOUNT_ID,
            "Amount": amount_to_transfer,
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_2])
