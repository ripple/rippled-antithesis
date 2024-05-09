#!/usr/bin/env python
import os
import sys
import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import helper
from ..utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_create_check_and_cash_it(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_with_disallow_incoming_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.account_set(account_2, flag=constants.FLAGS_CHECKS_asfDisallowIncomingCheck)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_cash_check_as_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_1.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_check_dipping_into_base_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": rippled_server.get_account_balance(account_1.account_id)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": rippled_server.get_account_balance(account_1.account_id)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_create_check_dipping_into_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=11000000)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": rippled_server.get_account_balance(account_1.account_id)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="tecINSUFFICIENT_RESERVE")


def test_create_check_on_account_with_exact_owner_reserve_and_cash_a_portion(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True,
                                              amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE)))
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.OWNER_RESERVE
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_on_account_with_exact_owner_reserve_and_cash_all_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True,
                                              amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE)))
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.OWNER_RESERVE
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.OWNER_RESERVE
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_PAYMENT")


def test_create_check_for_more_than_account_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": str(int(constants.DEFAULT_ACCOUNT_BALANCE) + 1)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_for_more_than_account_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": str(int(rippled_server.get_account_balance(account_1.account_id)) + 1)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_cash_check_dest_account_with_just_base_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True, amount=constants.BASE_RESERVE)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_for_more_than_send_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": str(int(constants.DEFAULT_CHECK_MAX_SEND) + 1)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_create_check_to_self(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_1.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1], response_result="temREDUNDANT")


def test_create_check_to_non_existent_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account()
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="srcActNotFound")


def test_create_check_to_non_existent_dest_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1], response_result="tecNO_DST")


def test_create_check_with_no_dest_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1], response_result="invalidParams")


def test_create_check_with_no_send_max(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_cash_check_with_invalid_check_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": "INVALID_CHECK_ID",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_create_check_with_expiration_time_in_the_past(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(-20)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="tecEXPIRED")


def test_cash_check_by_3rd_party(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_3.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_3.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_cash_check_after_expiration_time(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    rippled_server.wait_before_executing_transaction(wait_time=constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], response_result="tecEXPIRED")


def test_cash_check_before_expiration_time(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_with_dest_tag_and_cash_it(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "DestinationTag": 1
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_with_invoce_id_and_cash_it(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "InvoiceID": "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B"
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_make_payment_cash_it_with_sufficient_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_make_payment_cash_it_with_insufficient_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    check_amount = int(int(rippled_server.get_account_balance(account_1.account_id)) / 2)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": str(check_amount)
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": str(check_amount)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")
    log.info("As expected, there was insufficient balance left in source account to be cashed out")


def test_create_check_with_non_full_number(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": "100.5"
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_cash_check_with_non_full_number(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": "10.5"
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_cash_check_with_negative_number(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": "-10"
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_check_cash_check_with_low_bal_fund_account_cash_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")

    log.info("")
    log.info("As expected, cash check failed due to low balance")
    log.info("Fund account from a new account...")
    account_3 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_3.account_id,
            "Destination": account_1.account_id,
            "Amount": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_3.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_again_with_same_check_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    check_id = rippled_server.get_check_ids(account_1)[0]

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": check_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": check_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], response_result="tecNO_ENTRY")


def test_create_multiple_checks_and_cash_them(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    for count in range(2):
        log.info("")
        log.info("Create Check: {}".format(count + 1))
        create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    for count in range(2):
        log.info("")
        log.info("Cash Check: {}".format(count + 1))
        payload = {
            "tx_json": {
                "TransactionType": "CheckCash",
                "Account": account_2.account_id,
                "CheckID": rippled_server.get_check_ids(account_1)[0],
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "secret": account_2.master_seed
        }
        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cancel_unexpired_check_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_1.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cancel_unexpired_check_by_recipient(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cancel_unexpired_check_by_3rd_party(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_3.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_3.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_cancel_expired_check_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    rippled_server.wait_before_executing_transaction(wait_time=constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_1.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cancel_expired_check_by_recipient(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    rippled_server.wait_before_executing_transaction(wait_time=constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cancel_expired_check_by_3rd_party(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    rippled_server.wait_before_executing_transaction(wait_time=constants.DEFAULT_CHECK_EXPIRATION_IN_SECONDS)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_3.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_3.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_cancel_unexpired_check_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    check_id = rippled_server.get_check_ids(account_1)[0]
    log.info(check_id)
    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": check_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_1.account_id,
            "CheckID": check_id
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], response_result="tecNO_ENTRY")


def test_cash_check_with_both_delivermin_and_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "DeliverMin": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_cash_check_with_delivermin(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "DeliverMin": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_with_delivermin_on_max_send_more_than_account_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": str(int(rippled_server.get_account_balance(account_1.account_id)) + 1)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "DeliverMin": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_twice_with_delivermin_and_saving_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": str(int(rippled_server.get_account_balance(account_1.account_id)) + 1)
        },
        "secret": account_1.master_seed
    }
    for count in range(2):
        log.info("")
        log.info("Create Check: {}".format(count + 1))
        create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    for count in range(2):
        log.info("")
        log.info("Cash Check: {}".format(count + 1))

        payload = {
            "tx_json": {
                "TransactionType": "CheckCash",
                "Account": account_2.account_id,
                "CheckID": rippled_server.get_check_ids(account_1)[0],
                "DeliverMin": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "secret": account_2.master_seed
        }
        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_with_delivermin_dippling_into_base_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": str(int(rippled_server.get_account_balance(account_1.account_id)) + 1)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "DeliverMin": rippled_server.get_account_balance(account_1.account_id)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_cash_check_with_no_delivermin_nor_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_enabling_deposit_auth_block_payment_but_not_check_payments(fx_rippled):
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
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")
    log.info("")
    log.info("As expected, 'Payment' to 'deposit authorized' account was not permitted;")
    log.info("Verifying cashing Check on 'deposit authorized' to be permitted")

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    log.info("")
    log.info("As expected, cashing Check on 'deposit authorized' was permitted")


def test_create_check_using_multi_sign_key_cash_using_regular_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # accounts for signing txns
    account_3 = rippled_server.create_account()
    account_4 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_3.account_id,
                        "SignerWeight": 2
                    }
                },
                {
                    "SignerEntry": {
                        "Account": account_4.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "account": account_3.account_id,
        "secret": account_3.master_seed,
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        }
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2])

    # Generate regular key for account
    rippled_server.add_regular_key_to_account(account_2)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_check_using_regular_key_cash_using_multi_sign_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Generate regular key for account
    rippled_server.add_regular_key_to_account(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.regular_key_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    # accounts for signing txns
    account_3 = rippled_server.create_account()
    account_4 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_2.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_3.account_id,
                        "SignerWeight": 2
                    }
                },
                {
                    "SignerEntry": {
                        "Account": account_4.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        },
        "account": account_3.account_id,
        "secret": account_3.master_seed
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2])


def test_create_check_using_regular_key_cancel_using_multi_sign_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Generate regular key for account
    rippled_server.add_regular_key_to_account(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_1.regular_key_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    # accounts for signing txns
    account_3 = rippled_server.create_account()
    account_4 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_2.account_id,
            "Fee": constants.DEFAULT_TRANSACTION_FEE,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_3.account_id,
                        "SignerWeight": 2
                    }
                },
                {
                    "SignerEntry": {
                        "Account": account_4.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Sequence": rippled_server.get_account_sequence(account_2),
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        },
        "account": account_3.account_id,
        "secret": account_3.master_seed
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2])


def test_write_check_for_currency_doesnt_exist(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            }
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            }
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_using_trustline_with_available_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "100",
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "10",
            }
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "10"
            }
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_cash_check_using_trustline_with_unavailable_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "100",
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "10",
            }
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "20"
            }
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_fund_account_with_issued_currency_and_issue_check_cash_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "900"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "900"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "900",
            }
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "900"
            }
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
