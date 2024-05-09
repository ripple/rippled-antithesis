import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator
from rippled_automation.rippled_end_to_end_scenarios.utils.streams import streams_helper

log = log_helper.get_logger()

MAX_ITERATIONS = 3


def test_subscribe_to_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_account_and_make_payment_transactions(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    for i in range(MAX_ITERATIONS):
        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": alice.account_id,
                "Destination": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "secret": alice.master_seed
        }
        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_account_with_api_version_2_and_make_payment_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id],
        "api_version": 2
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/CLIO-476")
def test_subscribe_to_same_stream_with_v1_v2_and_make_payment_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload1 = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload1)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload1)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload2 = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id],
        "api_version": 2
    }

    rippled_server.send_request_to_existing_ws(ws=ws, payload=payload2)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_server.send_request_to_existing_ws(ws=clio_ws, payload=payload2)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/CLIO-476")
def test_subscribe_to_different_stream_with_v1_v2_and_make_payment_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload1 = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload1, max_stream_timeout=180)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload1, max_stream_timeout=180)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload2 = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts_proposed": [alice.account_id],
        "api_version": 2
    }

    rippled_server.send_request_to_existing_ws(ws=ws, payload=payload2)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_server.send_request_to_existing_ws(ws=clio_ws, payload=payload2)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_account_and_make_3_different_transactions(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": bob.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": bob.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": alice.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 67890,
        },
        "secret": alice.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    rippled_response = rippled_server.close_streaming_thread(ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_accounts_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_with_empty_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Watch empty accounts",
            "command": "subscribe",
            "accounts": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_without_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Watch without accounts",
            "command": "subscribe"
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_subscribe_to_deleted_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(alice)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "secret": alice.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_subscribe_to_resurrected_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    rippled_server.wait_for_ledger_to_advance_for_account_delete(alice)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "secret": alice.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": bob.account_id,
            "Destination": alice.account_id,
            "Amount": 20000000,
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_account_and_payment_txn_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": alice.account_id,
            "Sequence": rippled_server.get_account_sequence(alice),
            "TicketCount": 1
        },
        "secret": alice.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[alice])

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TicketSequence": rippled_server.get_ticket_sequence(alice)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_accounts_with_malformed_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Watch account",
            "command": "subscribe",
            "accounts": ["rrpNnNLKrartuEqfJGpqyDwPj1AFPg9vn"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_with_two_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Watch accounts alice and bob",
            "command": "subscribe",
            "accounts": [alice.account_id, bob.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_with_two_accounts_and_do_payment_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch accounts alice and bob",
        "command": "subscribe",
        "accounts": [alice.account_id, bob.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_accounts_with_two_accounts_and_do_txn_separately(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch accounts alice and bob",
        "command": "subscribe",
        "accounts": [alice.account_id, bob.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob, carol], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol],
                               stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": bob.account_id,
            "Destination": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_accounts_proposed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts_proposed": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/680")
def test_subscribe_to_accounts_proposed_and_make_payment_transactions(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts_proposed": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    for i in range(MAX_ITERATIONS):
        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": alice.account_id,
                "Destination": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "secret": alice.master_seed
        }
        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/680")
def test_subscribe_to_accounts_proposed_and_make_3_different_transactions(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts_proposed": [alice.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": bob.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": bob.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": alice.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 67890,
        },
        "secret": alice.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_accounts_proposed_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Watch account alice",
            "command": "subscribe",
            "accounts_proposed": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_proposed_with_empty_accounts_proposed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Watch empty account",
            "command": "subscribe",
            "accounts_proposed": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_proposed_with_malformed_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Watch account",
            "command": "subscribe",
            "accounts_proposed": ["rrpNnNLKrartuEqfJGpqyDwPj1AFPg9vn"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_accounts_proposed_with_two_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Watch accounts alice and bob",
            "command": "subscribe",
            "accounts_proposed": [alice.account_id, bob.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/680")
def test_subscribe_to_accounts_proposed_with_two_accounts_and_do_payment_txn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch accounts alice and bob",
        "command": "subscribe",
        "accounts_proposed": [alice.account_id, bob.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    }
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_existing_offer_and_snapshot_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])
    assert response["offers"], "existing offers not found:{}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])
    assert response["offers"], "existing offers not found:{}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_existing_offer_and_snapshot_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "snapshot": False
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])
    assert "offers" not in response, "offers found:{}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])
    assert "offers" not in response, "offers found:{}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_non_existent_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/352")
def test_subscribe_to_order_books_with_empty_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": "",
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="badIssuer")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="badIssuer")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/352")
def test_subscribe_to_order_books_with_malformed_taker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": "rpoVB5W2CxKSmmzJcqWSBcgASxSZNd45",
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="badIssuer")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="badIssuer")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_create_offer_and_publish_with_snapshot_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    }
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])
    assert response["offers"], "existing offers not found:{}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])
    assert clio_response["offers"], "existing offers not found:{}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_create_offer_and_publish_with_snapshot_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    }
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": False
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])
    assert "offers" not in response, "offers found:{}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])
    assert "offers" not in clio_response, "offers found:{}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/rippled/issues/4621")
def test_subscribe_to_order_books_create_offer_and_publish_with_snapshot_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    }
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "snapshot": "ghj"
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob],
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_existing_offer_snapshot_and_both_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "snapshot": True,
                    "both": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_existing_offer_snapshot_false_and_both_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": False,
                    "both": True
                }
            ]
        }
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])
    assert "offers" not in response, "offers found:{}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])
    assert "offers" not in clio_response, "offers found:{}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/rippled/issues/4622")
def test_subscribe_to_order_books_with_existing_offer_and_both_malformed_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "taker_pays": {
                        "currency": "GKO",
                        "issuer": bob.account_id
                    },
                    "both": "fghjk"
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob],
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_both_false_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               offer_crossing=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                },
                "both": False
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_with_both_true_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_gets": {
                    "currency": "XRP"
                },
                "taker_pays": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                },
                "both": True
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               offer_crossing=True, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_create_offer_and_swap_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               offer_crossing=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_gets": {
                    "currency": "XRP"
                },
                "taker_pays": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                },
                "both": True
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=120)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_with_both_api_version_2_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_gets": {
                    "currency": "XRP"
                },
                "taker_pays": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                },
                "both": True
            }
        ],
        "api_version": 2
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_with_snapshot_both_true_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_gets": {
                    "currency": "XRP"
                },
                "taker_pays": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                },
                "snapshot": True,
                "both": True
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_with_empty_books(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_empty_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {},
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcCurMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="srcCurMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_without_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_malformed_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XR"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob],
                               response_result="srcCurMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob],
                               response_result="srcCurMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_empty_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": ""
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_pays_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "XRP",
                        "issuer": bob.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": carol.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol],
                               response_result="srcIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob, carol],
                               response_result="srcIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_pays_currency_non_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "INR",
                        "issuer": bob.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": carol.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob, carol])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_pays_currency_non_xrp_and_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account()
    carol = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker": alice.account_id,
                    "taker_pays": {
                        "currency": "INR",
                        "issuer": bob.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": carol.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob, carol])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_empty_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {},
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_without_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_malformed_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "US",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="dstAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="dstAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_empty_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_gets_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "XRP",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="dstIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="dstIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_gets_currency_non_xrp_and_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_taker_pays_currency_and_taker_gets_currency_as_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="badMarket")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="badMarket")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_same_currency_and_different_issuers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_same_currency_and_issuers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="badMarket")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="badMarket")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_with_different_currency_and_same_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Example subscribe to XRP/GateHub USD order book",
            "command": "subscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "INR",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "snapshot": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_order_books_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                }
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_accounts_with_taker_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "accounts": [alice.account_id],
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                }
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_accounts_with_issuer_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "accounts": [bob.account_id],
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                }
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    streams_helper.compare_rippled_and_clio_responses(rippled_response, clio_response)


def test_subscribe_to_order_books_accounts_with_taker_issuer_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "accounts": [alice.account_id, bob.account_id],
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                }
            }
        ]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    # compare_rippled_and_clio_responses(rippled_response, clio_response)
    # Rippled bug: https://github.com/XRPLF/rippled/issues/4648


def test_subscribe_to_order_books_accounts_with_taker_issuer_separately_and_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "accounts": [alice.account_id, bob.account_id]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_ws = clio_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD order book",
        "command": "subscribe",
        "books": [
            {
                "taker": alice.account_id,
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": "GKO",
                    "issuer": bob.account_id
                }
            }
        ]
    }
    rippled_server.send_request_to_existing_ws(ws, payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_server.send_request_to_existing_ws(clio_ws, payload)
    test_validator.verify_test(clio_server, accounts=[alice, bob], stream_validation=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    # compare_rippled_and_clio_responses(rippled_response, clio_response)
    # Rippled bug: https://github.com/XRPLF/rippled/issues/4648


def test_subscribe_to_book_changes_and_trigger_book_change(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example subscribe to XRP/GateHub USD book changes",
        "command": "subscribe",
        "streams": ["book_changes"]
    }

    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": bob.account_id,
                "value": "2"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               offer_crossing=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    assert streams_helper.find_a_book_change_in_book_changes_list(account_id=bob.account_id, response=rippled_response)
    assert streams_helper.find_a_book_change_in_book_changes_list(account_id=bob.account_id, response=clio_response)


def test_subscribe_to_ledger_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["ledger"]
    }

    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)


def test_subscribe_to_consensus_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["consensus"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)

    payload = {
        "tx_json": {
            "id": "Example watch for new validated ledgers",
            "command": "subscribe",
            "streams": ["server"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # consensus stream is not available from servers in Reporting Mode


def test_subscribe_to_manifests_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["manifests"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)


def test_subscribe_to_transactions_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["transactions"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)


def test_subscribe_to_transactions_stream_and_make_a_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["transactions"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    rippled_txn = streams_helper.find_a_txn_in_txns_list(account_id=alice.account_id, response=rippled_response)
    clio_txn = streams_helper.find_a_txn_in_txns_list(account_id=alice.account_id, response=clio_response)

    test_validator.validate_stream_data(rippled_server, response, stream_response=rippled_txn)
    test_validator.validate_stream_data(clio_server, response, stream_response=clio_txn)


def test_subscribe_to_transactions_stream_with_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["transactions"],
        "api_version": 2
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)


def test_subscribe_to_transactions_proposed_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["transactions_proposed"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)


def test_subscribe_to_transactions_proposed_stream_and_make_a_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["transactions_proposed"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    clio_response = clio_server.close_streaming_thread(clio_ws)

    rippled_txn = streams_helper.find_a_txn_in_txns_list(account_id=alice.account_id, response=rippled_response)
    clio_txn = streams_helper.find_a_txn_in_txns_list(account_id=alice.account_id, response=clio_response)

    test_validator.validate_stream_data(rippled_server, response, stream_response=rippled_txn)
    test_validator.validate_stream_data(clio_server, response, stream_response=clio_txn)


def test_subscribe_to_server_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["server"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)

    payload = {
        "tx_json": {
            "id": "Example watch for new validated ledgers",
            "command": "subscribe",
            "streams": ["server"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # server stream is not available from servers in Reporting Mode


def test_subscribe_to_peer_status_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["peer_status"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=30)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)

    payload = {
        "tx_json": {
            "id": "Example watch for new validated ledgers",
            "command": "subscribe",
            "streams": ["peer_status"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # peer_status stream is not available from servers in Reporting Mode


def test_subscribe_to_empty_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example watch for new validated ledgers",
            "command": "subscribe",
            "streams": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_subscribe_to_malformed_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Example watch for new validated ledgers",
            "command": "subscribe",
            "streams": ["peer_stat"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="malformedStream")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="malformedStream")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_subscribe_to_validations_stream(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "Example watch for new validated ledgers",
        "command": "subscribe",
        "streams": ["validations"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload, max_stream_timeout=5)
    clio_ws = clio_server.start_streaming_thread(payload=payload, max_stream_timeout=5)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_server.close_streaming_thread(ws)
    clio_server.close_streaming_thread(clio_ws)
