from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, helper
from rippled_automation.rippled_end_to_end_scenarios.utils import test_validator

log = log_helper.get_logger()


def test_unsubscribe_to_all(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe a lot of stuff",
            "command": "unsubscribe",
            "streams": ["ledger", "transactions", "transactions_proposed"],
            "accounts": [alice.account_id],
            "accounts_proposed": [alice.account_id],
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_all_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe a lot of stuff",
        "command": "subscribe",
        "streams": ["ledger", "transactions", "transactions_proposed"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe a lot of stuff",
        "command": "unsubscribe",
        "streams": ["ledger", "transactions", "transactions_proposed"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_empty_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to empty streams",
            "command": "unsubscribe",
            "streams": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_ledger_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to ledger",
        "command": "subscribe",
        "streams": ["ledger"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to ledger",
        "command": "unsubscribe",
        "streams": ["ledger"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_server_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to server",
        "command": "subscribe",
        "streams": ["server"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to server",
        "command": "unsubscribe",
        "streams": ["server"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to server",
            "command": "unsubscribe",
            "streams": ["server"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # server stream is not available from servers in Reporting Mode


def test_unsubscribe_to_transactions_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to transactions",
        "command": "subscribe",
        "streams": ["transactions"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to transactions",
        "command": "unsubscribe",
        "streams": ["transactions"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_transactions_proposed_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to transactions_proposed",
        "command": "subscribe",
        "streams": ["transactions_proposed"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to transactions_proposed",
        "command": "unsubscribe",
        "streams": ["transactions_proposed"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_consensus_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to consensus",
        "command": "subscribe",
        "streams": ["consensus"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to consensus",
        "command": "unsubscribe",
        "streams": ["consensus"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to consensus",
            "command": "unsubscribe",
            "streams": ["consensus"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # consensus stream is not available from servers in Reporting Mode


def test_unsubscribe_to_manifests_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to manifests",
        "command": "subscribe",
        "streams": ["manifests"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to manifests",
        "command": "unsubscribe",
        "streams": ["manifests"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_peer_status_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to peer_status",
        "command": "subscribe",
        "streams": ["peer_status"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to peer_status",
        "command": "unsubscribe",
        "streams": ["peer_status"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    test_validator.verify_test(rippled_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to peer_status",
            "command": "unsubscribe",
            "streams": ["peer_status"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="reportingUnsupported")

    # peer_status stream is not available from servers in Reporting Mode


def test_unsubscribe_to_validations_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "id": "subscribe to validations",
        "command": "subscribe",
        "streams": ["validations"]
    }
    ws = rippled_server.start_streaming_thread(payload=payload)
    clio_ws = clio_server.start_streaming_thread(payload=payload)

    payload = {
        "id": "Unsubscribe to validations",
        "command": "unsubscribe",
        "streams": ["validations"]
    }
    rippled_server.send_request_to_existing_ws(ws, payload=payload)
    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)

    test_validator.verify_test(rippled_server, stream_validation=True)
    test_validator.verify_test(clio_server, stream_validation=True)

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_malformed_streams(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to malformed stream",
            "command": "unsubscribe",
            "streams": ["validatio"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="malformedStream")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, clio_response, response_result="malformedStream")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "id": "Watch account alice",
        "command": "subscribe",
        "accounts": [alice.account_id]
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

    payload = {
        "id": "Unsubscribe to alice",
        "command": "unsubscribe",
        "accounts": [alice.account_id]
    }
    rippled_server.send_request_to_existing_ws(ws=ws, payload=payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)
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
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_accounts_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to malformed account",
            "command": "unsubscribe",
            "accounts": ["rrpNnNLKrartuEqfJGpqyDwPj1AFPg9v"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_accounts_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Unsubscribe to alice",
            "command": "unsubscribe",
            "accounts": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_empty_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe a lot of stuff",
            "command": "unsubscribe",
            "streams": ["ledger", "transactions", "transactions_proposed"],
            "accounts": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_accounts_proposed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to alice",
            "command": "unsubscribe",
            "accounts_proposed": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_accounts_proposed_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to malformed account",
            "command": "unsubscribe",
            "accounts_proposed": ["rrpNnNLKrartuEqfJGpqyDwPj1AFPg9v"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_accounts_proposed_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Unsubscribe to alice",
            "command": "unsubscribe",
            "accounts_proposed": [alice.account_id]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_empty_accounts_proposed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to empty accounts",
            "command": "unsubscribe",
            "accounts_proposed": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_books(fx_rippled):
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

    payload = {
        "id": "Unsubscribe a lot of stuff",
        "command": "unsubscribe",
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
    rippled_server.send_request_to_existing_ws(ws, payload)
    test_validator.verify_test(rippled_server, accounts=[alice, bob], stream_validation=True)

    clio_server.send_request_to_existing_ws(clio_ws, payload=payload)
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
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    rippled_response = rippled_server.close_streaming_thread(ws)
    assert rippled_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)

    clio_response = clio_server.close_streaming_thread(clio_ws)
    assert clio_response[-1]["type"] == "response", "unsubscribe failed:{}".format(rippled_response)


def test_unsubscribe_to_empty_books(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to empty books",
            "command": "unsubscribe",
            "books": []
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_books_with_empty_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe a lot of stuff",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_without_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": "true"
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


def test_unsubscribe_to_books_with_taker_pays_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
                    "both": True
                }
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], response_result="srcIsrMalformed")

    clio_response = clio_server.execute_transaction(payload=payload)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, bob], response_result="srcIsrMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_unsubscribe_to_books_with_taker_pays_currency_non_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "INR",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
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


def test_unsubscribe_to_books_with_malformed_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XR"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_empty_taker_pays_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": ""
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_taker_pays_currency_non_xrp_and_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "INR",
                        "issuer": alice.account_id
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": bob.account_id
                    },
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


def test_unsubscribe_to_books_with_empty_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {},
                    "both": True
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


def test_unsubscribe_to_books_with_without_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_taker_gets_currency_xrp_and_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "XRP",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_malformed_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "XR",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_empty_taker_gets_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_taker_gets_currency_non_xrp_and_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "USD",
                        "issuer": alice.account_id
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_taker_gets_and_taker_pays_currency_as_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
            "books": [
                {
                    "taker_pays": {
                        "currency": "XRP"
                    },
                    "taker_gets": {
                        "currency": "XRP"
                    },
                    "both": True
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


def test_unsubscribe_to_books_with_same_currency_and_issuer_in_taker_gets_and_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
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
                    "both": True
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


def test_unsubscribe_to_books_with_same_currency_and_different_issuer_in_taker_gets_and_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
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


def test_unsubscribe_to_books_with_different_currency_and_same_issuer_in_taker_gets_and_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "id": "Unsubscribe to books",
            "command": "unsubscribe",
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
                    "both": True
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

