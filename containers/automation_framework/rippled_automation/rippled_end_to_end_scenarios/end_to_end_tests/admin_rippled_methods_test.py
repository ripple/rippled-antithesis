#!/usr/bin/env python
import os
import sys
import time

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_key_generation_methods_validation_create(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "secret": "BAWL MAN JADE MOON DOVE GEM SON NOW HAD ADEN GLOW TIRE"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="validation_create")
    test_validator.verify_test(rippled_server, response, accounts=[], method="validation_create")


@pytest.mark.smoke
def test_key_generation_methods_wallet_propose_with_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "seed": "snoPBrXtMeMyMHUVTgbuqAfg1SUTb",
            "key_type":constants.DEFAULT_ACCOUNT_KEY_TYPE
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="wallet_propose")
    test_validator.verify_test(rippled_server, response, accounts=[], method="wallet_propose")


def test_key_generation_methods_wallet_propose_with_no_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "passphrase": "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="wallet_propose")
    test_validator.verify_test(rippled_server, response, accounts=[], method="wallet_propose")


def test_data_mgmt_methods_can_delete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    if rippled_server.rippled_as_clio:
        pytest.skip("Not able to read remote rippled config through Clio server")

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_current")

    payload = {
        "tx_json": {
            "can_delete": response["ledger_current_index"]
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="can_delete")
    advisory_delete_value = helper.get_config_value(section="node_db", key="advisory_delete")
    online_delete_value = helper.get_config_value(section="node_db", key="online_delete")
    if advisory_delete_value == 1 and online_delete_value:
        test_validator.verify_test(rippled_server, response, accounts=[], method="can_delete")
    else:
        log.info(
            "notEnabled - If either online deletion or advisory deletion are not enabled in the server's configuration.")
        test_validator.verify_test(rippled_server, response, accounts=[], method="can_delete",
                                   response_result="notEnabled")


# Remove this test and add asana ticket
@pytest.mark.skip("test_data_mgmt_methods_crawl_shards needs shard server")
def test_data_mgmt_methods_crawl_shards(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "public_key": True,
            "limit": 0
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="crawl_shards")
    test_validator.verify_test(rippled_server, response, accounts=[], method="crawl_shards")


# Remove this test and add asana ticket
@pytest.mark.skip("test_data_mgmt_methods_download_shard needs shard server")
def test_data_mgmt_methods_download_shard(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "shards": [
                {"index": 1, "url": "https://example.com/1.tar.lz4"},
                {"index": 2, "url": "https://example.com/2.tar.lz4"},
                {"index": 5, "url": "https://example.com/5.tar.lz4"}
            ]
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="download_shard")
    test_validator.verify_test(rippled_server, response, accounts=[], method="download_shard")


# Remove this test and add asana ticket
@pytest.mark.skip("test_data_mgmt_methods_node_to_shard needs shard server")
def test_data_mgmt_methods_node_to_shard(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "action": "start"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="node_to_shard")
    test_validator.verify_test(rippled_server, response, accounts=[], method="node_to_shard")


def test_signing_methods_sign(fx_rippled):
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


def test_signing_methods_sign_for(fx_rippled):
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
                               accounts=[account_1, account_2])


@pytest.mark.daemon_mode_only  # test not supported in standalone or reporting server modes
def test_peer_mgmt_methods_connect(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "ip": "192.170.145.88",
            "port": 51235
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="connect")
    test_validator.verify_test(rippled_server, response, accounts=[], method="connect")


@pytest.mark.skip("RIP-591 - mismatch public key")
def test_peer_mgmt_methods_peer_reservations_add_list_del(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="peer_reservations_list")
    original_no_of_reservations = len(response["reservations"])

    log.info("Add peer reservation...")
    payload = {
        "tx_json": {
            "public_key": "n9Jt8awsPzWLjBCNKVEEDQnw4bQEPjezfcQ4gttD1UzbLT1FoG99",
            "description": "Ripple s1 server 'WOOL'"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="peer_reservations_add")
    test_validator.verify_test(rippled_server, response, accounts=[], method="peer_reservations_add")

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="peer_reservations_list")
    test_validator.verify_test(rippled_server, response, accounts=[], method="peer_reservations_list")
    assert len(response["reservations"]) == (original_no_of_reservations + 1), "Peer reservation is not added"
    log.info("  Peer reservation added")

    log.info("Delete peer reservation...")
    payload = {
        "tx_json": {
            "public_key": "n9Jt8awsPzWLjBCNKVEEDQnw4bQEPjezfcQ4gttD1UzbLT1FoG99"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="peer_reservations_del")
    test_validator.verify_test(rippled_server, response, accounts=[], method="peer_reservations_del")

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="peer_reservations_list")
    test_validator.verify_test(rippled_server, response, accounts=[], method="peer_reservations_list")
    assert len(response["reservations"]) == original_no_of_reservations, "Peer reservation not deleted"
    log.info("  Peer reservation deleted")


def test_status_debugging_methods_consensus_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="consensus_info")
    test_validator.verify_test(rippled_server, response, accounts=[], method="consensus_info")


def test_status_debugging_methods_feature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    feature = "4C97EBA926031A7CF7D7B36FDE3ED66DDA5421192D63DE53FFB46E43B9DC8373"

    payload = {
        "tx_json": {
            "feature": feature,
            "vetoed": False
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="feature")
    test_validator.verify_test(rippled_server, response, accounts=[], method="feature")
    assert response[feature], "{} not found".format(feature)


def test_status_debugging_methods_fetch_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "clear": False
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="fetch_info")
    test_validator.verify_test(rippled_server, response, accounts=[], method="fetch_info")


def test_status_debugging_methods_get_counts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
            "min_count": 100
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="get_counts")
    test_validator.verify_test(rippled_server, response, accounts=[], method="get_counts")


def test_status_debugging_methods_validator_list_sites(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="validator_list_sites")
    test_validator.verify_test(rippled_server, response, accounts=[], method="validator_list_sites")


def test_status_debugging_methods_validators(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="validators")
    test_validator.verify_test(rippled_server, response, accounts=[], method="validators")
