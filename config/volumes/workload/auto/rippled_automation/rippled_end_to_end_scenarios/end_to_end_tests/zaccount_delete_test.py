#!/usr/bin/env python
import os
import sys
import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator

log = log_helper.get_logger()


def test_delete_account_too_soon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecTOO_SOON")


def test_delete_no_dest_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1],
                               response_result="invalidParams")


def test_delete_no_dest_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecNO_DST")


def test_delete_same_src_dest_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1],
                               response_result="temDST_IS_SRC")


def test_delete_account_insufficient_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": str(int(constants.DEFAULT_DELETE_ACCOUNT_FEE) - 1),
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="telINSUF_FEE_P")


def test_delete_account_with_missing_destination_tag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    pass


def test_dest_account_requires_authorization(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_2)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_delete_account_with_account_sequence_mismatch(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True, amount=20000000)
    account_2 = rippled_server.create_account(fund=True)

    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_2),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="terPRE_SEQ")


@pytest.mark.longrun
def test_block_deletion_object_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    # Delete source account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")
    log.info("")
    log.info("As expected, source account with unfinished escrow cannot be deleted")

    # Delete Destination account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_2),
        },
        "secret": account_2.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")
    log.info("")
    log.info("As expected, destination account with unfinished escrow cannot be deleted")


@pytest.mark.longrun
def test_block_deletion_object_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    check_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, check_create_response, accounts=[account_1, account_2])

    assert rippled_server.get_check_ids(account_1), "Check IDs not present"

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    # Delete source account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")
    log.info("")
    log.info("As expected, account with un-cashed check cannot be deleted")


@pytest.mark.longrun
def test_block_deletion_object_payment_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_DELETE_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    check_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, check_response, accounts=[account_1, account_2])

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    # Delete account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")
    log.info("")
    log.info("As expected, account with un-claimed payment cannot be deleted")


@pytest.mark.longrun
def test_delete_account_with_minimum_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True, amount=20000000)
    account_2 = rippled_server.create_account(fund=True, amount=20000000)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_resurrect_deleted_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])

    log.info("")
    log.info("Account deleted successfully. Now resurrecting the deleted account...")
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Amount": "25000000"
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_unblocked_deletion_object_signer_list(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    # accounts for signing txns
    account_3 = rippled_server.create_account()

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
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


# TODO: This test takes more than 1 hr to create 1000 objects sequentially.
# TODO: Replace this with parallel threads
# @pytest.mark.longrun
# def test_1000_plus_unblocked_deletion_object(fx_rippled):
#     rippled_server = fx_rippled["rippled_server"]
#
#     # Create and fund account accounts
#     account_1 = rippled_server.create_account(fund=True, amount=2600000000)
#     rippled_server.fund_account(account_1.account_id, amount=2600000000)
#     account_2 = rippled_server.create_account(fund=True)
#
#     payload = {
#         "tx_json": {
#             "TransactionType": "OfferCreate",
#             "Account": account_1.account_id,
#             "TakerGets": 6,
#             "TakerPays": {
#                 "currency": "GKO",
#                 "issuer": account_1.account_id,
#                 "value": "2"
#             }
#         },
#         "secret": account_1.master_seed
#     }
#
#     no_of_txns = 1001
#     log.info("")
#     for i in range(0, no_of_txns):
#         log.info("Creating txn: {}/{}...".format(i+1, no_of_txns))
#         response = rippled_server.execute_transaction(payload=payload, verbose=False)
#         assert response["engine_result"] != "tecINSUF_RESERVE_OFFER", response["engine_result"]
#
#     rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)
#
#     payload = {
#         "tx_json": {
#             "TransactionType": "AccountDelete",
#             "Account": account_1.account_id,
#             "Destination": account_2.account_id,
#             "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
#             "Sequence": rippled_server.get_account_sequence(account_1),
#         },
#         "secret": account_1.master_seed
#     }
#     delete_response = rippled_server.execute_transaction(payload=payload)
#     test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
#                                response_result="tefTOO_BIG")


@pytest.mark.longrun
def test_delete_account_holding_tickets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_account_delete_using_ticket_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_delete_account_with_signer_list_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # accounts for signing txns
    account_2 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    # Create and fund account
    account_3 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2, account_3])


@pytest.mark.longrun
def test_delete_account_with_escrow_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # Create and fund account accounts
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    # Create and fund account
    account_3 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2, account_3],
                               response_result="tecHAS_OBLIGATIONS")


@pytest.mark.longrun
def test_delete_account_with_paychannel_created_on_ticket_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_DELETE_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    # Create and fund account
    account_3 = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2, account_3],
                               response_result="tecHAS_OBLIGATIONS")
