#!/usr/bin/env python
import os
import pytest
import sys


path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_account_needs_xrp_plus_fees_to_create_signers_list(fx_rippled):
    '''
    1. Create an account and fund it with 20 xrp only
    2. Do a wallet propose create 1 other signers
    3. Prepare a signers list transactions and submit it and verify it cannot be done
    4. Now fund the account with more money and verify signers list transactions can be done
    '''
    rippled_server = fx_rippled["rippled_server"]

    account = rippled_server.create_account(fund=True, amount=10000000)
    signer_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry":
                        {
                            "Account": signer_1.account_id,
                            "SignerWeight": 1
                        }
                }
            ]
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account],
                               response_result='tecINSUFFICIENT_RESERVE')

    # Fund the account with more xrp, enough to add a signer
    rippled_server.fund_account(account.account_id)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry":
                        {
                            "Account": signer_1.account_id,
                            "SignerWeight": 1
                        }
                }
            ]
        },
        "secret": account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)


@pytest.mark.smoke
def test_create_signers_list_and_use_to_send_payment(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry":
                        {
                            "Account": signer_1.account_id,
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
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2])


def test_signers_list_maximum_size(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    signer_accounts = {}
    signer_accounts_to_create = constants.MAX_SIGNER_ENTRIES + 1
    log.info("")
    log.info("Create {} signer accounts".format(signer_accounts_to_create))
    for count in range(signer_accounts_to_create):
        signer_accounts[count] = rippled_server.create_account(verbose=False)

    signer_entries = []
    signer_entries_to_create = constants.MAX_SIGNER_ENTRIES
    log.info("")
    log.info("Create signer entries with {} accounts".format(signer_entries_to_create))
    for count in range(signer_entries_to_create):
        signer_entry = {
                           "SignerEntry": {
                               "Account": signer_accounts[count].account_id,
                               "SignerWeight": 1
                           }
                       }
        signer_entries.append(signer_entry)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": signer_entries
        },
        "secret": alice.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    signer_entries = []
    signer_entries_to_create = constants.MAX_SIGNER_ENTRIES + 1
    log.info("")
    log.info("Create signer entries with {} accounts".format(signer_entries_to_create))
    for count in range(signer_entries_to_create):
        signer_entry = {
                           "SignerEntry": {
                               "Account": signer_accounts[count].account_id,
                               "SignerWeight": 1
                           }
                       }
        signer_entries.append(signer_entry)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": signer_entries
        },
        "secret": alice.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result='temMALFORMED')


def test_account_cannot_be_used_as_multisigner_for_ownself(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result='temBAD_SIGNER')


def test_signer_weight_cannot_be_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 0
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result='temBAD_WEIGHT')


def test_signer_weight_cannot_be_more_than_maximum_allowed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": constants.DEFAULT_MAX_SIGNER_WEIGHT
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
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": constants.DEFAULT_MAX_SIGNER_WEIGHT + 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="invalidParams")


def test_account_cannot_have_duplicate_signer_in_the_signer_list(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                },
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result='temBAD_SIGNER')


def test_signer_list_with_zero_quorum(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 0,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="temMALFORMED")


def test_create_signer_list_with_quorum_impossible_to_reach(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)
    signer_2 = rippled_server.create_account(fund=True)
    signer_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 4,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                },
                {
                    "SignerEntry": {
                        "Account": signer_2.account_id,
                        "SignerWeight": 1
                    }
                },
                {
                    "SignerEntry": {
                        "Account": signer_3.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result="temBAD_QUORUM")


# A phantom account does not create transactions. It is only used for signing
def test_attach_phantom_signer_account_to_signer_list_verify_its_possible(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=False)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
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
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2])


def test_duplicate_phantom_signer_account_to_signer_list_fails(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=False)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                },
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1], response_result='temBAD_SIGNER')


def test_using_account_to_sign_which_is_not_a_part_of_signers_list(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)
    not_signer_account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
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
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": not_signer_account_1.account_id,
        "secret": not_signer_account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2],
                               response_result='tefBAD_SIGNATURE')


def test_disable_lone_signer_list(fx_rippled):
    """
    1. Create a signer list
    2. Now disable master key: verify its possible
    3. Now disable signer list: verify its not possible
    """
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    rippled_server.disable_master_key(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SignerQuorum": 0,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1],
                               response_result='tecNO_ALTERNATIVE_KEY')


def test_removing_regular_key_when_signers_list_available(fx_rippled):
    """
    1. Create regular key
    2. disable master key
    3. Create a signer list
    4. Now disable regular key: verify its possible
    5. Now disable signer list: verify its not possible
    """
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    rippled_server.add_regular_key_to_account(account_1)
    rippled_server.disable_master_key(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "SetRegularKey",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SignerQuorum": 0,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1],
                               response_result='tecNO_ALTERNATIVE_KEY')


def test_signers_list_can_be_removed_when_master_key_enabled(fx_rippled):
    pass
    """
    1. Create a signer list
    2. Now disable master key: verify its possible
    3. Now enable master key verify its possible
    4. Now disable signer list: verify its possible
    """
    rippled_server = fx_rippled["rippled_server"]
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    rippled_server.disable_master_key(account_1)

    # NOW ENABLE MASTER KEY AGAIN
    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": "",
            "ClearFlag": 4
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])

    # NOW VERIFY WE CAN REMOVE THE SIGNERS LIST FROM THE ACCOUNT
    payload = {
        "tx_json": {
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SignerQuorum": 0,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2],
                               response_result='tefNOT_MULTI_SIGNING')


def test_signers_list_can_be_removed_when_regular_key_is_available(fx_rippled):
    pass
    """
    1. Create a signer list
    2. Enable regular key
    3. Disable Master key
    4. Now disable regular key: verify its possible
    5. Now enable regular key verify its possible
    6. Now disable signer list: verify its possible
    """

    rippled_server = fx_rippled["rippled_server"]
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # Now send a transaction to set regular key for the account
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    regular_key = rippled_server.add_regular_key_to_account(account_1)
    rippled_server.disable_master_key(account_1)

    rippled_server.remove_regular_key_from_account(account_1)

    # NOW ADD A REGULAR KEY AGAIN
    payload = {
        "tx_json": {
            "TransactionType": "SetRegularKey",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": "",
            "RegularKey": regular_key.account_id
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])

    # VERIFY REGULAR KEY WAS ADDED TO THE ACCOUNT BY SENDING A PAYMENT TYPE TX
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id
        },
        "secret": regular_key.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    # NOW VERIFY WE CAN REMOVE THE SIGNERS LIST FROM THE ACCOUNT
    payload = {
        "tx_json": {
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": "",
            "SignerQuorum": 0
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2],
                               response_result='tefNOT_MULTI_SIGNING')


def test_zero_fees_to_multisign_payment_fail(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
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
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": "",
            "Fee": 0
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1],
                               response_result="invalidParams")


def test_multisign_trust_set_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    # NOW EXECUTE A TRUST SET TX
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "Flags": 262144,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "100"
            },
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])


def test_multisign_offer_create_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    # NOW EXECUTE A OFFER CREATE TX
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "Flags": 262144,
            "TakerGets": "6000000",
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1, account_2],
                               response_result="tecKILLED", offer_crossing=False)


def test_multisign_signers_list_set_transaction(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)
    signer_2 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    # NOW EXECUTE A OFFER CREATE TX
    payload = {
        "tx_json": {
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "Flags": 262144,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                },
                {
                    "SignerEntry": {
                        "Account": signer_2.account_id,
                        "SignerWeight": 1
                    }
                }
            ],
            "Sequence": rippled_server.get_account_sequence(account_1),
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])


def test_masterSigners(fx_rippled):
    """
    Give alice a regular key and a signers list.
    Now give regular keys to signers on alicess signers list.
    Assert: Now use the master keys of the users on the signers list to sign a tranaction and it should pass
    """
    # Give alice a regular key and a signers list.
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)
    signer_2 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    # Now give regular keys to signers on alice's signers list.
    rippled_server.add_regular_key_to_account(signer_1)
    rippled_server.add_regular_key_to_account(signer_2)

    # Now use the master keys of the users on the signers list to sign a transaction, it should pass
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])


def test_regularSigners(fx_rippled):
    """
    Attach 2 signers to alice. Give everyone regular keys.
    Disable cheri's master key to mix things up. Attempt a multisigned transaction that meets the quorum.
    """
    # Give alice a regular key and a signers list.
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    signer_1 = rippled_server.create_account(fund=True)
    signer_2 = rippled_server.create_account(fund=True)

    # ADDING A SIGNER TO THE ACCOUNT
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": signer_1.account_id,
                        "SignerWeight": 1
                    }
                }
            ]
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    # Now give regular keys to signers on alice's signers list.
    rippled_server.add_regular_key_to_account(signer_1)
    rippled_server.add_regular_key_to_account(signer_2)

    # Now use the master keys of the users on the signers list to sign a transaction, it should pass
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Flags": 2147483648,
            "Sequence": rippled_server.get_account_sequence(account_1),
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SigningPubKey": ""
        },
        "account": signer_1.account_id,
        "secret": signer_1.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")

    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[account_1])


def test_heterogeneousSigners(fx_rippled):
    pass


def test_multisigningMultisigner(fx_rippled):
    pass


def test_signForHash(fx_rippled):
    pass
