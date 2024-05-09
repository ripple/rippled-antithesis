#!/usr/bin/env python
import os
import pytest
import random
import string
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_multiple_nft_mint_with_same_token_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    # Mint 2nd NFT
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_nft_mint_with_low_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=10000000)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1],
                               response_result="tecINSUFFICIENT_RESERVE")


def test_mint_nft_optional_uri_as_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "URI": "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi",
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_optional_uri_as_hex_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
    hex_uri = uri.encode('utf-8').hex()
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "URI": hex_uri,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_mint_nft_optional_invalid_uri(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    uri = ""
    hex_uri = uri.encode('utf-8').hex()
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "URI": hex_uri,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_mint_nft_optional_uri_with_more_than_265_chars(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    uri_length = 257
    uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
    for count in range(uri_length - len(uri)):
        uri += random.choice(string.ascii_letters)

    hex_uri = uri.encode('utf-8').hex()
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "URI": hex_uri,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_mint_nft_optional_transfer_fee_negative(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "TransferFee": -1,
            "Flags": 8,  # tfTransferable
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_optional_transfer_fee_zero(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "TransferFee": 0,
            "Flags": 8,  # tfTransferable
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_mint_nft_optional_transfer_fee_decimal(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "TransferFee": 10.5,
            "Flags": 8,  # tfTransferable
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_optional_transfer_fee_50000_plus(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "TransferFee": 50001,
            "Flags": 8,  # tfTransferable
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1],
                               response_result="temBAD_NFTOKEN_TRANSFER_FEE")


def test_mint_nft_optional_transfer_fee_without_flag_tfTransferable(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "TransferFee": 50,
            # "Flags": 8,  # tfTransferable
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_mint_nft_optional_memos(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
    hex_uri = uri.encode('utf-8').hex()

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "URI": hex_uri,
            "Memos": [
                {
                    "Memo": {
                        "MemoType":
                            "687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E65726963",
                        "MemoData": "72656E74"
                    }
                }
            ],
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_mint_nft_with_seed_mismatch(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="badSecret")


def test_mint_nft_without_token_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_with_negative_token_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": -10
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_with_higher_token_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": "4294967296"  # Taxon identifiers greater than 0xFFFFFFFF (4294967295) is disallowed
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="invalidParams")


def test_mint_nft_with_no_source_account_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="srcActMissing")


def test_mint_nft_with_no_source_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": "",
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="srcActMalformed")


def test_mint_nft_with_same_account_as_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_mint_nft_with_non_existent_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account()
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ISSUER")


def test_mint_nft_with_issuer_having_unauthorized_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New unauthorized NFTokenMinter account (without 'asfAuthorizedNFTokenMinter' flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_mint_nft_with_issuer_having_authorized_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_on_ticket_with_issuer_having_authorized_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": account_2.account_id,
            "Sequence": rippled_server.get_account_sequence(account_2),
            "TicketCount": 1
        },
        "secret": account_2.master_seed
    }
    ticket_rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
            "TicketSequence": rippled_server.get_ticket_sequence(account_2)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_with_issuer_having_user_authorization_removed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Un-authorize user who had minted
    rpc_response = rippled_server.account_set(account_1, flag=10, clear_flag=True)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_mint_nft_with_issuer_having_authorized_user_and_remove_authorization(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Un-authorize user who had minted
    rpc_response = rippled_server.account_set(account_1, flag=10, clear_flag=True)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_with_issuer_having_authorized_user_changed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    account_3 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_3.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")
    log.info("** As expected, this transaction failed with 'tecNO_PERMISSION' as there is a different authorized NFTokenMinter")

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_3.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])
    log.info("** As expected, this transaction succeeded with the new authorized NFTokenMinter")


def test_mint_nft_with_issuer_having_chain_of_authorized_users(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # account 2 authorizing account 3 to mint for account 1 (issuer)
    account_3 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_2, NFTokenMinter=account_3.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_3.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")


def test_mint_nft_on_ticket(fx_rippled):
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
    ticket_rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_mint_nft_and_delete_account_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    # Not required ti wait for ledger to advance as this is a negative delete testcase
    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    # Delete source account
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")


def test_mint_nft_on_ticket_and_delete_account(fx_rippled):
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
    ticket_rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "TicketSequence": rippled_server.get_ticket_sequence(account_1)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # Not required to wait for ledger to advance as this is a negative delete testcase
    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    # Delete source account
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")


def test_mint_nft_with_issuer_remove_authorization_and_delete_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete issuer after un-authorizing NFTokenMinter
    rpc_response = rippled_server.account_set(account_1, flag=10, clear_flag=True)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Not required ti wait for ledger to advance as this is a negative delete testcase
    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_2),
        },
        "secret": account_2.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")


def test_mint_nft_with_issuer_remove_authorization_and_delete_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete issuer after un-authorizing NFTokenMinter
    rpc_response = rippled_server.account_set(account_1, flag=10, clear_flag=True)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Not required ti wait for ledger to advance as this is a negative delete testcase
    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2],
                               response_result="tecHAS_OBLIGATIONS")


@pytest.mark.smoke
def test_burn_nft_as_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_burn_nft_with_low_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True,
                                              amount=str(
                                                  int(constants.BASE_RESERVE) + 2 * int(constants.OWNER_RESERVE)))

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

    account_2 = rippled_server.create_account(fund=True, amount=constants.BASE_RESERVE)
    # lower balance
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": str(int(rippled_server.get_account_balance(account_1.account_id)) -
                          int(constants.BASE_RESERVE) -
                          int(constants.OWNER_RESERVE))
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_burn_nft_with_NFTokenID_mismatch(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Fee": 10,
            "NFTokenID": "0008000044CAF362635003E9D565979EE87A1668A1FFE7BB2DCBAB9D00000002"
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="tecNO_ENTRY")


def test_burn_nft_as_diff_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ENTRY")


def test_mint_nft_with_issuer_burn_as_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_with_issuer_burn_as_issuer_without_flag_tfBurnable(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_mint_nft_with_issuer_burn_as_issuer_with_flag_tfBurnable(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 1  # tfBurnable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_with_issuer_burn_as_issuer_without_owner_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 1  # tfBurnable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ENTRY")


def test_burn_nft_and_remint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

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


@pytest.mark.longrun
def test_burn_nft_delete_owner_and_remint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    nft_id = rippled_server.get_nft_tokens(account_1.account_id)[-1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # Delete issuer
    account_2 = rippled_server.create_account(fund=True)
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Amount": 20000000,
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 9
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])
    new_nft_id = rippled_server.get_nft_tokens(account_1.account_id)[-1]

    assert nft_id != new_nft_id, "re-minted NFT {} with the same NFTokenID {}".format(nft_id, new_nft_id)


@pytest.mark.longrun
def test_mint_nft_with_issuer_burn_as_owner_and_delete_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete owner
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_2)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_2),
        },
        "secret": account_2.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_burn_nft_as_owner_and_delete_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete issuer
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_burn_nft_as_issuer_and_delete_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 1  # tfBurnable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete owner
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_2),
        },
        "secret": account_2.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


@pytest.mark.longrun
def test_burn_nft_as_issuer_and_delete_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # New authorized NFTokenMinter account (with 'asfAuthorizedNFTokenMinter' (10) flag)
    account_2 = rippled_server.create_account(fund=True)
    rpc_response = rippled_server.account_set(account_1, NFTokenMinter=account_2.account_id, flag=10)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "Issuer": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 1  # tfBurnable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": rippled_server.get_nft_tokens(account_2.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete issuer
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2])


def test_nft_mint_32_plus_nftoken_object(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    max_nftokens = 35
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    for count in range(1, max_nftokens+1):
        log.info("")
        log.info("NFToken Count: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

