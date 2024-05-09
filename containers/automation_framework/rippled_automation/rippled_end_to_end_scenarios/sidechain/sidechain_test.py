#!/usr/bin/env python
import os
import sys
import time
import pytest
from datetime import datetime

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from ..end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from . import sidechain_helper

log = log_helper.get_logger()


@pytest.mark.smoke
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_simple_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.smoke
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_and_xchain_claim(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_NO_CLAIM_ID")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_non_existent_other_chain_destination(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(int(constants.DEFAULT_ACCOUNT_BALANCE) * 2))
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    # Non funded account
    carol = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_ACCOUNT_BALANCE,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": carol.account_id,  # non-existent destination account
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_non_existent_other_chain_destination_transfer_less_than_reserve(fx_rippled, src_chain_name,
                                                                                           dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    # Non funded account
    carol = dest_chain.create_account()
    amount_to_transfer = "100"  # less than reserve

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_to_transfer,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_to_transfer,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": carol.account_id,  # non-existent destination account
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(dest_chain, accounts=[carol], can_have_deleted_account=True)
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_new_destination(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    # Desination account as carol
    carol = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": carol.account_id,  # new destination account
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_auto_claim_no_quorum(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    total_no_of_witnesses = len(witnesses.servers[bridge_type])
    signer_quorum = witnesses.get_quorum(bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    min_out_of_quorum = total_no_of_witnesses - signer_quorum + 1

    log.info("")
    log.info("** Stop {} servers to go out of quorum...".format(min_out_of_quorum))
    for witness_index in range(min_out_of_quorum):
        witnesses.witness_server_stop(witness_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "OtherChainDestination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    for witness_index in range(min_out_of_quorum):
        witnesses.witness_server_start(witness_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                       mainchain=mainchain, sidechain=sidechain)


@pytest.mark.smoke
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    claim_account = dest_chain.create_account(fund=True)
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_stop_all_witnesses_create_account_commit_bring_up_witnesses(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")
    if not src_chain.txn_submit:
        pytest.skip("Applicable for auto-submit mode only")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    log.info("")
    log.info("** Stop all witnesses...")
    for server_index, server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        witnesses.witness_server_stop(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    claim_account = dest_chain.create_account(fund=True)
    add_attestation_payload = None
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        add_attestation_payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=add_attestation_payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob], can_have_deleted_account=True)
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())
    log.info("")
    log.info("** As expected, bob on issuing chain is not created/funded as witnesses are down")

    log.info("")
    log.info("** Start all witnesses...")
    for server_index, server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        witnesses.witness_server_start(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                       mainchain=mainchain, sidechain=sidechain)

    # Re-lookup submission accounts for catch-up
    response = dest_chain.execute_transaction(payload=add_attestation_payload, source_account=alice.account_id)
    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())
    log.info("")
    log.info("** As expected, bob on issuing chain is now created/funded as witnesses are back up")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_destination_exists_with_preauth_enabled(fx_rippled, src_chain_name,
                                                                              dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account(fund=True)

    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=bob)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    xchain_account_claim_count = dest_chain.get_xchain_account_claim_count(dest_chain.door.account_id,
                                                                           bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    # XChainAccountClaimCount should be destroyed as bob on destination account didn't receive funds (preauth set)
    assert dest_chain.get_xchain_account_claim_count(dest_chain.door.account_id,
                                                     bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP) == \
           xchain_account_claim_count + 1, "XChainAccountClaimCount is not destroyed"
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_destination_exists(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_dest_exists_delete_account_claim(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    # Destination account to receive funds after account delete
    claim_account = dest_chain.create_account(fund=True)
    dest_chain.wait_for_ledger_to_advance_for_account_delete(bob)
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": bob.account_id,
            "Destination": claim_account.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": dest_chain.get_account_sequence(bob),
        },
        "secret": bob.master_seed
    }
    delete_response = dest_chain.execute_transaction(payload=payload)

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_twice_claim_twice(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(3 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    create_count = {}
    for iteration in range(1, 3):
        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "Destination": bob.account_id,
                "TransactionType": "XChainAccountCreateCommit",
                "Amount": src_chain.get_xchain_minimum_account_create_amount(),
                "SignatureReward": src_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])
        create_count[iteration] = src_chain.get_xchain_account_create_count()

    claim_account = dest_chain.create_account(fund=True)
    for iteration in range(1, 3):
        for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
            payload = {
                "tx_json": {
                    "bridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                    },
                    "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                    "reward_amount": src_chain.get_xchain_signature_reward(),
                    "door": src_chain.door.account_id,
                    "sending_account": alice.account_id,
                    "destination": bob.account_id,
                    "reward_account": dest_chain.reward_accounts,
                    "create_count": create_count[iteration]
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                              witness_index=witness_index,
                                                                              method="witness_account_create",
                                                                              bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

            payload = {
                "tx_json": {
                    "Account": claim_account.account_id,
                    "TransactionType": "XChainAddAccountCreateAttestation",
                    "OtherChainSource": alice.account_id,
                    "Destination": bob.account_id,
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                    "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                },
                "secret": claim_account.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

            if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                               witness_index=witness_index) or dest_chain.txn_submit:
                break

        test_validator.verify_test(dest_chain, response)
        test_validator.validate_account_balance(dest_chain, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME)])
def test_xchain_create_account_commit_claim_on_source_chain_and_create_account_again_unclog_ledger(fx_rippled,
                                                                                                   src_chain_name,
                                                                                                   dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    clogged_create_count = src_chain.get_xchain_account_create_count()
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": src_chain.reward_accounts,
                "create_count": clogged_create_count
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_WRONG_CHAIN")
    test_validator.validate_account_balance(dest_chain, accounts=[bob], can_have_deleted_account=True)
    test_validator.validate_account_balance(src_chain, accounts=src_chain.reward_accounts.values())

    log.info("")
    log.info("** Verifying if ledger is clogged now for XChainAccountCreateCommit...")

    claim_account = dest_chain.create_account(fund=True)
    carol = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    dave = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": carol.account_id,
            "Destination": dave.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": carol.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[carol])

    clogged_create_count_2 = src_chain.get_xchain_account_create_count()
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": carol.account_id,
                "destination": dave.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": clogged_create_count_2
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": carol.account_id,
                "Destination": dave.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=carol.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[dave], can_have_deleted_account=True)
    test_validator.validate_account_balance(src_chain, accounts=[carol])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** XChainAccountCreateCommit is clogged as expected!")
    log.info("** Now, unclog the ledger for XChainAccountCreateCommit...")
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": clogged_create_count  # to unclog the ledger
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # Ref: RXI-453 - XChainAccountCreateCommit clogs the system until all pending transactions are not successful
    log.info("")
    log.info("Subsequent create_count should have automatically reached quorum.")
    log.info("Triggering with 1 witness should create account")
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": carol.account_id,
                "destination": dave.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": clogged_create_count_2
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": carol.account_id,
                "Destination": dave.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=carol.account_id)

        # Special case: Just to trigger the transaction (Ref: RXI-453)
        if (witness_index + 1) == 1 or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[dave])
    test_validator.validate_account_balance(src_chain, accounts=[carol])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_other_chain_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True,
                                     amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_negative_xrp_followed_by_valid_amount(fx_rippled, src_chain_name,
                                                                            dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": -100,
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")

    claim_account = dest_chain.create_account(fund=True)
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, response_result="invalidParams")
    test_validator.validate_account_balance(dest_chain, accounts=[bob], can_have_deleted_account=True)
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Now, Submit XChainAccountCreateCommit with valid amount...")

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_no_src_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account()
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="srcActNotFound")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_no_dest_field(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            # "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_no_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            # "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_less_than_available_balance(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_account_balance(alice.account_id),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecUNFUNDED_PAYMENT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_less_than_min_account_create_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": int(src_chain.get_xchain_minimum_account_create_amount()) - 1,
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_INSUFF_CREATE_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_more_than_min_account_create_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": int(src_chain.get_xchain_minimum_account_create_amount()) + 1,
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_no_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            # "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_zero_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": "0",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_less_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": int(src_chain.get_xchain_signature_reward()) - 1,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_with_more_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": int(src_chain.get_xchain_signature_reward()) + 1,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_account_commit_amount_in_iou(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_from_multiple_source_accounts(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    carol = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id_by_alice = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": carol.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id_by_carol = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id_by_alice
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice, carol])

    payload = {
        "tx_json": {
            "Account": carol.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id_by_carol
        },
        "secret": carol.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice, carol])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id_by_alice,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim_for_alice = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                                    witness_index=witness_index,
                                                                                    bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim_for_alice, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim_for_alice.get("Amount"),
                "PublicKey": xchain_attestation_claim_for_alice.get("PublicKey"),
                "Signature": xchain_attestation_claim_for_alice.get("Signature"),
                "XChainClaimID": xchain_attestation_claim_for_alice.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim_for_alice.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim_for_alice.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim_for_alice.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id_by_carol,
                "door": src_chain.door.account_id,
                "sending_account": carol.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim_for_carol = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                                    witness_index=witness_index,
                                                                                    bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim_for_carol, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": carol.account_id,
                "Amount": xchain_attestation_claim_for_carol.get("Amount"),
                "PublicKey": xchain_attestation_claim_for_carol.get("PublicKey"),
                "Signature": xchain_attestation_claim_for_carol.get("Signature"),
                "XChainClaimID": xchain_attestation_claim_for_carol.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim_for_carol.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim_for_carol.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim_for_carol.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }

        response = dest_chain.execute_transaction(payload=payload, source_account=carol.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id_by_alice,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice, carol])

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id_by_carol,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice, carol])

    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_multiple_transfers_multiple_claims(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    xchain_claim_ids = {}
    for iteration in range(1, 3):
        log.info("")
        log.info("Get Claim ID for iteration: {}".format(iteration))
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        xchain_claim_ids[iteration] = dest_chain.get_xchain_claim_id(response)

    for iteration in range(1, 3):
        log.info("")
        log.info("XChain Transfer for iteration: {}".format(iteration))
        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "XChainClaimID": xchain_claim_ids[iteration]
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

    for iteration in range(1, 3):
        log.info("")
        log.info("Get attestation for iteration: {}".format(iteration))

        for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
            payload = {
                "tx_json": {
                    "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                    "claim_id": xchain_claim_ids[iteration],
                    "door": src_chain.door.account_id,
                    "sending_account": alice.account_id,
                    "bridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                              witness_index=witness_index,
                                                                              bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

            payload = {
                "tx_json": {
                    "Account": bob.account_id,
                    "TransactionType": "XChainAddClaimAttestation",
                    "OtherChainSource": alice.account_id,
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                },
                "secret": bob.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
            test_validator.verify_test(dest_chain, response, accounts=[bob])

            if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                               witness_index=witness_index) or dest_chain.txn_submit:
                break

    for iteration in range(2, 0, -1):  # Last one first
        log.info("")
        log.info("Claim for iteration: {}".format(iteration))
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "TransactionType": "XChainClaim",
                "XChainClaimID": xchain_claim_ids[iteration],
                "Destination": bob.account_id,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])

        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_base_reserve(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.BASE_RESERVE,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.BASE_RESERVE,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.BASE_RESERVE,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_with_no_reserve_balance(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": src_chain.get_account_balance(alice.account_id, verbose=False),
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecUNFUNDED_PAYMENT")


def test_xchain_mainchain_transfer_10m_xrp(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]

    src_chain = mainchain
    dest_chain = sidechain

    amount_to_transfer = "10000000000000"

    # Create and fund account
    # alice = src_chain.create_account(fund=True,
    #                                  amount=str(int(amount_to_transfer) + int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": constants.TEST_GENESIS_ACCOUNT_ID,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": constants.TEST_GENESIS_ACCOUNT_ID,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_to_transfer,
            "XChainClaimID": xchain_claim_id
        },
        "secret": constants.TEST_GENESIS_ACCOUNT_SEED
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response)

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_to_transfer,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": constants.TEST_GENESIS_ACCOUNT_ID,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": constants.TEST_GENESIS_ACCOUNT_ID,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=constants.TEST_GENESIS_ACCOUNT_ID)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount_to_transfer,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Transfer {} XRP (drops) back to {}".format(amount_to_transfer, constants.TEST_GENESIS_ACCOUNT_ID))

    payload = {
        "tx_json": {
            "Account": constants.TEST_GENESIS_ACCOUNT_ID,
            "OtherChainSource": bob.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": constants.TEST_GENESIS_ACCOUNT_SEED
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response)
    xchain_claim_id = src_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_to_transfer,
            "XChainClaimID": xchain_claim_id
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_to_transfer,
                "claim_id": xchain_claim_id,
                "door": dest_chain.door.account_id,
                "sending_account": bob.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": constants.TEST_GENESIS_ACCOUNT_ID,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": constants.TEST_GENESIS_ACCOUNT_SEED
        }
        response = src_chain.execute_transaction(payload=payload, source_account=bob.account_id)
        test_validator.verify_test(src_chain, response)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": constants.TEST_GENESIS_ACCOUNT_ID,
            "Amount": amount_to_transfer,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": constants.TEST_GENESIS_ACCOUNT_ID,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": constants.TEST_GENESIS_ACCOUNT_SEED
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response)
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=src_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_use_claim_id_from_diff_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # make a new account carol claim with bob's claim id
    carol = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": carol.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol], response_result="tecXCHAIN_BAD_CLAIM_ID")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_witness_before_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account(fund=True)
    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    # skip XChainCommit

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        assert xchain_attestation_claim is None or constants.SIDECHAIN_IGNORE_VALIDATION, "Attestation found"

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_wittness_bad_witness_signature(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    # Bad signature proof
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "TransactionType": "XChainAddClaimAttestation",
            "OtherChainSource": alice.account_id,
            "Amount": "100000",
            "PublicKey": "ED310FC4C590B0E7E1123BAD49C7FFA7E0F60649079F7AC9EB38D3D3EC7824A2AB",
            "Signature": "47E6551C1122431A983B6A808CB2094355CA3EE66797B64BD94BDE0ABE2CE0633CBFD4FE33D37F4917B7EB13CA00BE4B9AC12759ACD4CC99BB88122B5854530A",
            "WasLockingChainSend": 1,
            "XChainClaimID": "10",
            "AttestationRewardAccount": "rpnoVSm4nZMj2nxZujfpjM8JcwhwkeUWTR",
            "AttestationSignerAccount": "rpnoVSm4nZMj2nxZujfpjM8JcwhwkeUWTR",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_withness_mismatch_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "sending_amount": 100,  # mismatch amount
            "claim_id": xchain_claim_id,
            "door": src_chain.door.account_id,
            "sending_account": alice.account_id,
            "bridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        }
    }
    xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                      bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    assert xchain_attestation_claim is None or constants.SIDECHAIN_IGNORE_VALIDATION


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_without_otherchain_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            # "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_witness_no_reward_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                # "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_non_existent_otherchain_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    dummy_account = src_chain.create_account()
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": dummy_account.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob],
                                   response_result="tecXCHAIN_SENDING_ACCOUNT_MISMATCH")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_get_claim_id_from_non_existent_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account()
    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="srcActNotFound")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_get_claim_id_incorrect_secret(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account(fund=True)
    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": "BAD_SECRET"
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="badSecret")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_get_claim_id_without_bridge_section(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account(fund=True)
    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_get_claim_id_with_mismatch_door_accounts(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account(fund=True)
    alice = src_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": sidechain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": mainchain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecNO_ENTRY")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_get_claim_id_with_incorrect_door_accounts(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    bob = dest_chain.create_account(fund=True)
    alice = src_chain.create_account(fund=True)

    dummy_mainchain_door = src_chain.create_account(fund=True)
    dummy_sidechain_door = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": dummy_mainchain_door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": dummy_sidechain_door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecNO_ENTRY")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_incorrect_claim_id(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = str(int(dest_chain.get_xchain_claim_id(response), 16) + 1000)  # future claim id

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_NO_CLAIM_ID")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_claim_id_as_zero(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = 0

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_NO_CLAIM_ID")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_negative_claim_id(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    xchain_claim_id = -10

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_reuse_claim_id_after_failed_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": src_chain.get_account_balance(alice.account_id, verbose=False),
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecUNFUNDED_PAYMENT")

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_create_commit_multiple_times_with_same_claim_id_before_claim(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    for iteration in range(3):
        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "XChainClaimID": xchain_claim_id
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_reuse_claim_id_after_a_claim(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",

            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Reuse claim ID: {}".format(xchain_claim_id))
    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_NO_CLAIM_ID")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_reuse_claim_id_after_a_claim_without_second_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Reuse claim ID: {}".format(xchain_claim_id))

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_NO_CLAIM_ID")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_claim_by_third_party(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # claim by third party carol for bob
    carol = dest_chain.create_account(fund=True)
    payload = {
        "tx_json": {
            "Account": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": carol.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[carol, bob], response_result="tecXCHAIN_BAD_CLAIM_ID")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.longrun
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_delete_before_claim(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # Destination account to receive funds after account delete
    carol = dest_chain.create_account(fund=True)
    dest_chain.wait_for_ledger_to_advance_for_account_delete(bob)
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": bob.account_id,
            "Destination": carol.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": dest_chain.get_account_sequence(bob),
        },
        "secret": bob.master_seed
    }
    delete_response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, delete_response, accounts=[bob, carol], response_result="tecHAS_OBLIGATIONS")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.longrun
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_delete_before_comit(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    # Destination account to receive funds after account delete
    carol = dest_chain.create_account(fund=True)
    dest_chain.wait_for_ledger_to_advance_for_account_delete(bob)
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": bob.account_id,
            "Destination": carol.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": dest_chain.get_account_sequence(bob),
        },
        "secret": bob.master_seed
    }
    delete_response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, delete_response, accounts=[bob, carol], response_result="tecHAS_OBLIGATIONS")

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.longrun
@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_delete_after_claim_resurrect_deleted_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # Destination account to receive funds after account delete
    carol = dest_chain.create_account(fund=True)
    dest_chain.wait_for_ledger_to_advance_for_account_delete(bob)
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": bob.account_id,
            "Destination": carol.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": dest_chain.get_account_sequence(bob),
        },
        "secret": bob.master_seed
    }
    delete_response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, delete_response, accounts=[bob, carol])

    log.info("")
    log.info("Account deleted successfully. Now resurrecting the deleted account...")
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": carol.account_id,
            "Destination": bob.account_id,
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": carol.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_more_than_available_xrp(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": str(int(src_chain.get_account_balance(alice.account_id)) + 1),
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecUNFUNDED_PAYMENT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_from_non_existent_source_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account()
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="srcActNotFound")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_same_account_ids_on_both_chains(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True, wallet=alice.wallet)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_zero_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": 0,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_negative_value_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": -10000,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_decimal_value_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    amount_to_transfer = "10.5"
    amount_str = str(int(float(amount_to_transfer) * 1000000))
    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_str,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_str,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount_str,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_non_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": "10000",
                "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_ISSUER")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_on_ticket(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": alice.account_id,
            "Sequence": src_chain.get_account_sequence(alice),
            "TicketCount": 1
        },
        "secret": alice.master_seed
    }
    ticket_create_response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, ticket_create_response, accounts=[alice])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TicketSequence": src_chain.get_ticket_sequence(alice)[0],
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_enable_deposit_auth_for_same_dest_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=bob)
    # Enable deposit auth for self (bob)
    response = dest_chain.deposit_preauthorize(account_object=bob, third_party_account=bob)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temCANNOT_PREAUTH_SELF")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_preauth_account_with_diff_dest_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    carol = dest_chain.create_account(fund=True)
    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=carol)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol], response_result="tecNO_PERMISSION")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_preauth_account_with_diff_dest_account_disable_preauth(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    carol = dest_chain.create_account(fund=True)
    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=carol)
    # Disable deposit auth
    dest_chain.disable_deposit_auth(account_object=carol)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_diff_dest_account_preauth_enabled(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    carol = dest_chain.create_account(fund=True)
    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=carol)
    # Enable deposit auth on carol
    dest_chain.deposit_preauthorize(account_object=carol, third_party_account=bob)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol], response_result="tecNO_PERMISSION")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Bug https://ripplelabs.atlassian.net/browse/RXI-358 - tecNO_PERMISSION")
    log.info("** Workaround, bob will claim the funds to himself and make a payment to carol in a separate transaction")
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": bob.account_id,
            "Destination": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_claim_from_account_with_preauth_enabled(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    carol = dest_chain.create_account(fund=True)
    # Set deposit auth
    dest_chain.enable_deposit_auth(account_object=bob)
    # Enable deposit auth on carol
    dest_chain.deposit_preauthorize(account_object=bob, third_party_account=carol)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_diff_dest_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # carol to receive funds
    carol = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_diff_non_existent_dest_account(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    # carol doesn't exist
    carol = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol], response_result="tecNO_DST")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # create account carol and claim
    carol = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": carol.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob, carol])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_multiple_transfers_one_claim_with_initial_transfer_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    amount_1 = constants.DEFAULT_TRANSFER_AMOUNT
    amount_2 = str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1)
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_1,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_2,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_1,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount_1,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    if dest_chain.txn_submit:
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
        test_validator.validate_account_balance(src_chain, accounts=[alice])
    else:
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_multiple_transfers_one_claim_with_later_transfer_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    amount_1 = constants.DEFAULT_TRANSFER_AMOUNT
    amount_2 = str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1)
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_1,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": amount_2,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": amount_2,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": amount_2,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])

    # Special case: As this test initiates 2 auto-attestation submissions without a claim,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_skip_unlcaimed_id_and_use_later(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id_for_later = dest_chain.get_xchain_claim_id(response)

    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id_for_now = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id_for_now
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id_for_now,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id_for_now,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Use Claim ID saved for later claim...")
    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id_for_later
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id_for_later,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id_for_later,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_signature_reward_less_than_in_bridge_object(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": int(dest_chain.get_xchain_signature_reward()) - 1,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_signature_reward_more_than_in_bridge_object(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": int(dest_chain.get_xchain_signature_reward()) + 1,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_no_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            # "SignatureReward": dest_chain.get_xchain_signature_reward(sidechain.door.account_id),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_zero_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": 0,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_negative_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": -100,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob],
                               response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_invalid_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": "INVALID_AMOUNT",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_iou_signature_reward(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": {
                "currency": dest_chain.iou_currency,
                "value": dest_chain.get_xchain_signature_reward(),
                "issuer": dest_chain.issuer.account_id
            },
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob],
                               response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_claim_amount_more_than_sending_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1),
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_claim_amount_less_than_sending_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT) - 1),
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_zero_sending_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "sending_amount": 0,
            "claim_id": xchain_claim_id,
            "door": src_chain.door.account_id,
            "sending_account": alice.account_id,
            "bridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        }
    }
    xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                      bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    assert xchain_attestation_claim is None or constants.SIDECHAIN_IGNORE_VALIDATION
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_with_no_sending_amount(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "sending_amount": "",
            "claim_id": xchain_claim_id,
            "door": src_chain.door.account_id,
            "sending_account": alice.account_id,
            "bridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        }
    }
    xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                      bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    assert xchain_attestation_claim is None or constants.SIDECHAIN_IGNORE_VALIDATION, "Attestation found"

    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=[bob])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


def test_create_xchain_bridge_with_issuer_as_side_chain_door_account(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    mainchain_new_door = mainchain.create_account(fund=True)
    sidechain_new_door = sidechain.create_account(fund=True)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": 0,
                "XChainBridge": {
                    "LockingChainDoor": mainchain_new_door.account_id,
                    "IssuingChainDoor": sidechain_new_door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain_new_door.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain_new_door.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_NONDOOR_OWNER")


def test_create_xchain_bridge_with_another_issued_currency_same_door_accounts(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_ISSUES")


def test_create_xchain_bridge_without_bridge_info(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge"
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_same_door_accounts(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                },
                "SignatureReward": chain.get_xchain_signature_reward(),
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_EQUAL_DOOR_ACCOUNTS")


def test_create_xchain_bridge_same_bridge_for_xrp(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                },
                "SignatureReward": chain.get_xchain_signature_reward()
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="tecDUPLICATE")


def test_create_xchain_bridge_exact_same_xrp_bridge_different_door(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Different door for XRP bridge can be only the issuing chain master account
    payload = {
        "tx_json": {
            "Account": constants.MASTER_ACCOUNT_ID,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "IssuingChainDoor": sidechain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": constants.MASTER_ACCOUNT_SEED
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response, response_result="tecDUPLICATE")


def test_create_xchain_bridge_exact_same_iou_bridge_different_door(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    sidechain_issuer_account = mainchain.create_account(fund=True, seed=sidechain.iou_door.master_seed)
    payload = {
        "tx_json": {
            "Account": sidechain_issuer_account.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": sidechain_issuer_account.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response, response_result="tecDUPLICATE")


def test_create_xchain_bridge_same_iou_bridge_for_issued_currency(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.iou_door.account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                },
                "SignatureReward": chain.get_xchain_signature_reward()
            },
            "secret": chain.iou_door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="tecDUPLICATE")


def test_multiple_bridges_different_iou_bridge(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain = mainchain
    dest_chain = sidechain

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # new currency - not to conflict with any existing
    new_currency = hex(round(time.time()) + int("0158415500000000C1F76FF6ECB0BAC6000000000", 16))[2:]

    log.info("")
    log.info("** Update witness configs with currency: {}".format(new_currency))
    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_IOU
    # Stop witness servers, update IOU currency
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_currency(server_index, bridge_type=bridge_type, currency=new_currency)

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create a new bridge for the new currency
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.iou_door.account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": str(new_currency),
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": str(new_currency),
                        "issuer": sidechain.issuer.account_id
                    }
                },
                "SignatureReward": constants.SIGNATURE_REWARDS[chain.name]
            },
            "secret": chain.iou_door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": mainchain.iou_door.account_id,
            "LimitAmount": {
                "currency": new_currency,
                "issuer": mainchain.issuer.account_id,
                "value": str(int(constants.DEFAULT_TRANSFER_AMOUNT) * 100),
            },
        },
        "secret": mainchain.iou_door.master_seed
    }
    rsp = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, rsp)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    # Initiate xchain IOU transfer on the new bridge
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": new_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": new_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": new_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": new_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("Trustline on sidechain for bob...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": new_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": new_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": new_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": new_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_IOU].items():
        payload = {
            "tx_json": {
                "sending_amount": {
                    "currency": new_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
                "claim_id": xchain_claim_id,
                "door": src_chain.iou_door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": new_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": new_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": new_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": new_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": {
                "currency": new_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": new_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": new_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Revert witness configs to currency: {}".format(mainchain.iou_currency))
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_currency(server_index, bridge_type=bridge_type, currency=mainchain.iou_currency)

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)


def test_multiple_bridges_another_xrp_bridge(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_door = mainchain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": new_mainchain_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": new_mainchain_door.account_id,
                "IssuingChainDoor": sidechain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": new_mainchain_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response)


def test_multiple_bridges_another_xrp_bridge_with_new_issuing_chain_door(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_door = mainchain.create_account(fund=True)
    new_sidechain_door = mainchain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": new_mainchain_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": new_mainchain_door.account_id,
                "IssuingChainDoor": new_sidechain_door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": new_mainchain_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response, response_result="temXCHAIN_BRIDGE_BAD_ISSUES")


def test_multiple_bridges_another_iou_bridge_with_existing_issuer(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_iou_door = mainchain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": new_mainchain_iou_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": new_mainchain_iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": new_mainchain_iou_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response)


def test_multiple_bridges_another_iou_bridge_with_new_issuer(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_iou_door = mainchain.create_account(fund=True)
    new_mainchain_issuer = mainchain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": new_mainchain_iou_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": new_mainchain_iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": new_mainchain_issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": new_mainchain_iou_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response)


def test_multiple_bridges_same_iou_bridge_with_diff_issuer(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_issuer = mainchain.create_account(fund=True)
    new_sidechain_issuer = sidechain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": mainchain.iou_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": new_mainchain_issuer.account_id
                },
                "IssuingChainDoor": new_sidechain_issuer.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": new_sidechain_issuer.account_id
                }
            },
            "SignatureReward": mainchain.get_xchain_signature_reward()
        },
        "secret": mainchain.iou_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response, response_result="tecDUPLICATE")


def test_create_xchain_bridge_with_new_door_accounts_for_issued_currency(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_iou_door = {
        mainchain: mainchain.create_account(fund=True),
        sidechain: sidechain.create_account(fund=True)
    }

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": new_iou_door[chain].account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": new_iou_door[mainchain].account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": new_iou_door[sidechain].account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": new_iou_door[sidechain].account_id
                    }
                },
                "SignatureReward": mainchain.get_xchain_signature_reward()
            },
            "secret": new_iou_door[chain].master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


@pytest.mark.longrun
def test_create_xchain_bridge_and_delete_door_account(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_mainchain_door = mainchain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": new_mainchain_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": new_mainchain_door.account_id,
                "IssuingChainDoor": sidechain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "SignatureReward": constants.SIGNATURE_REWARDS[mainchain.name]
        },
        "secret": new_mainchain_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response)

    # Destination account to receive funds after account delete
    alice = mainchain.create_account(fund=True)
    mainchain.wait_for_ledger_to_advance_for_account_delete(new_mainchain_door)
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": new_mainchain_door.account_id,
            "Destination": alice.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": mainchain.get_account_sequence(new_mainchain_door),
        },
        "secret": new_mainchain_door.master_seed
    }
    delete_response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, delete_response, accounts=[alice, new_mainchain_door],
                               response_result="tecHAS_OBLIGATIONS")


def test_create_xchain_bridge_with_new_door_accounts_for_issued_currency_wrong_issuer(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    mainchain_new_iou_door = mainchain.create_account(fund=True)
    sidechain_new_iou_door = sidechain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": mainchain_new_iou_door.account_id,
            "TransactionType": "XChainCreateBridge",
            "XChainBridge": {
                "LockingChainDoor": mainchain_new_iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain_new_iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "SignatureReward": mainchain.get_xchain_signature_reward()
        },
        "secret": mainchain_new_iou_door.master_seed
    }
    response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, response, response_result="temXCHAIN_BRIDGE_BAD_ISSUES")


def test_create_xchain_bridge_duplicate_xrp_bridge_with_iou_bridge_currency(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_ISSUES")


def test_create_xchain_bridge_with_mainchain_xrp_and_sidechain_non_xrp(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": {"currency": "BTC"},
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_mainchain_non_xrp_and_sidechain_xrp(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": {"currency": "BTC"},
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_issued_currency_non_xrp(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {"currency": "BTC"},
                    "IssuingChainIssue": {"currency": "BTC"},
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_issued_currency_invalid_bridge(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": "BTC",  # not in format {"currency": "BTC"}
                    "IssuingChainIssue": "BTC",  # not in format {"currency": "BTC"}
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_signature_reward_no_field(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                # "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_signature_reward_zero_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": 0,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_ISSUES")


def test_create_xchain_bridge_signature_reward_negative_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": -100,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


def test_create_xchain_bridge_signature_reward_iou(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": {
                    "currency": chain.iou_currency,
                    "value": chain.get_xchain_signature_reward(),
                    "issuer": chain.issuer.account_id
                },
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


def test_create_xchain_bridge_with_min_account_create_amount_negative_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": -100,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


def test_create_xchain_bridge_with_min_account_create_amount_zero_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": 0,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


def test_create_xchain_bridge_with_min_account_create_amount_no_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": "",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_min_account_create_amount_invalid_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": "invalid",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {
                        "currency": asset,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainIssue": {
                        "currency": asset,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_create_xchain_bridge_with_min_account_create_amount_iou(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainCreateBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": {
                    "currency": chain.iou_currency,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                    "issuer": chain.issuer.account_id
                },
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


def test_modify_bridge_with_no_change(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": chain.get_xchain_minimum_account_create_amount(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


def test_modify_bridge_for_non_existent_bridge(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": {"currency": asset},
                    "IssuingChainIssue": {"currency": asset}
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_modify_bridge_signature_reward_negative_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": -100,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


def test_modify_bridge_signature_reward_decimal_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": "100.5",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_modify_bridge_signature_reward_iou_wrong_bridge(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": {
                    "currency": mainchain.iou_currency,
                    "value": mainchain.get_xchain_signature_reward(),
                    "issuer": mainchain.issuer.account_id
                },
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_modify_bridge_signature_reward_increase(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": int(chain.get_xchain_signature_reward()) + 1,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": constants.SIGNATURE_REWARDS[dest_chain.name],  # verify default value fails
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # revert chance in signature reward
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": int(chain.get_xchain_signature_reward()) - 1,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_modify_bridge_signature_reward_decrease(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": int(chain.get_xchain_signature_reward()) - 1,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": constants.SIGNATURE_REWARDS[dest_chain.name],  # verify default value fails
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # revert chance in signature reward
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": int(chain.get_xchain_signature_reward()) + 1,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_modify_bridge_signature_reward_zero(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": 0,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": constants.SIGNATURE_REWARDS[dest_chain.name],  # verify default value fails
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_REWARD_MISMATCH")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # revert chance in signature reward
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": constants.SIGNATURE_REWARDS[chain.name],
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


def test_modify_bridge_with_min_account_create_amount_no_change(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": chain.get_xchain_minimum_account_create_amount(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


def test_modify_bridge_with_min_account_create_amount_disable_flag_with_min_amount(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "Flags": 0x00010000,  # disable account creation
                "MinAccountCreateAmount": chain.get_xchain_minimum_account_create_amount(),  # Not allowed with Flags
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temMALFORMED")


def test_modify_bridge_with_min_account_create_amount_disable_flag(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "Flags": 0x00010000,  # disable account creation
                # "MinAccountCreateAmount": chain.get_xchain_minimum_account_create_amount(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

        src_chain, dest_chain = mainchain, sidechain

        # Create and fund account
        alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
        bob = dest_chain.create_account()

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "Destination": bob.account_id,
                "TransactionType": "XChainAccountCreateCommit",
                "Amount": "2000000000",
                "SignatureReward": src_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice],
                                   response_result="tecXCHAIN_CREATE_ACCOUNT_DISABLED")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": constants.DEFAULT_ACCOUNT_BALANCE,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

        src_chain, dest_chain = mainchain, sidechain

        # Create and fund account
        alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
        bob = dest_chain.create_account()

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "Destination": bob.account_id,
                "TransactionType": "XChainAccountCreateCommit",
                "Amount": src_chain.get_xchain_minimum_account_create_amount(),
                "SignatureReward": src_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])


def test_modify_bridge_with_min_account_create_amount_negative_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": -100,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


def test_modify_bridge_with_min_account_create_amount_zero_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # To make it always unique
    asset = str(datetime.now().strftime('%Y%m%d%H%M%S')) + "00000000000000000000000000"

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": 0,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


def test_modify_bridge_with_min_account_create_amount_no_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": "",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_modify_bridge_with_min_account_create_amount_invalid_value(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": "invalid",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="invalidParams")


def test_modify_bridge_with_min_account_create_amount_iou(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.iou_door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": {
                    "currency": mainchain.iou_currency,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                    "issuer": mainchain.issuer.account_id
                },
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": chain.iou_door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="temXCHAIN_BRIDGE_BAD_MIN_ACCOUNT_CREATE_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_modify_bridge_with_min_account_create_amount_increase(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": str(int(chain.get_xchain_minimum_account_create_amount()) + 1),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE,  # default value should fail
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="tecXCHAIN_INSUFF_CREATE_AMOUNT")

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    claim_account = dest_chain.create_account(fund=True)
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # Revert changes to MinAccountCreateAmount
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": str(int(chain.get_xchain_minimum_account_create_amount()) - 1),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_modify_bridge_with_min_account_create_amount_decrease(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": str(int(chain.get_xchain_minimum_account_create_amount()) - 1),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)

    # Create and fund account
    alice = src_chain.create_account(fund=True, amount=str(2 * int(constants.DEFAULT_ACCOUNT_BALANCE)))
    bob = dest_chain.create_account()

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "TransactionType": "XChainAccountCreateCommit",
            "Amount": src_chain.get_xchain_minimum_account_create_amount(),
            "SignatureReward": src_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    claim_account = dest_chain.create_account(fund=True)
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "sending_amount": src_chain.get_xchain_minimum_account_create_amount(),
                "reward_amount": src_chain.get_xchain_signature_reward(),
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "destination": bob.account_id,
                "reward_account": dest_chain.reward_accounts,
                "create_count": src_chain.get_xchain_account_create_count()
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          method="witness_account_create",
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness_account_create")

        payload = {
            "tx_json": {
                "Account": claim_account.account_id,
                "TransactionType": "XChainAddAccountCreateAttestation",
                "OtherChainSource": alice.account_id,
                "Destination": bob.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainAccountCreateCount": xchain_attestation_claim.get("XChainAccountCreateCount"),
                "SignatureReward": xchain_attestation_claim.get("SignatureReward"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": claim_account.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    # Revert changes to MinAccountCreateAmount
    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": chain.door.account_id,
                "TransactionType": "XChainModifyBridge",
                "SignatureReward": chain.get_xchain_signature_reward(),
                "MinAccountCreateAmount": str(int(chain.get_xchain_minimum_account_create_amount()) + 1),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": chain.door.master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_iou_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("Trustline on sidechain for bob...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_IOU].items():
        payload = {
            "tx_json": {
                "sending_amount": {
                    "currency": src_chain.iou_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
                "claim_id": xchain_claim_id,
                "door": src_chain.iou_door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_iou_without_trustline(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    # No trustline on sidechain for bob

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_IOU].items():
        payload = {
            "tx_json": {
                "sending_amount": {
                    "currency": src_chain.iou_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
                "claim_id": xchain_claim_id,
                "door": src_chain.iou_door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id,
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id,
                    }
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_IOU,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="terNO_LINE")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_negative_iou(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("Trustline on sidechain for bob...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }

    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": -100,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_transfer_zero_iou(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("Trustline on sidechain for bob...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }

    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": 0,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice], response_result="temBAD_AMOUNT")


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_xrp_transfer_add_attestation_incorrect_bridge(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_IOU].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        assert xchain_attestation_claim is None or constants.SIDECHAIN_IGNORE_VALIDATION, "Attestation found"

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_xrp_witness_stop_start_maintaining_exact_quorum(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    total_no_of_witnesses = len(witnesses.servers[bridge_type])
    signer_quorum = witnesses.get_quorum(bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    max_offline_to_maintain_quorum = total_no_of_witnesses - signer_quorum

    for witness_index_i, witness_server_i in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        log.info("")
        log.info("** Iteration: {}...".format(witness_index_i + 1))
        log.info("")
        log.info("** Maximum offline witnesses allowed to maintain exact quorum: {} **".format(
            max_offline_to_maintain_quorum))

        for server_index in range(max_offline_to_maintain_quorum):
            index_to_stop = (witness_index_i + server_index) % total_no_of_witnesses
            witnesses.witness_server_stop(index_to_stop, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "OtherChainSource": alice.account_id,
                "TransactionType": "XChainCreateClaimID",
                "SignatureReward": dest_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        xchain_claim_id = dest_chain.get_xchain_claim_id(response)

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "XChainClaimID": xchain_claim_id
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
            payload = {
                "tx_json": {
                    "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                    "claim_id": xchain_claim_id,
                    "door": src_chain.door.account_id,
                    "sending_account": alice.account_id,
                    "bridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                              witness_index=witness_index,
                                                                              bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

            payload = {
                "tx_json": {
                    "Account": bob.account_id,
                    "TransactionType": "XChainAddClaimAttestation",
                    "OtherChainSource": alice.account_id,
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                },
                "secret": bob.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
            test_validator.verify_test(dest_chain, response, accounts=[bob])

            if dest_chain.txn_submit:
                break

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "TransactionType": "XChainClaim",
                "XChainClaimID": xchain_claim_id,
                "Destination": bob.account_id,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])

        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

        for server_index in range(max_offline_to_maintain_quorum):
            index_to_start = (witness_index_i + server_index) % total_no_of_witnesses
            witnesses.witness_server_start(index_to_start, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           mainchain=mainchain, sidechain=sidechain)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_xrp_witness_stop_start_not_maintaining_quorum(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    total_no_of_witnesses = len(witnesses.servers[bridge_type])
    signer_quorum = witnesses.get_quorum(bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    min_out_of_quorum = total_no_of_witnesses - signer_quorum + 1

    log.info("")
    log.info("** Stop {} servers to go out of quorum...".format(min_out_of_quorum))
    for server_index in range(min_out_of_quorum):
        witnesses.witness_server_stop(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])

    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    for server_index in range(min_out_of_quorum):
        witnesses.witness_server_start(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                       mainchain=mainchain, sidechain=sidechain)

    log.info("")
    log.info("** Re-attesting after bringing up all witnesses...")
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])

    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_restart_outside_quorum_stop_within_quorum_transfer_xrp(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    total_no_of_witnesses = len(witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP])
    signer_quorum = witnesses.get_quorum(bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
    max_offline_to_maintain_quorum = total_no_of_witnesses - signer_quorum

    for witness_index_i, witness_server_i in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        log.info("")
        log.info("** Iteration: {}...".format(witness_index_i + 1))
        log.info("")
        log.info("** Maximum offline witnesses allowed to maintain exact quorum: {} **".format(
            max_offline_to_maintain_quorum))

        log.info("")
        log.info("Restart {} server(s) outside quorum...".format(max_offline_to_maintain_quorum))
        for server_index in range(max_offline_to_maintain_quorum):
            index_to_restart = (witness_index_i + server_index) % total_no_of_witnesses
            witnesses.witness_server_stop(index_to_restart, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
            witnesses.witness_server_start(index_to_restart, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           mainchain=mainchain, sidechain=sidechain)

        log.info("")
        log.info("Stop next {} server(s)...".format(max_offline_to_maintain_quorum))
        for server_index in range(max_offline_to_maintain_quorum):
            index_to_restart = (max_offline_to_maintain_quorum + witness_index_i + server_index) % total_no_of_witnesses
            witnesses.witness_server_stop(index_to_restart, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "OtherChainSource": alice.account_id,
                "TransactionType": "XChainCreateClaimID",
                "SignatureReward": dest_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        xchain_claim_id = dest_chain.get_xchain_claim_id(response)

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "XChainClaimID": xchain_claim_id
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
            payload = {
                "tx_json": {
                    "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                    "claim_id": xchain_claim_id,
                    "door": src_chain.door.account_id,
                    "sending_account": alice.account_id,
                    "bridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                              witness_index=witness_index,
                                                                              bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

            payload = {
                "tx_json": {
                    "Account": bob.account_id,
                    "TransactionType": "XChainAddClaimAttestation",
                    "OtherChainSource": alice.account_id,
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                },
                "secret": bob.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
            test_validator.verify_test(dest_chain, response, accounts=[bob])

            if dest_chain.txn_submit:
                break

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "TransactionType": "XChainClaim",
                "XChainClaimID": xchain_claim_id,
                "Destination": bob.account_id,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])

        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

        for server_index in range(max_offline_to_maintain_quorum):
            index_to_restart = (max_offline_to_maintain_quorum + witness_index_i + server_index) % total_no_of_witnesses
            witnesses.witness_server_start(index_to_restart, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           mainchain=mainchain, sidechain=sidechain)


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_restart_all_witnesses_transfer_xrp(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    log.info("")
    log.info("** Restarting all witnesses...")
    for server_index, server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        witnesses.witness_server_stop(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        witnesses.witness_server_start(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                       mainchain=mainchain, sidechain=sidechain)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])

    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_start_witnesses_just_before_attestation(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    log.info("")
    log.info("** Stop all witnesses...")
    for server_index, server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        witnesses.witness_server_stop(server_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("** Start all witnesses just before getting attestation...")
    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        witnesses.witness_server_start(witness_index, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                       mainchain=mainchain, sidechain=sidechain)

    for witness_index, witness_server in witnesses.servers[constants.SIDECHAIN_BRIDGE_TYPE_XRP].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": alice.account_id,
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])

    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


def test_witness_server_info(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    witnesses = fx_rippled["witnesses"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        log.info("")
        payload = {
            "tx_json": {
            }
        }
        witnesses.set_admin_info(payload, bridge_type, witness_index)
        response = witness_server.execute_transaction(payload=payload, method="server_info")
        assert response["status"] == "success", "server_info failed"


def test_witness_server_info_incorrect_password(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    witnesses = fx_rippled["witnesses"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        log.info("")
        payload = {
            "tx_json": {
                "Password": "incorrect_password"
            }
        }
        witnesses.set_admin_info(payload, bridge_type, witness_index)
        response = witness_server.execute_transaction(payload=payload, method="server_info")
        if witnesses.admin_info[bridge_type][witness_index]:
            assert response["error"] == "notAuthorized", "Admin privilege required"
        else:
            assert response["status"] == "success", "server_info failed"


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_xrp_transfer_delete_db_xchain_xrp_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    for iteration in range(1, 3):
        log.info("")
        log.info("** Iteration: {}".format(iteration))

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "OtherChainSource": alice.account_id,
                "TransactionType": "XChainCreateClaimID",
                "SignatureReward": dest_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        xchain_claim_id = dest_chain.get_xchain_claim_id(response)

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                },
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "XChainClaimID": xchain_claim_id
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        for witness_index, witness_server in witnesses.servers[bridge_type].items():
            payload = {
                "tx_json": {
                    "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                    "claim_id": xchain_claim_id,
                    "door": src_chain.door.account_id,
                    "sending_account": alice.account_id,
                    "bridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                              bridge_type=bridge_type)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

            payload = {
                "tx_json": {
                    "Account": bob.account_id,
                    "TransactionType": "XChainAddClaimAttestation",
                    "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.door.account_id,
                        "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        "IssuingChainDoor": sidechain.door.account_id,
                        "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    }
                },
                "secret": bob.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
            test_validator.verify_test(dest_chain, response, accounts=[bob])

            if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                              witness_index=witness_index) or dest_chain.txn_submit:
                break

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "TransactionType": "XChainClaim",
                "XChainClaimID": xchain_claim_id,
                "Destination": bob.account_id,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])
        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

        log.info("")
        log.info("** Stop & delete all witness db...")
        for server_index, server in witnesses.servers[bridge_type].items():
            witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
            witnesses.delete_witness_db(server_index, bridge_type=bridge_type)
            witnesses.witness_server_start(server_index, bridge_type=bridge_type,
                                           mainchain=mainchain, sidechain=sidechain)

        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        # Verify reward account balances after deleting witness db
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_iou_transfer_delete_db_xchain_iou_transfer(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode - Multiple bridges not configured")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_IOU
    for iteration in range(1, 3):
        log.info("")
        log.info("** Iteration: {}".format(iteration))

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "OtherChainSource": alice.account_id,
                "TransactionType": "XChainCreateClaimID",
                "SignatureReward": dest_chain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        xchain_claim_id = dest_chain.get_xchain_claim_id(response)

        log.info("")
        log.info("Trustline on mainchain for alice...")
        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": alice.account_id,
                "LimitAmount": {
                    "currency": src_chain.iou_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": int(constants.DEFAULT_TRANSFER_AMOUNT) * 5,
                },
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": src_chain.issuer.account_id,
                "Destination": alice.account_id,
                "Amount": {
                    "currency": src_chain.iou_currency,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                    "issuer": src_chain.issuer.account_id
                },
            },
            "secret": src_chain.issuer.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        log.info("")
        log.info("Trustline on sidechain for bob...")
        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": bob.account_id,
                "LimitAmount": {
                    "currency": dest_chain.iou_currency,
                    "issuer": dest_chain.issuer.account_id,
                    "value": int(constants.DEFAULT_TRANSFER_AMOUNT) * 5,
                },
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        payload = {
            "tx_json": {
                "Account": alice.account_id,
                "TransactionType": "XChainCommit",
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                },
                "Amount": {
                    "currency": src_chain.iou_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
                "XChainClaimID": xchain_claim_id
            },
            "secret": alice.master_seed
        }
        response = src_chain.execute_transaction(payload=payload)
        test_validator.verify_test(src_chain, response, accounts=[alice])

        for witness_index, witness_server in witnesses.servers[bridge_type].items():
            payload = {
                "tx_json": {
                    "sending_amount": {
                        "currency": src_chain.iou_currency,
                        "issuer": src_chain.issuer.account_id,
                        "value": constants.DEFAULT_TRANSFER_AMOUNT,
                    },
                    "claim_id": xchain_claim_id,
                    "door": src_chain.iou_door.account_id,
                    "sending_account": alice.account_id,
                    "bridge": {
                        "LockingChainDoor": mainchain.iou_door.account_id,
                        "LockingChainIssue": {
                            "currency": mainchain.iou_currency,
                            "issuer": mainchain.issuer.account_id
                        },
                        "IssuingChainDoor": sidechain.iou_door.account_id,
                        "IssuingChainIssue": {
                            "currency": sidechain.iou_currency,
                            "issuer": sidechain.issuer.account_id
                        }
                    }
                }
            }
            xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload,
                                                                              witness_index=witness_index,
                                                                              bridge_type=bridge_type)
            test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

            payload = {
                "tx_json": {
                    "Account": bob.account_id,
                    "TransactionType": "XChainAddClaimAttestation",
                    "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                    "Amount": xchain_attestation_claim.get("Amount"),
                    "PublicKey": xchain_attestation_claim.get("PublicKey"),
                    "Signature": xchain_attestation_claim.get("Signature"),
                    "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                    "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                    "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                    "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                    "XChainBridge": {
                        "LockingChainDoor": mainchain.iou_door.account_id,
                        "LockingChainIssue": {
                            "currency": mainchain.iou_currency,
                            "issuer": mainchain.issuer.account_id
                        },
                        "IssuingChainDoor": sidechain.iou_door.account_id,
                        "IssuingChainIssue": {
                            "currency": sidechain.iou_currency,
                            "issuer": sidechain.issuer.account_id
                        }
                    }
                },
                "secret": bob.master_seed
            }
            response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
            test_validator.verify_test(dest_chain, response, accounts=[bob])

            if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                              witness_index=witness_index) or dest_chain.txn_submit:
                break

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "Amount": {
                    "currency": dest_chain.iou_currency,
                    "issuer": dest_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT
                },
                "TransactionType": "XChainClaim",
                "XChainClaimID": xchain_claim_id,
                "Destination": bob.account_id,
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload)
        test_validator.verify_test(dest_chain, response, accounts=[bob])
        test_validator.validate_account_balance(src_chain, accounts=[alice])
        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

        log.info("")
        log.info("** Stop & delete all witness db...")
        for server_index, server in witnesses.servers[bridge_type].items():
            witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
            witnesses.delete_witness_db(server_index, bridge_type=bridge_type)
            witnesses.witness_server_start(server_index, bridge_type=bridge_type,
                                           mainchain=mainchain, sidechain=sidechain)

        # Special case: As this test initiates 2 auto-attestation submissions,
        # reward account balance calculations are not kept track of
        # Verify reward account balances after deleting witness db
        if not dest_chain.txn_submit:
            test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_all_xrp_witness_signers_and_key_type_with_witness_restart(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    # Stop witness servers, update witness signing seed
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_signing_seed(server_index, bridge_type=bridge_type,
                                      signing_seed_account=src_chain.create_account(verbose=False))

    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=witnesses.get_quorum(bridge_type))
        assert chain.verify_signer_list(response, verbose=False)

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_all_iou_witness_signers_and_key_type_with_witness_restart(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_IOU
    # Stop witness servers, update witness signing seed
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_signing_seed(server_index, bridge_type=bridge_type,
                                      signing_seed_account=src_chain.create_account(verbose=False))

    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.iou_door, signer_entries=signer_entries,
                                         signer_quorum=witnesses.get_quorum(bridge_type))
        assert chain.verify_signer_list(response, verbose=False)

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    log.info("")
    log.info("Trustline on mainchain for alice...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": src_chain.issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": src_chain.iou_currency,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": src_chain.issuer.account_id
            },
        },
        "secret": src_chain.issuer.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    log.info("")
    log.info("Trustline on sidechain for bob...")
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            },
            "Amount": {
                "currency": src_chain.iou_currency,
                "issuer": src_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": {
                    "currency": src_chain.iou_currency,
                    "issuer": src_chain.issuer.account_id,
                    "value": constants.DEFAULT_TRANSFER_AMOUNT,
                },
                "claim_id": xchain_claim_id,
                "door": src_chain.iou_door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.iou_door.account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": mainchain.issuer.account_id
                    },
                    "IssuingChainDoor": sidechain.iou_door.account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": sidechain.issuer.account_id
                    }
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": {
                "currency": dest_chain.iou_currency,
                "issuer": dest_chain.issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT
            },
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.iou_door.account_id,
                "LockingChainIssue": {
                    "currency": mainchain.iou_currency,
                    "issuer": mainchain.issuer.account_id
                },
                "IssuingChainDoor": sidechain.iou_door.account_id,
                "IssuingChainIssue": {
                    "currency": sidechain.iou_currency,
                    "issuer": sidechain.issuer.account_id
                }
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_3_witness_signers(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    no_of_witnesses_to_update = 3
    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    signer_quorum = witnesses.get_quorum(bridge_type)

    # Stop witness servers, update witness signing seed, create/update signer list
    for server_count, (server_index, server) in enumerate(witnesses.servers[bridge_type].items()):
        if server_count == no_of_witnesses_to_update:
            break
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_signing_seed(server_index, bridge_type=bridge_type,
                                      signing_seed_account=src_chain.create_account(verbose=False))

    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=signer_quorum)
        assert chain.verify_signer_list(response, verbose=False)

    # Start witness servers
    for server_count, (server_index, server) in enumerate(witnesses.servers[bridge_type].items()):
        if server_count == no_of_witnesses_to_update:
            break
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_all_witness_signers_with_regular_key(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    signer_quorum = witnesses.get_quorum(bridge_type)

    # Stop witness servers, update witness signing seed, create/update signer list
    signer_entries = []
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)

        log.info("")
        log.info("Create signer account...")
        signer_account = src_chain.create_account(fund=True, verbose=False)
        regular_key_account = src_chain.create_account(fund=True, verbose=False)
        src_chain.add_regular_key_to_account(signer_account, regular_key_account=regular_key_account)
        src_chain.disable_master_key(signer_account)

        log.info("")
        log.info("Create signer account...")
        signer_account = dest_chain.create_account(fund=True, seed=signer_account.master_seed, verbose=False)
        regular_key_account = dest_chain.create_account(fund=True, seed=regular_key_account.master_seed, verbose=False)
        dest_chain.add_regular_key_to_account(signer_account, regular_key_account=regular_key_account)
        dest_chain.disable_master_key(signer_account)

        witnesses.update_signing_seed(server_index, bridge_type=bridge_type, signing_seed_account=regular_key_account,
                                      signing_account=signer_account)

        # Create signer entries
        signer_entry = {
            "SignerEntry": {
                "Account": signer_account.account_id,
                "SignerWeight": 1
            }
        }
        signer_entries.append(signer_entry)

    # Update signer list set on door accounts
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=signer_quorum)
        assert chain.verify_signer_list(response, verbose=False)

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_all_witness_signers_and_not_signer_list(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    signer_quorum = witnesses.get_quorum(bridge_type)

    # Stop witness servers, update witness signing seed
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_signing_seed(server_index, bridge_type=bridge_type,
                                      signing_seed_account=src_chain.create_account(verbose=False))

    # Create/update signer entries and update signer list set on door accounts - skip this step

    # Start witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    log.info("")
    log.info("** Verify xChain transfer without updating signer list set...")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecNO_PERMISSION")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Update signer list set on door accounts...")
    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=signer_quorum)
        assert chain.verify_signer_list(response, verbose=False)

    log.info("")
    log.info("** Verify xChain transfer after signer list set is updated...")
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_all_witness_signers_without_witness_restart(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    signer_quorum = witnesses.get_quorum(bridge_type)

    # Update witness signing seed without stopping witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        # witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.update_signing_seed(server_index, bridge_type=bridge_type,
                                      signing_seed_account=src_chain.create_account(verbose=False))

    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=signer_quorum)
        assert chain.verify_signer_list(response, verbose=False)

    # Start witness servers: step not required as server were not stopped

    log.info("")
    log.info("** Verify xChain transfer without restarting witness servers...")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecNO_PERMISSION")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Restart all witness servers...")
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    log.info("")
    log.info("** Verify xChain transfer after restarting witness servers...")
    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_attest_from_same_signer_until_quorum(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if src_chain.txn_submit:
        pytest.skip("Not applicable for auto-submit mode")

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        # witness_index = 0 : getting attestation from same witness until quorum
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=0,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="tecXCHAIN_CLAIM_NO_QUORUM")
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_update_witness_signers_to_one(fx_rippled, src_chain_name, dest_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]
    witnesses = fx_rippled["witnesses"]
    src_chain, dest_chain = sidechain_helper.assign_chains(fx_rippled, src_chain_name)

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")
    if src_chain.txn_submit:
        pytest.skip("Applicable for non-auto-submit mode only")

    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    bridge_type = constants.SIDECHAIN_BRIDGE_TYPE_XRP
    witness_index = 0
    # Stop witness servers
    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)

    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type],
                                                            signer_weight=witnesses.get_quorum(bridge_type))
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=witnesses.get_quorum(bridge_type))
        assert chain.verify_signer_list(response, verbose=False)

    # Start only one witness server - index 0
    witnesses.witness_server_start(witness_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    # Create and fund account
    alice = src_chain.create_account(fund=True)
    bob = dest_chain.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    payload = {
        "tx_json": {
            "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "claim_id": xchain_claim_id,
            "door": src_chain.door.account_id,
            "sending_account": alice.account_id,
            "bridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        }
    }
    xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                      bridge_type=bridge_type)
    test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "TransactionType": "XChainAddClaimAttestation",
            "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
            "Amount": xchain_attestation_claim.get("Amount"),
            "PublicKey": xchain_attestation_claim.get("PublicKey"),
            "Signature": xchain_attestation_claim.get("Signature"),
            "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
            "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
            "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
            "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
    test_validator.verify_test(dest_chain, response, accounts=[bob])

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())

    log.info("")
    log.info("** Reset signer list with signer weight=1 and restart all witness servers...")
    # Create/update signer entries and update signer list set on door accounts
    signer_entries = sidechain_helper.create_signer_entries(rippled_server=src_chain,
                                                            bridge=witnesses.bridge_info[bridge_type])
    for chain in [mainchain, sidechain]:
        response = chain.set_signer_list(account=chain.door, signer_entries=signer_entries,
                                         signer_quorum=witnesses.get_quorum(bridge_type))
        assert chain.verify_signer_list(response, verbose=False)

    for server_index, server in witnesses.servers[bridge_type].items():
        witnesses.witness_server_stop(server_index, bridge_type=bridge_type)
        witnesses.witness_server_start(server_index, bridge_type=bridge_type, mainchain=mainchain, sidechain=sidechain)

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "OtherChainSource": alice.account_id,
            "TransactionType": "XChainCreateClaimID",
            "SignatureReward": dest_chain.get_xchain_signature_reward(),
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    xchain_claim_id = dest_chain.get_xchain_claim_id(response)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "XChainCommit",
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
            },
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "XChainClaimID": xchain_claim_id
        },
        "secret": alice.master_seed
    }
    response = src_chain.execute_transaction(payload=payload)
    test_validator.verify_test(src_chain, response, accounts=[alice])

    for witness_index, witness_server in witnesses.servers[bridge_type].items():
        payload = {
            "tx_json": {
                "sending_amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "claim_id": xchain_claim_id,
                "door": src_chain.door.account_id,
                "sending_account": alice.account_id,
                "bridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            }
        }
        xchain_attestation_claim = witnesses.get_xchain_attestation_claim(payload=payload, witness_index=witness_index,
                                                                          bridge_type=bridge_type)
        test_validator.verify_test(witnesses, xchain_attestation_claim, method="witness")

        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "AttestationRewardAccount": xchain_attestation_claim.get("AttestationRewardAccount"),
                "AttestationSignerAccount": xchain_attestation_claim.get("AttestationSignerAccount"),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                }
            },
            "secret": bob.master_seed
        }
        response = dest_chain.execute_transaction(payload=payload, source_account=alice.account_id)
        test_validator.verify_test(dest_chain, response, accounts=[bob])

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=bridge_type,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break

    payload = {
        "tx_json": {
            "Account": bob.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "TransactionType": "XChainClaim",
            "XChainClaimID": xchain_claim_id,
            "Destination": bob.account_id,
            "XChainBridge": {
                "LockingChainDoor": mainchain.door.account_id,
                "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                "IssuingChainDoor": sidechain.door.account_id,
                "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
            }
        },
        "secret": bob.master_seed
    }
    response = dest_chain.execute_transaction(payload=payload)
    test_validator.verify_test(dest_chain, response, accounts=[bob])
    test_validator.validate_account_balance(src_chain, accounts=[alice])
    # Special case: As this test initiates 2 auto-attestation submissions,
    # reward account balance calculations are not kept track of
    if not dest_chain.txn_submit:
        test_validator.validate_account_balance(dest_chain, accounts=dest_chain.reward_accounts.values())


def test_create_xchain_bridge_no_clawback(fx_rippled):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if not mainchain.standalone_mode:
        pytest.skip("Not supported on network mode")

    new_iou_door = {
        mainchain: mainchain.create_account(fund=True),
        sidechain: sidechain.create_account(fund=True)
    }

    new_issuer = {
        mainchain: mainchain.create_account(fund=True),
        sidechain: new_iou_door[sidechain]
    }

    for chain in [mainchain, sidechain]:
        account_set_response = chain.account_set(new_issuer[chain],
                                                 flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
        test_validator.verify_test(chain, account_set_response)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": new_iou_door[mainchain].account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": new_issuer[mainchain].account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": new_iou_door[mainchain].master_seed
    }
    create_response = mainchain.execute_transaction(payload=payload)
    test_validator.verify_test(mainchain, create_response)

    for chain in [mainchain, sidechain]:
        payload = {
            "tx_json": {
                "Account": new_iou_door[chain].account_id,
                "TransactionType": "XChainCreateBridge",
                "XChainBridge": {
                    "LockingChainDoor": new_iou_door[mainchain].account_id,
                    "LockingChainIssue": {
                        "currency": mainchain.iou_currency,
                        "issuer": new_issuer[mainchain].account_id
                    },
                    "IssuingChainDoor": new_iou_door[sidechain].account_id,
                    "IssuingChainIssue": {
                        "currency": sidechain.iou_currency,
                        "issuer": new_issuer[sidechain].account_id
                    }
                },
                "SignatureReward": mainchain.get_xchain_signature_reward()
            },
            "secret": new_iou_door[chain].master_seed
        }
        response = chain.execute_transaction(payload=payload)
        test_validator.verify_test(chain, response, response_result="tecNO_PERMISSION")
