import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.price_oracle import price_oracle_test_data as test_data
from ..utils import log_helper, helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_ledger_entry_get_ledger_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    response = rippled_server.get_ledger_data(binary=True, ledger_index=rippled_server.get_txn_sequence(response),
                                              limit=5)
    index = response["state"][0]["index"]

    response = rippled_server.get_ledger_entry(index=index)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    clio_response = clio_server.get_ledger_entry(index=index)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_index_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    # Get index from ledger_data
    ledger_index = rippled_server.get_txn_sequence(response)

    response = rippled_server.get_ledger_data(binary=True, ledger_index=ledger_index, limit=5)
    index = response["state"][0]["index"]

    response = rippled_server.get_ledger_entry(index=index, binary=True)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "AccountRoot not found"

    clio_response = clio_server.get_ledger_entry(index=index, binary=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert response["node_binary"], "AccountRoot not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_account_root_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account_root": account_1.account_id,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "AccountRoot", "AccountRoot not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "AccountRoot", "AccountRoot not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_account_root_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account_root": account_1.account_id,
            "binary": True,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1])
    assert response["node_binary"], "AccountRoot not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])
    assert clio_response["node_binary"], "AccountRoot not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_node_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "directory": {
                "owner": account_1.account_id,
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_node_with_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "directory": {
                "owner": account_1.account_id,
                "sub_index": 0
            },
            "binary": True,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "DirectoryNode not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "DirectoryNode not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_node_object_with_dir_root(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "directory": {
                "owner": account_1.account_id,
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    payload = {
        "tx_json": {
            "directory": {
                "dir_root": response["node"]["index"],
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_node_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "directory": {
                "owner": account_1.account_id,
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "DirectoryNode", "DirectoryNode not found"

    payload = {
        "tx_json": {
            "directory": response["node"]["index"],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "offer": {
                "account": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(offer_create_response)
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "Offer", "Offer not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "Offer", "Offer not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "offer": {
                "account": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(offer_create_response)
            },
            "binary": True,
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "Offer not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "Offer not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "offer": {
                "account": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(offer_create_response)
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    payload = {
        "tx_json": {
            "offer": response["node"]["index"],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripplestate_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    account_1.account_id,
                    account_2.account_id
                ],
                "currency": "USD"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "RippleState", "RippleState not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "RippleState", "RippleState not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripplestate_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    account_1.account_id,
                    account_2.account_id
                ],
                "currency": "USD"
            },
            "ledger_index": "validated",
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "RippleState not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "RippleState not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_check_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "check": rippled_server.get_check_ids(account_1)[0],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "Check", "Check not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "Check", "Check not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_check_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "check": rippled_server.get_check_ids(account_1)[0],
            "ledger_index": "validated",
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "Check not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "Check not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_escrow_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "escrow": {
                "owner": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(escrow_create_response)
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "Escrow", "Escrow not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "Escrow", "Escrow not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_escrow_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "escrow": {
                "owner": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(escrow_create_response)
            },
            "ledger_index": "validated",
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "Escrow not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "Escrow not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_escrow_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "escrow": {
                "owner": account_1.account_id,
                "seq": rippled_server.get_txn_sequence(escrow_create_response)
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    payload = {
        "tx_json": {
            "escrow": response["node"]["index"],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_paychannel_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "payment_channel": rippled_server.get_channel_ids(account_1)[0],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "PayChannel", "PayChannel not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "PayChannel", "PayChannel not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_paychannel_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "PaymentChannelCreate",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "payment_channel": rippled_server.get_channel_ids(account_1)[0],
            "ledger_index": "validated",
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "PayChannel not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "PayChannel not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_depositpreauth_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account_2.account_id,
                "authorized": account_1.account_id
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "DepositPreauth", "DepositPreauth not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "DepositPreauth", "DepositPreauth not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_depositpreauth_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account_2.account_id,
                "authorized": account_1.account_id
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    payload = {
        "tx_json": {
            "deposit_preauth": response["node"]["index"],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_depositpreauth_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account_2.account_id,
                "authorized": account_1.account_id
            },
            "ledger_index": "validated",
            "binary": True
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])
    assert response["node_binary"], "DepositPreauth not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])
    assert clio_response["node_binary"], "DepositPreauth not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ticket_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "ticket": {
                "account": account_1.account_id,
                "ticket_seq": rippled_server.get_account_sequence(account_1) - 1
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "Ticket", "Ticket not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="ledger_entry")
    assert clio_response["node"]["LedgerEntryType"] == "Ticket", "Ticket not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ticket_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "ticket": {
                "account": account_1.account_id,
                "ticket_seq": rippled_server.get_account_sequence(account_1) - 1
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry")

    payload = {
        "tx_json": {
            "ticket": response["node"]["index"],
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ticket_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "ticket": {
                "account": account_1.account_id,
                "ticket_seq": rippled_server.get_account_sequence(account_1) - 1
            },
            "ledger_index": "validated",
            "binary": True
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1])
    assert response["node_binary"], "Ticket not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])
    assert clio_response["node_binary"], "Ticket not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_nft_page(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    account_objects_response = rippled_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(rippled_server, account_objects_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "nft_page": account_objects_response["account_objects"][0]["index"],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_nft_page_with_binary_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    account_objects_response = rippled_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(rippled_server, account_objects_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "nft_page": account_objects_response["account_objects"][0]["index"],
            "ledger_index": "validated",
            "binary": True
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1])
    assert response["node_binary"], "NFT page not found"

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])
    assert clio_response["node_binary"], "NFT page not found"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ledger_object_with_invalid_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_entry(index="000001D35A51B6EEB6D9CF8BEB6C6D93C66B4955A4BBE486C87B5A3988BA45B9")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.get_ledger_entry(index="000001D35A51B6EEB6D9CF8BEB6C6D93C66B4955A4BBE486C87B5A3988BA45B9")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ledger_object_with_malformed_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_entry(index="7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.get_ledger_entry(index="7DB0788C020F02780A673DC74757F23823FA3014C1866E72CC4CD8B226CD6EF")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_account_root_with_non_existent_account_root(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "account_root": account.account_id,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_account_root_with_malformed_account_root(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "account_root": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jp",
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_with_non_existent_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "directory": {
                "owner": account.account_id,
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_with_malformed_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "directory": {
                "owner": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jp",
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "offer": {
                "account": account.account_id,
                "seq": 359
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "offer": {
                "account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jp",
                "seq": 359
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripple_state_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    account.account_id,
                    "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
                ],
                "currency": "USD"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripple_state_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jn",
                    "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
                ],
                "currency": "USD"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_check_with_invalid_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "check": "C4A46CCD8F096E994C4B0DEAB6CE98E722FC17D7944C28B95127C2659C47CBEB",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_check_with_malformed_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "check": "C4A46CCD8F096E994C4B0DEAB6CE98E722FC17D7944C28B95127C2659C47CBE",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_pay_channel_with_invalid_payment_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "payment_channel": "C7F634794B79DB40E87179A9D1BF05D05797AE7E92DF8E93FD6656E8C4BE3AE7",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_pay_channel_with_malformed_payment_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "payment_channel": "C7F634794B79DB40E87179A9D1BF05D05797AE7E92DF8E93FD6656E8C4BE3AE",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_methods_ledger_entry_get_ticket_with_non_existent_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account()

    payload = {
        "tx_json": {
            "ticket": {
                "account": account_1.account_id,
                "ticket_seq": rippled_server.ledger_current() - 10
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_deposit_preauth_with_non_existent_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account.account_id,
                "authorized": "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_deposit_preauth_with_malformed_authorized(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account.account_id,
                "authorized": "raRSbvdbhw6ao8Atgedp6AqXTJk4NHSwb"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="malformedAuthorized")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="malformedAddress")


def test_ledger_entry_get_deposit_preauth_with_non_existent_authorized(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    authorized = rippled_server.create_account()

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account.account_id,
                "authorized": authorized.account_id
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_without_default_params(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="unknownOption")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="unknownOption")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_without_default_params_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated",
            "api_version": 2
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    response = rippled_server.get_ledger_data(binary=True, ledger_index=rippled_server.get_txn_sequence(response),
                                              limit=5)
    index = response["state"][0]["index"]

    response = rippled_server.get_ledger_entry(index=index, ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="lgrNotFound")

    clio_response = clio_server.get_ledger_entry(index=index, ledger_index=clio_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    response = rippled_server.get_ledger_data(binary=True, ledger_index=rippled_server.get_txn_sequence(response),
                                              limit=5)
    index = response["state"][0]["index"]

    response = rippled_server.get_ledger_entry(index=index,
                                               ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="lgrNotFound")

    clio_response = clio_server.get_ledger_entry(index=index,
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_with_invalid_account_root(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "account_root": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_directory_with_invalid_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "directory": {
                "owner": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
                "sub_index": 0
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload,
                                                    method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response,
                               method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_offer_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "offer": {
                "account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
                "seq": 359
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload,
                                                    method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response,
                               method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripple_state_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
                    "rsA2LpzuawewSBQXkiju3YQTMzW13pAAdW"
                ],
                "currency": "USD"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload,
                                                    method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_escrow_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "escrow": {
                "owner": "rL4fPHi2FWGwRGRQSH7gBcxkuo2b9NTjKKa",
                "seq": 126
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  method="ledger_entry",
                                                  response_result="malformedOwner")
    test_validator.verify_test(rippled_server, response, method="ledger_entry",
                               response_result="malformedOwner")

    clio_response = clio_server.execute_transaction(payload=payload,
                                                    method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry",
                               response_result="malformedOwner")


def test_ledger_entry_get_escrow_with_non_existent_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "escrow": {
                "owner": account.account_id,
                "seq": 126
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", accounts=[account],
                               response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", accounts=[account],
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_escrow_with_malformed_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "escrow": {
                "owner": "rL4fPHi2FWGwRGRQSH7gBcxkuo2b9NTjK",
                "seq": 126
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedOwner")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedOwner")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_deposit_preauth_invalid_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
                "authorized": "ra5nK24KXen9AHvsdFTKHSANinZseWnPcX"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedOwner")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedOwner")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ticket_with_invalid_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ticket": {
                "account": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpna",
                "ticket_seq": rippled_server.ledger_current() - 10
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response,
                               method="ledger_entry",
                               response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response,
                               method="ledger_entry",
                               response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_ripple_state_with_invalid_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "ripple_state": {
                "accounts": [
                    account.account_id,
                    destination_account.account_id
                ],
                "currency": "aa"
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response,
                               accounts=[account, destination_account],
                               method="ledger_entry",
                               response_result="malformedCurrency")

    clio_response = clio_server.execute_transaction(payload=payload,
                                                    method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response,
                               accounts=[account, destination_account],
                               method="ledger_entry",
                               response_result="malformedCurrency")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_with_invalid_combination_of_params(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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
            "check": {
                "owner": account_1.account_id,
                "sub_index": 0
            },
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry",
                               response_result="internal")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_entry",
                               response_result="malformedRequest")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # TODO: Uncomment this after Rippled issue: https://github.com/XRPLF/rippled/issues/4550 is fixed


def test_ledger_entry_with_mismatch_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payload = {
        "tx_json": {
            "deposit_preauth": {
                "owner": account_2.account_id,
                "authorized": account_1.account_id
            },
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")

    payload = {
        "tx_json": {
            "check": response["node"]["index"],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", accounts=[account_1, account_2],
                               response_result="unexpectedLedgerType")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", accounts=[account_1, account_2],
                               response_result="unexpectedLedgerType")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_nft_page_with_invalid_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "nft_page": "255DD86DDF59D778081A06D02701E9B2C9F4F01DFFFFFFFFFFFFFFFFFFFFFFFF",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_nft_page_with_malformed_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "nft_page": "255DD86DDF59D778081A06D02701E9B2C9F4F01DFFFFFFFFFFFFFFFFFFFFFFF",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_valid_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency": asset_2["currency"],
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_valid_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    amm_account = rippled_server.get_amm_id(asset_1, asset_2)

    account_objects = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")

    payload = {
        "tx_json": {
            "amm": account_objects["account_objects"][0]["index"],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_invalid_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm": "4D35F9225188E69C3CF0077BF8DB7E7B9903D53803DFE87011203BDA7E77FDE2",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_malformed_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm": "4D35F9225188E69C3CF0077BF8DB7E7B9903D53803DFE87011203BDA7E77FDE",
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_invalid_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "INR"
                },
                "asset2": {
                    "currency":  asset_2["currency"],
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_empty_asset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                },
                "asset2": {
                    "currency": "INR",
                    "issuer": alice.account_id
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_invalid_asset_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "AAA"
                },
                "asset2": {
                    "currency":  asset_2["currency"],
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_lower_case_asset_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "xrp"
                },
                "asset2": {
                    "currency":  asset_2["currency"],
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_as_malformed_asset_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "xr"
                },
                "asset2": {
                    "currency":  asset_2["currency"],
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_empty_asset2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_invalid_asset2_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "AAA",
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_lower_case_asset2_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "usd",
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_malformed_asset2_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "US",
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_same_currency_in_asset_and_asset2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "XRP",
                    "issuer": asset_2["issuer"]
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_same_currency_in_asset_and_asset2_without_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "XRP"
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_non_existent_issuer_in_asset2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account()

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "USD",
                    "issuer": alice.account_id
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_get_amm_with_malformed_issuer_in_asset2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "amm": {
                "asset": {
                    "currency": "XRP"
                },
                "asset2": {
                    "currency":  "USD",
                    "issuer": "rhtE16FXfAnsXvZ2ACYscDCoLRhsQSGeZ"
                }
            },
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, method="ledger_entry", response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, method="ledger_entry", response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_for_DIDSet(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    ledger_index = rippled_server.get_did_ledger_index(response)

    response = rippled_server.get_ledger_entry(index=ledger_index)
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry")

    clio_response = clio_server.get_ledger_entry(index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_for_DIDDelete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "DIDSet",
            "Account": alice.account_id,
            "Data": "A1B1",
            "DIDDocument": "A1B1",
            "URI": "A1B1"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "DIDDelete",
            "Account": alice.account_id
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    ledger_index = rippled_server.get_did_ledger_index(response)

    response = rippled_server.get_ledger_entry(index=ledger_index)
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry",
                               response_result="entryNotFound")

    clio_response = clio_server.get_ledger_entry(index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry",
                               response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.smoke
def test_ledger_entry_of_oracle(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "URI": test_data.VALID_URI
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_without_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID, uri=None)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_with_invalid_account_address(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=False)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": bob.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_with_invalid_owner_document_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": (test_data.DEFAULT_ORACLE_DOCUMENT_ID + 1)
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_non_existent_instance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.parametrize("account", [None, "", 123, "InvalidAccountAddress"])
def test_ledger_entry_of_oracle_malformed_account_inputs(fx_rippled, account):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": account,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedAddress")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="malformedAddress")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.parametrize("oracle_document_id", ["", "Invalid", -1])
def test_ledger_entry_of_oracle_malformed_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedDocumentID")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="malformedDocumentID")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://github.com/XRPLF/rippled/issues/4999")
@pytest.mark.parametrize("oracle_document_id", [None, 1.2])
def test_ledger_entry_of_oracle_invalid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="entryNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.parametrize("oracle_document_id", ["1", 0])
def test_ledger_entry_of_oracle_valid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": oracle_document_id,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": oracle_document_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_without_account_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_without_oracle_document_id_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="malformedRequest")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="malformedRequest")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_without_ledger_index_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID
            }
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_entry_of_oracle_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": alice.account_id,
            "Sequence": rippled_server.get_account_sequence(alice),
            "TicketCount": 1
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "oracle": {
                "account": alice.account_id,
                "oracle_document_id": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
                "TicketSequence": rippled_server.get_ticket_sequence(alice)[0]
            },
            "ledger_index": "validated",
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="ledger_entry")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="ledger_entry")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

