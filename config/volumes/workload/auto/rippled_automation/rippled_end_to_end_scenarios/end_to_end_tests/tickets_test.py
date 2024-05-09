#!/usr/bin/env python
import os
import sys
import time

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator

log = log_helper.get_logger()


def test_create_ticket_on_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": "bad_account_name",
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 0
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="srcActMalformed")


def test_zero_ticket_creation(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 0
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="temINVALID_COUNT")


def test_non_whole_number_ticket_count(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 1.2
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="invalidParams")


def test_ticket_count_equals_250(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=1300000000)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 250
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])


def test_ticket_count_over_250(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 251
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="temINVALID_COUNT")


def test_multiple_tickets_summing_over_250(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=1300000000)
    # account_1 = rippled_server.create_account(fund=True)

    ticket_counts = [240, 15]  # total count more than 250
    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": ticket_counts[0]
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": ticket_counts[1]
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="tecDIR_FULL")

    assert ticket_counts[0] == \
           len(test_validator.wait_for_account_objects_in_ledger(rippled_server, account_1.account_id,
                                                                 verbose=False)), "Not all objects created"


def test_create_tickets_from_tickets_summing_250(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=1300000000)
    # account_1 = rippled_server.create_account(fund=True)

    ticket_counts = [240, 10]  # total count more than 250
    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": ticket_counts[0]
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
            "TicketCount": ticket_counts[1]
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    assert sum(ticket_count for ticket_count in ticket_counts) - 1 == \
           len(test_validator.wait_for_account_objects_in_ledger(rippled_server, account_1.account_id,
                                                                 verbose=False)), "Not all objects created"

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_tickets_from_tickets_summing_over_250(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=1300000000)
    # account_1 = rippled_server.create_account(fund=True)

    ticket_counts = [240, 15]  # total count more than 250
    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": ticket_counts[0]
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
            "TicketCount": ticket_counts[1]
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="tecDIR_FULL")
    # adding wait time to avoid sync issue while running rippled as clio
    time.sleep(3)
    assert (ticket_counts[0] - 1) == \
           len(test_validator.wait_for_account_objects_in_ledger(rippled_server, account_1.account_id,
                                                                 verbose=False)), "Not all objects created"


def test_missing_ticket_count(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1)
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="invalidParams")


def test_ticket_create_with_past_account_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1) - 1,
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="tefPAST_SEQ")


def test_ticket_create_with_new_account_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1) + 1,
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="terPRE_SEQ")


def test_account_sequence_from_diff_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True, amount=20000000)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="terPRE_SEQ")


def test_missing_account_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])


def test_create_ticket_with_low_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=11000000)

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
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="tecINSUFFICIENT_RESERVE")


def test_negative_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount="21000000")

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Fee": str(-1),
            "TicketCount": 1
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1],
                               response_result="temBAD_FEE")


def test_transaction_with_ticket_sequence_and_account_sequence_set_to_non_zero(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temSEQ_AND_TICKET")


def test_transaction_with_ticket_sequence_and_account_sequence_set_to_zero(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Sequence": 0,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_transaction_using_account_sequence_in_ticket_sequence(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="terPRE_TICKET")


def test_transaction_using_ticket_sequence_in_account_sequence(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Sequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tefPAST_SEQ")


def test_transaction_using_ticket_sequence_field_when_no_ticket_created(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="terPRE_TICKET")


def test_payments_on_multiple_tickets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "TicketCount": 2
        },
        "secret": account_1.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    log.info("")
    log.info("** Submitting transaction using Ticket Sequence: {}".format(payload["tx_json"]["TicketSequence"]))
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    log.info("")
    log.info("** Submitting transaction using Ticket Sequence: {}".format(payload["tx_json"]["TicketSequence"]))
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_submit_transaction_on_used_ticket(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    log.info("")
    log.info("** Submitting transaction using Ticket Sequence: {}".format(payload["tx_json"]["TicketSequence"]))
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    log.info("")
    log.info("** Submitting transaction using Same Ticket Sequence: {}".format(payload["tx_json"]["TicketSequence"]))
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tefNO_TICKET")


def test_cancel_a_ticket(fx_rippled):
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

    response = rippled_server.ticket_cancel(account_1)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])


def test_transaction_using_cancelled_ticket(fx_rippled):
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
    ticket_sequence = rippled_server.get_ticket_sequence(account_1)[0]

    response = rippled_server.ticket_cancel(account_1)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    # Create and fund account
    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": ticket_sequence,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tefNO_TICKET")


def test_transaction_with_account_sequence_after_ticket_creation(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


@pytest.mark.smoke
def test_payment_on_ticket(fx_rippled):
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
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_create_payment_on_ticket_created_from_ticket(fx_rippled):
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
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_escrow_create_on_ticket(fx_rippled):
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


def test_escrow_finish_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowFinish",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0],
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response),
        },
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response, payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_escrow_cancel_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCancel",
            "Owner": account_1.account_id,
            "Account": account_2.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0],
            "OfferSequence": rippled_server.get_txn_sequence(escrow_create_response)
        },
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_offer_create_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_claim_on_ticket(fx_rippled):
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
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0],
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_cancel_on_ticket(fx_rippled):
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
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1])

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
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response),
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1])


def test_offer_cancel_with_invalid_offer_sequence_on_ticket(fx_rippled):
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
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

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
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response) - 1,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2],
                               offer_cancelled=False)


def test_check_create_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])


def test_check_cash_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0]
        },
        "secret": account_2.master_seed
    }
    cash_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, cash_response, accounts=[account_1, account_2])


def test_check_cancel_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "SendMax": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "CheckCancel",
            "Account": account_2.account_id,
            "CheckID": rippled_server.get_check_ids(account_1)[0],
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0]
        },
        "secret": account_2.master_seed
    }
    cash_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, cash_response, accounts=[account_1, account_2])


def test_signer_list_on_ticket(fx_rippled):
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


def test_multisign_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

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
        "account": account_3.account_id,
        "secret": account_3.master_seed,
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Sequence": 0,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
            "SigningPubKey": "",
            "Fee": constants.DEFAULT_TRANSACTION_FEE
        }
    }
    sign_for_response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multisign_response = rippled_server.execute_transaction(payload=sign_for_response,
                                                            method="submit_multisigned")
    test_validator.verify_test(rippled_server, multisign_response,
                               accounts=[account_1, account_2, account_3])


def test_payment_channel_create_on_ticket(fx_rippled):
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


def test_payment_channel_claim_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_DELETE_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

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
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    channels = rippled_server.get_account_channels(account_1.account_id)
    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelClaim",
            "Account": account_1.account_id,
            "Channel": channels['channels'][0]['channel_id'],
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    claim_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, claim_response, accounts=[account_1, account_2])


def test_payment_channel_fund_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_DELETE_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

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
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    channels = rippled_server.get_account_channels(account_1.account_id)
    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelFund",
            "Account": account_1.account_id,
            "Channel": channels['channels'][0]['channel_id'],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0],
        },
        "secret": account_1.master_seed
    }
    fund_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, fund_response, accounts=[account_1, account_2])


def test_preauthorize_third_party_on_ticket_using_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    # Set deposit auth
    account_3 = rippled_server.create_account(fund=True)
    rippled_server.enable_deposit_auth(account_object=account_2)
    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_3,
                                        ticket_sequence=rippled_server.get_ticket_sequence(account_2)[0])

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


def test_regular_key_on_ticket_using_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[account_1, account_2])

    # Generate regular key for accounts
    rippled_server.add_regular_key_to_account(account_1,
                                              ticket_sequence=rippled_server.get_ticket_sequence(account_1)[0])

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
        "secret": account_2.master_seed,
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                  create_response=escrow_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
