#!/usr/bin/env python
import os
import sys
import time

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_account_methods_account_channels(fx_rippled):
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
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")


def test_account_methods_account_currencies(fx_rippled):
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
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_currencies(account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_currencies")


def test_account_methods_account_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")


def test_account_methods_account_lines(fx_rippled):
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
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_lines(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_lines")


def test_account_methods_account_objects_offer(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="offer")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_ripplestate(fx_rippled):
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
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "type": "state",
            "deletion_blockers_only": False,
            "limit": 10
        },
    }
    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="state")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_signerlist(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="signer_list")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_escrow(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="escrow")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_paychannel(fx_rippled):
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
            "SettleDelay": 80,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="payment_channel")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_check(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="check")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_deposit_preauth(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)

    # Set deposit auth
    account_2 = rippled_server.create_account(fund=True)
    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.deposit_preauthorize(account_object=account_1, third_party_account=account_2)

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="deposit_preauth")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")


def test_account_methods_account_objects_ticket(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="ticket")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")


def test_account_methods_account_offers(fx_rippled):
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

    response = rippled_server.get_account_offers(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_offers")


def test_account_methods_account_tx(fx_rippled):
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

    response = rippled_server.get_account_tx(account_1.account_id, limit=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_tx")


def test_account_methods_gateway_balances(fx_rippled):
    # validating all three cases for one account i.e., assets, balances, obligations.
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)
    account_4 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "CUC",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "CUC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "INR",
                "issuer": account_4.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_4.account_id,
            "Destination": account_1.account_id,
            "Amount": {
                "currency": "INR",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_4.account_id
            },
        },
        "secret": account_4.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "hotwallet": account_2.account_id,
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4],
                               method="gateway_balances")
    assert response["balances"], "balances not found: {}".format(response)
    assert response["obligations"], "obligations not found: {}".format(response)
    assert response["assets"], "assets not found: {}".format(response)


def test_account_methods_gateway_balances_with_obligations_overflow(fx_rippled):
    # verifying list of accounts in hotwallet and validating balances.

    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "9999999999999999e80",
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": "9999999999999999e80",
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "9999999999999999e80",
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "USD",
                "value": "9999999999999999e80",
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert response["obligations"], "obligations not found: {}".format(response)


def test_account_methods_noripple_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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
            "account": account_1.account_id,
            "ledger_index": "current",
            "limit": 2,
            "role": "gateway",
            "transactions": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="noripple_check")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")


def test_ledger_methods_ledger(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated",
            "transactions": False,
            "expand": False,
            "owner_funds": False
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger")
    test_validator.verify_test(rippled_server, response, accounts=[], method="ledger")


def test_ledger_methods_ledger_closed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_closed")
    test_validator.verify_test(rippled_server, response, accounts=[], method="ledger_closed")


def test_ledger_methods_ledger_current(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_current")
    test_validator.verify_test(rippled_server, response, accounts=[], method="ledger_current")


def test_ledger_methods_account_ledger_data(fx_rippled):
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

    payload = {
        "tx_json": {
            "binary": True,
            "ledger_index": rippled_server.get_txn_sequence(response),
            "limit": 5
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_data")


def test_ledger_methods_ledger_entry_get_ledger_object(fx_rippled):
    # log.info("HOW TO DO THIS (https://xrpl.org/ledger_entry.html#get-ledger-object-by-id)?")
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

    # Get index from ledger_data
    payload = {
        "tx_json": {
            "binary": True,
            "ledger_index": rippled_server.get_txn_sequence(response),
            "limit": 5
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    index = response["state"][0]["index"]

    payload = {
        "tx_json": {
            "index": index,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")


def test_ledger_methods_ledger_entry_get_account_root_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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


def test_ledger_methods_ledger_entry_get_directory_node_object(fx_rippled):
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


def test_ledger_methods_ledger_entry_get_offer_object(fx_rippled):
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


def test_ledger_methods_ledger_entry_get_ripplestate_object(fx_rippled):
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


def test_ledger_methods_ledger_entry_get_check_object(fx_rippled):
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
            "check": rippled_server.get_check_ids(account_1)[0],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "Check", "Check not found"


def test_ledger_methods_ledger_entry_get_escrow_object(fx_rippled):
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


def test_ledger_methods_ledger_entry_get_paychannel_object(fx_rippled):
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
            "SettleDelay": 80,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    channels = rippled_server.get_account_channels(account_1.account_id)
    payload = {
        "tx_json": {
            "payment_channel": channels['channels'][0]['channel_id'],
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_entry")
    assert response["node"]["LedgerEntryType"] == "PayChannel", "PayChannel not found"


@pytest.mark.skip(reason="https://ripplelabs.atlassian.net/browse/RIP-615")
def test_ledger_methods_ledger_entry_get_amm_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account = rippled_server.create_account(fund=True)

    xrp_asset = constants.XRP_ASSET
    usd_amount = {
        "currency": "USD",
        "issuer": account.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_DEPOSIT
    }
    xrp_amount = constants.DEFAULT_AMM_XRP_CREATE

    payload = {
        "tx_json": {
            "TransactionType": "AMMCreate",
            "Account": account.account_id,
            "Amount": xrp_amount,
            "Amount2": usd_amount,
            "TradingFee": constants.DEFAULT_AMM_TRADING_FEE,
            "Fee": constants.DEFAULT_AMM_CREATE_FEE
        },
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  secret=account.master_seed)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    payload = {
        "tx_json": {
            "amm": {
                "asset": xrp_asset,
                "asset2": usd_amount,
                "ledger_index": "validated"
            }
        }
    }
    response = rippled_server.execute_transaction(payload=payload,
                                                  method="ledger_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account])
    assert response["node"]["LedgerEntryType"] == "AMM", "AMM not found"


def test_transaction_methods_submit(fx_rippled):
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


def test_transaction_methods_submit_only_mode(fx_rippled):
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


def test_transaction_methods_submit_multisigned(fx_rippled):
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


def test_transaction_methods_transaction_entry(fx_rippled):
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
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(response["tx_json"]["hash"], verbose=False)

    payload = {
        "tx_json": {
            "tx_hash": tx_response["hash"],
            "ledger_index": tx_response["ledger_index"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="transaction_entry")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="transaction_entry")


def test_transaction_methods_tx(fx_rippled):
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
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="tx")


def test_transaction_methods_tx_history(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "start": 0
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="tx_history")
    test_validator.verify_test(rippled_server, response, method="tx_history")


def test_order_book_methods_book_offers(fx_rippled):
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

    response = rippled_server.get_book_offers(response=offer_create_response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="book_offers")


def test_order_book_methods_deposit_authorized(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account accounts
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_2)

    payload = {
        "tx_json": {
            "source_account": account_1.account_id,
            "destination_account": account_2.account_id,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    assert not response["deposit_authorized"], \
        "'deposit_authorized' set to True for non-preauthorized destination account"

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)
    payload = {
        "tx_json": {
            "source_account": account_1.account_id,
            "destination_account": account_2.account_id,
            "ledger_index": "validated"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")


def test_order_book_methods_ripple_path_find(fx_rippled):
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
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "destination_account": account_2.account_id,
            "destination_amount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "source_account": account_1.account_id,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ripple_path_find")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ripple_path_find")


def test_paychan_methods_channel_authorize(fx_rippled):
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
            "SettleDelay": 80,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    channels = rippled_server.get_account_channels(account_1.account_id)
    payload = {
        "tx_json": {
            "channel_id": channels['channels'][0]['channel_id'],
            "seed": account_1.master_seed,
            "key_type": constants.DEFAULT_ACCOUNT_KEY_TYPE,
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="channel_authorize")


def test_paychan_methods_channel_verify(fx_rippled):
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
            "SettleDelay": 80,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    # Get signature
    channels = rippled_server.get_account_channels(account_1.account_id)
    payload = {
        "tx_json": {
            "channel_id": channels['channels'][0]['channel_id'],
            "seed": account_1.master_seed,
            "key_type": constants.DEFAULT_ACCOUNT_KEY_TYPE,
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")

    payload = {
        "tx_json": {
            "channel_id": channels['channels'][0]['channel_id'],
            "public_key": account_1.public_key_hex,
            "signature": response["signature"],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="channel_verify")


def test_server_info_methods_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="fee")
    test_validator.verify_test(rippled_server, response, accounts=[], method="fee")


def test_server_info_methods_manifest(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "public_key": "nHUFE9prPXPrHcG3SkwP1UzAQbSphqyQkQK9ATXLZsfkezhhda3p"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(rippled_server, response, accounts=[], method="manifest")


def test_server_info_methods_server_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="server_info")
    test_validator.verify_test(rippled_server, response, accounts=[], method="server_info")


def test_server_info_methods_server_state(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="server_state")
    test_validator.verify_test(rippled_server, response, accounts=[], method="server_state")


def test_utility_methods_ping(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="ping")
    test_validator.verify_test(rippled_server, response, accounts=[], method="ping")


def test_utility_methods_random(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="random")
    test_validator.verify_test(rippled_server, response, accounts=[], method="random")
