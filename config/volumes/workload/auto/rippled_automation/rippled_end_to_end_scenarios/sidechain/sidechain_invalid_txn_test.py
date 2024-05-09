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


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_other_chain_source(fx_rippled, src_chain_name, dest_chain_name):
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

        invalid_value = src_chain.create_account(fund=False)
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                # "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "OtherChainSource": invalid_value.account_id,  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_amount(fx_rippled, src_chain_name, dest_chain_name):
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
                # "Amount": xchain_attestation_claim.get("Amount"),
                "Amount": str(int(xchain_attestation_claim.get("Amount")) + 1),  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_amount(fx_rippled, src_chain_name, dest_chain_name):
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
                # "Amount": xchain_attestation_claim.get("Amount"),
                "Amount": str(int(xchain_attestation_claim.get("Amount")) + 1),  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_public_key(fx_rippled, src_chain_name, dest_chain_name):
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

        public_key = xchain_attestation_claim.get("PublicKey")
        invalid_value = public_key.replace(public_key[1], '9')
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                # "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "PublicKey": invalid_value,  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temMALFORMED")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_string_public_key(fx_rippled, src_chain_name, dest_chain_name):
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
                # "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "PublicKey": "string public key",  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_signature(fx_rippled, src_chain_name, dest_chain_name):
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

        signature = xchain_attestation_claim.get("Signature")
        invalid_value = hex(int(signature, 16) + 1)[2:]
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                # "Signature": xchain_attestation_claim.get("Signature"),
                "Signature": invalid_value,  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_xchain_claim_id(fx_rippled, src_chain_name, dest_chain_name):
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

        chain_claim_id = xchain_attestation_claim.get("XChainClaimID")
        invalid_value = hex(int(chain_claim_id, 16) + 1)[2:]
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                # "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "XChainClaimID": invalid_value,  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_string_xchain_claim_id(fx_rippled, src_chain_name, dest_chain_name):
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

        chain_claim_id = xchain_attestation_claim.get("XChainClaimID")
        invalid_value = hex(int(chain_claim_id, 16) + 1)[2:]
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                # "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                "XChainClaimID": "XChainClaimID",  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="invalidParams")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


@pytest.mark.parametrize("src_chain_name, dest_chain_name", [(constants.MAINCHAIN_NAME, constants.SIDECHAIN_NAME),
                                                             (constants.SIDECHAIN_NAME, constants.MAINCHAIN_NAME)])
def test_xchain_add_attestation_invalid_was_locking_chain_send(fx_rippled, src_chain_name, dest_chain_name):
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

        was_locking_chain_send = xchain_attestation_claim.get("WasLockingChainSend")
        invalid_value = 0 if was_locking_chain_send == 1 else 1
        payload = {
            "tx_json": {
                "Account": bob.account_id,
                "TransactionType": "XChainAddClaimAttestation",
                "OtherChainSource": xchain_attestation_claim.get("OtherChainSource"),
                "Amount": xchain_attestation_claim.get("Amount"),
                "PublicKey": xchain_attestation_claim.get("PublicKey"),
                "Signature": xchain_attestation_claim.get("Signature"),
                "XChainClaimID": xchain_attestation_claim.get("XChainClaimID"),
                # "WasLockingChainSend": xchain_attestation_claim.get("WasLockingChainSend"),
                "WasLockingChainSend": invalid_value,  # Invalid value
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
        test_validator.verify_test(dest_chain, response, accounts=[bob], response_result="temXCHAIN_BAD_PROOF")

        if sidechain_helper.reached_quorum(witnesses=witnesses, bridge_type=constants.SIDECHAIN_BRIDGE_TYPE_XRP,
                                           witness_index=witness_index) or dest_chain.txn_submit:
            break


