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


def test_escrow_create_cancel(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)

    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


@pytest.mark.smoke
def test_escrow_create_finish(fx_rippled):
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

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_finish_time_in_the_past(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(-20)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='tecNO_PERMISSION')


def test_cancel_time_in_the_past(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(-20)
        },
        "secret": account_1.master_seed,
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_EXPIRATION')


def test_destination_account_does_not_exit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

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
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='tecNO_DST')


def test_sending_zero_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": "0",
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_AMOUNT')


def test_cancel_after_finish_after_are_missing(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_EXPIRATION')


def test_escrow_with_missing_destination_tag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    # This is covered in any of the escrow tests
    assert True


def test_sender_sends_more_than_he_has(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": "1000000000",
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='tecUNFUNDED')


def test_third_party_cancel_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": account_1.account_id,
            "Account": account_3.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_3.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_third_party_finishes_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response,
                               accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_3.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_3.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])


def test_set_deposit_auth_and_verify_only_user_can_finish_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_2)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed,
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_set_deposit_auth_and_preauthorize_third_party_and_thrid_party_finishes_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    account_3 = rippled_server.create_account(fund=True)
    rippled_server.enable_deposit_auth(account_object=account_2)
    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_3)

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

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response,
                               accounts=[account_1, account_2, account_3], response_result='tecNO_PERMISSION')
    log.info("As expected, EscrowFinish with unauthorized account was not permitted")

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_3.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_3.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response,
                               accounts=[account_1, account_2, account_3])
    log.info("EscrowFinish completed successfully with permitted account")


def test_add_regular_key_to_create_and_finish_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Generate regular key for accounts
    rippled_server.add_regular_key_to_account(account_1)
    rippled_server.add_regular_key_to_account(account_2)

    # EscrowCreate using account1 regular key
    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.regular_key_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    # EscrowFinish using account2 regular key
    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.regular_key_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_creating_and_escrow_and_canceling_using_regular_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Generate regular key for accounts
    rippled_server.add_regular_key_to_account(account_1)
    rippled_server.add_regular_key_to_account(account_2)

    # EscrowCreate using account1 regular key
    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.regular_key_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    # EscrowFinish using account2 regular key
    payload = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.regular_key_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_using_non_xrp_to_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": "10000",
                "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
            },
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_AMOUNT')


def test_escrow_create_finish_same_source_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_1.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_1.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])


def test_escrow_finish_with_finish_after_and_cancel_after(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_neg_escrow_finish_escrow_cancel_at_same_time(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_EXPIRATION')


def test_escrow_finish_with_2_txns_for_same_destination(fx_rippled):
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
    escrow_create_response_1 = rippled_server.execute_transaction(payload=payload)
    escrow_create_response_2 = rippled_server.execute_transaction(payload=payload)

    test_validator.verify_test(rippled_server, escrow_create_response_1, accounts=[account_1, account_2])
    test_validator.verify_test(rippled_server, escrow_create_response_2, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response_1)
        },
        "secret": account_2.master_seed
    }
    response_1 = rippled_server.execute_transaction(payload=payload,
                                                    execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                    create_response=escrow_create_response_1)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2])

    payload["tx_json"]["OfferSequence"] = rippled_server.get_txn_sequence(escrow_create_response_2)
    response_2 = rippled_server.execute_transaction(payload=payload,
                                                    execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                    create_response=escrow_create_response_2)
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2])


def test_escrow_create_2_diff_destinations_cancel_one_finish_one(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload_1 = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response_1 = rippled_server.execute_transaction(payload=payload_1)
    test_validator.verify_test(rippled_server, escrow_create_response_1,
                               accounts=[account_1, account_2, account_3])

    payload_2 = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response_2 = rippled_server.execute_transaction(payload=payload_2)
    test_validator.verify_test(rippled_server, escrow_create_response_2,
                               accounts=[account_1, account_2, account_3])

    payload_1 = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response_1)
        },
        "secret": account_1.master_seed
    }
    response_1 = rippled_server.execute_transaction(payload=payload_1,
                                                    execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                    create_response=escrow_create_response_1)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2, account_3])

    payload_2 = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": account_1.account_id,
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response_2)
        },
        "secret": account_1.master_seed
    }
    response_2 = rippled_server.execute_transaction(payload=payload_2,
                                                    execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                    create_response=escrow_create_response_2)

    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2, account_3])


def test_create_escrow_with_multi_sign_key_escrow_finish_cash_using_regular_key(fx_rippled):
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
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TransactionType": "EscrowCreate",
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Flags": 0,
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        }
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(multisign_response)
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=multisign_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])
    log.info("EscrowFinish completed successfully")


def test_create_escrow_with_regular_key_escrow_finish_cash_using_multi_sign_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # accounts for signing txns
    account_3 = rippled_server.create_account()
    account_4 = rippled_server.create_account()

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
    test_validator.verify_test(rippled_server, escrow_create_response,
                               accounts=[account_1, account_2, account_3, account_4])

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
        "account": account_3.account_id,
        "secret": account_3.master_seed,
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response),
            "Sequence": rippled_server.get_account_sequence(account_2),
            "Flags": 0,
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        }
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            create_response=escrow_create_response,
                                                            execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2, account_3, account_4])
    log.info("EscrowFinish completed successfully")


def test_escrow_create_with_dest_asfDisallowXRP_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    pass


def test_neg_escrow_create_no_source_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": "",
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='srcActMalformed')


def test_neg_escrow_create_no_destination_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": account_1.account_id,
            "Destination": "",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1],
                               response_result='invalidParams')


def test_neg_non_existant_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": "{}a".format(account_1.account_id),
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='srcActMalformed')


def test_neg_cancel_after_before_finish_after(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temBAD_EXPIRATION')


def test_escrow_create_invalid_source_secret(fx_rippled):
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
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER)
        },
        "secret": "INVALID_SOURCE_KEY"
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='badSecret')


def test_neg_escrow_create_with_only_cancel_after(fx_rippled):
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
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": account_1.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[account_1, account_2],
                               response_result='temMALFORMED')
