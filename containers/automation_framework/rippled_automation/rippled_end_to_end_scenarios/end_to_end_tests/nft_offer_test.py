#!/usr/bin/env python
import os
import py_compile
import time

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


@pytest.mark.smoke
def test_create_nft_buy_offer_and_accept_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_buy_offer_with_disallow_incoming_flag_before_mint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    rippled_server.account_set(account_1, flag=constants.FLAGS_NFT_asfDisallowIncomingNFTOffer)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_nft_buy_offer_with_disallow_incoming_flag_after_mint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_server.account_set(account_1, constants.FLAGS_NFT_asfDisallowIncomingNFTOffer)

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_nft_buy_offer_and_accept_offer_with_low_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=str(
        int(constants.BASE_RESERVE) + 2 * int(constants.OWNER_RESERVE)))

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # lower balance before accepting offer
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": str(int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) -
                          int(constants.BASE_RESERVE) -
                          int(constants.OWNER_RESERVE))
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_buy_offer_with_flags_0(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 0  # Is 0=buy offer?
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_buy_offer_with_invalid_flags(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 2
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temINVALID_FLAG")


def test_create_nft_buy_offer_without_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            # "Owner": account_1.account_id,  # No owner
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_create_nft_buy_offer_with_owner_same_as_NFTokenMinter(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_2.account_id,  # Owner same as NFTokenMinter
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_create_nft_buy_offer_with_tfSellToken_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # Buy offer with flag 1 should error
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_create_nft_buy_offer_accept_offer_after_expiration(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION)
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecEXPIRED")


def test_create_nft_buy_offer_accept_offer_before_expiration(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION)
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_BEFORE,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_sell_nft_offer_and_accept_before_expiration(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION),
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_BEFORE,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_sell_nft_offer_and_accept_after_expiration(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION),
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecEXPIRED")


def test_create_nft_sell_offer_accept_an_accepted_offer_with_same_token_id(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)
    token_offer = rippled_server.get_token_offers(account_1, token_id=token_id)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": token_offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])

    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecOBJECT_NOT_FOUND")


def test_create_nft_buy_offer_accept_an_accepted_offer_with_same_token_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecOBJECT_NOT_FOUND")


def test_create_multiple_nft_buy_offers_accept_one_by_one_different_token(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    for count in range(1, max_nft_tokens + 1):
        log.info("")
        log.info("NFToken Count: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        token_id = rippled_server.get_nft_tokens(account_1.account_id)[count-1]
        log.info("Using Token ID: ".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Accept Offer Count: {}".format(count))

        token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenAcceptOffer",
                "Account": account_1.account_id,
                "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            },
            "secret": account_1.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_buy_offer_with_non_mint_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)  # non-mint owner

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_3.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ENTRY")


def test_create_nft_buy_offer_without_transferable_flag_and_accept_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            # "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tefNFTOKEN_IS_NOT_TRANSFERABLE")


def test_create_nft_buy_offer_without_owner_and_accept_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            # "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


@pytest.mark.smoke
def test_create_nft_sell_offer_and_accept_offer(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_sell_offer_and_accept_offer_with_low_reserve(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer, but with low reserve
    account_2 = rippled_server.create_account(fund=True, amount=str(
        int(constants.BASE_RESERVE) + int(constants.DEFAULT_TRANSFER_AMOUNT)))

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecINSUFFICIENT_RESERVE")


def test_create_nft_sell_offer_with_disallow_incoming_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.account_set(account_2, constants.FLAGS_NFT_asfDisallowIncomingNFTOffer)

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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_nft_sell_offer_without_tfSellToken_flag(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_create_sell_offer_as_non_NFTokenMinter(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="tecNO_ENTRY")


def test_create_sell_offer_as_non_NFTokenMinter_mentioning_owner(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    account_2 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_create_nft_sell_offer_and_accept_offer_with_no_NFTokenSellOffer_field(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_create_nft_sell_offer_and_accept_offer_with_NFTokenBuyOffer_field(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNFTOKEN_OFFER_TYPE_MISMATCH")


def test_create_nft_buy_offer_and_accept_offer_with_no_NFTokenBuyOffer_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_create_nft_buy_offer_and_accept_offer_with_NFTokenSellOffer_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNFTOKEN_OFFER_TYPE_MISMATCH")


def test_create_nft_sell_offer_and_accept_offer_by_self(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1],
                               response_result="tecNFTOKEN_OFFER_TYPE_MISMATCH")


def test_create_nft_sell_offer_with_owner_field(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_create_nft_sell_offer_cancel_with_token_id(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
                token_id  # should be ledger index; so should not cancel offer/remove object
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], ignore_account_objects=True)


def test_create_sell_offer_and_burn(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_create_sell_offer_cancel_offer_and_burn(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_1, token_id=token_id)[0]
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_create_sell_offer_after_burn(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="tecNO_ENTRY")


def test_accept_nft_buy_offer_burn_by_issuer_with_burnable_but_no_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 9  # tfTransferable & burnable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="tecNO_ENTRY")


def test_accept_nft_buy_offer_burn_by_issuer_with_burnable_with_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 9  # tfTransferable & burnable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_accept_nft_buy_offer_burn_by_buyer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": token_id
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_accept_sell_offer_and_burn_by_issuer(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ENTRY")


def test_accept_sell_offer_and_burn_by_buyer(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": token_id
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_cancel_nft_buy_offer_by_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION)
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_cancel_nft_buy_offer_with_duplicate_token_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_offer = rippled_server.get_token_offers(account_2, token_id=token_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                token_offer,
                token_offer
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_cancel_nft_with_empty_token_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temMALFORMED")


def test_cancel_nft_with_existing_object_but_not_token_offer(fx_rippled):
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

    check_id = rippled_server.get_check_ids(account_1)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
                check_id
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_cancel_nft_buy_offer_with_check_id_and_token_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])
    check_id = rippled_server.get_check_ids(account_1)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_offer = rippled_server.get_token_offers(account_2, token_id=token_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                check_id,
                token_offer,
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_nft_sell_offer_and_cancel(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_1, token_id=token_id)[0]
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_cancel_nft_sell_offer_by_3rd_party(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # Create a new account to cancel offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_1, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_cancel_nft_buy_offer_by_3rd_party(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to create NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # 3rd party to cancel NFT offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_3.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")


def test_cancel_nft_buy_offer_after_offer_expiration_by_3rd_party(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to create NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION)
            # "Flags": 1  # buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # 3rd party to cancel NFT offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_3.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_cancel_nft_buy_offer_after_offer_expiration_by_owner(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to create NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION)
            # "Flags": 1  # buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_sell_nft_offer_and_accept_by_destination_account(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])


def test_create_sell_nft_offer_and_accept_by_non_destination_account(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # non-destination account
    account_3 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")


def test_create_sell_nft_offer_and_accept_by_destination_account_after_expiration(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_NFTOKEN_EXPIRATION),
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload,
                                                      execution_time=constants.EXECUTE_TRANSACTION_AFTER,
                                                      create_response=rpc_response)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecEXPIRED")


def test_create_buy_nft_offer_and_accept_by_destination_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to create NFT offer
    account_2 = rippled_server.create_account(fund=True)
    # destination account for a buy offer - should succeed with amendment "fixNonFungibleTokensV1_2" enabled
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "Destination": account_3.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_buy_nft_offer_destination_account_as_seller(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "Destination": account_1.account_id,  # seller as destination
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_sell_nft_offer_and_accept_by_destination_account_as_self(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temMALFORMED")


def test_cancel_offer_by_destination_account(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_1, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_offer_with_destination_cancel_by_3rd_party(fx_rippled):
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
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # cancel as a non-destination account
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_3.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_1, token_id=token_id)[0]
            ]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")


def test_create_2_nft_buy_offers_cancel_one_accept_one_for_same_token(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    log.info("token_id: {}".format(token_id))
    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        log.info("Using Token ID: {}".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]  # other offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_2_nft_buy_offers_cancel_one_accept_one_for_different_tokens(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    for count in range(1, max_nft_tokens + 1):
        log.info("")
        log.info("NFToken Count: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        token_id = rippled_server.get_nft_tokens(account_1.account_id)[count-1]
        log.info("Using Token ID: {}".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_2_nft_buy_offers_with_different_tokens_accept_both(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    for count in range(1, max_nft_tokens + 1):
        log.info("")
        log.info("NFToken Count: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        token_id = rippled_server.get_nft_tokens(account_1.account_id)[count-1]
        log.info("Using Token ID: {}".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # token_id = rippled_server.get_nft_tokens(account_1.account_id)[1]
    token_offers = rippled_server.get_token_offers(account_2)

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Accept Offer Count: {}".format(count))

        payload = {
            "tx_json": {
                "TransactionType": "NFTokenAcceptOffer",
                "Account": account_1.account_id,
                "NFTokenBuyOffer": token_offers[count-1]
            },
            "secret": account_1.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_2_nft_buy_offers_for_same_token_cancel_all(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    log.info("token_id: {}".format(token_id))
    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        log.info("Using Token ID: {}".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_offers = rippled_server.get_token_offers(account_2)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": token_offers
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_cancel_nft_buy_offer_and_accept_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_offer = rippled_server.get_token_offers(account_2, token_id=token_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                token_offer
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": token_offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecOBJECT_NOT_FOUND")


def test_mint_nft_with_issuer_create_offer_as_owner_cancel_as_owner(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[-1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_mint_nft_with_issuer_create_sell_offer_as_owner_accept(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[-1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # account to accept NFT sell offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_mint_nft_with_issuer_create_offer_as_owner_cancel_as_issuer(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[-1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_1.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_mint_nft_with_issuer_create_offer_as_issuer_cancel_as_issuer(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[-1]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecNO_ENTRY")


def test_cancel_a_cancelled_nft_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    log.info("")
    log.info("Cancel a cancelled offer")
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], ignore_account_objects=True)


def test_cancel_mix_of_valid_and_cancelled_nft_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    max_nft_tokens = max_offers = 2

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    for count in range(1, max_nft_tokens + 1):
        log.info("")
        log.info("NFToken Count: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    for count in range(1, max_offers + 1):
        log.info("")
        log.info("NFT Create Offer Count: {}".format(count))

        token_id = rippled_server.get_nft_tokens(account_1.account_id)[count-1]
        log.info("Using Token ID: {}".format(token_id))
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenCreateOffer",
                "Account": account_2.account_id,
                "Owner": account_1.account_id,
                "NFTokenID": token_id,
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                # "Flags": 1  # sell offer
            },
            "secret": account_2.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    token_offers = rippled_server.get_token_offers(account_2)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                token_offers[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": token_offers
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])


def test_cancel_nft_buy_offer_create_offer_with_for_same_token(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCancelOffer",
            "Account": account_2.account_id,
            "NFTokenOffers": [
                rippled_server.get_token_offers(account_2, token_id=token_id)[0]
            ]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_accept_nft_buy_offer_and_delete_by_issuer_without_burning(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Delete issuer
    account_3 = rippled_server.create_account(fund=True)
    # rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2, account_3],
                               response_result="tecHAS_OBLIGATIONS")


@pytest.mark.longrun
def test_accept_nft_buy_offer_burn_token_delete_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_2.account_id,
            "NFTokenID": token_id
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # Delete issuer
    account_3 = rippled_server.create_account(fund=True)
    rippled_server.wait_for_ledger_to_advance_for_account_delete(account_1)

    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(account_1),
        },
        "secret": account_1.master_seed
    }
    delete_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, delete_response, accounts=[account_1, account_2, account_3])


def test_create_nft_buy_offer_with_iou(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)
    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_sell_offer_with_iou(fx_rippled):
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

    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)
    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_sell_offer_and_accept_offer_with_deposit_auth_enabled(fx_rippled):
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

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_1)

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_create_nft_buy_offer_and_accept_offer_with_deposit_auth_enabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_1)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])


def test_alice_bob_ben_transfer_nft(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    token_id = rippled_server.get_nft_tokens(alice.account_id)[0]

    # account to accept NFT offer
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "Owner": alice.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": alice.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(bob, token_id=token_id)[0]
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    token_id = rippled_server.get_nft_tokens(bob.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[bob])

    # account to accept NFT sell offer
    ben = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": ben.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(bob, token_id=token_id)[0]
        },
        "secret": ben.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob, ben])


def test_nftoken_alice_bob_back_to_alice(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    # account to accept NFT offer
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    token_id = rippled_server.get_nft_tokens(alice.account_id)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "Owner": alice.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": alice.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(bob, token_id=token_id)[0]
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    token_id = rippled_server.get_nft_tokens(bob.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": alice.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(bob, token_id=token_id)[0]
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])


def test_nft_offer_accept_broker_mode_seller_first(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_nft_offer_accept_broker_mode_buyer_first(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_nft_transfer_offer_accept_broker_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT buyer offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_3.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])

    # broker deal
    account_4 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_4.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_3, token_id=token_id)[0]
        },
        "secret": account_4.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3, account_4])


def test_nft_offer_accept_broker_mode_without_buyer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # No NFT buyer offer

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_3],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_without_seller(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # No NFT seller offer

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_3],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_as_buyer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal (buyer as broker)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_as_seller(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal (seller as broker)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_as_NFTokenMinter(fx_rippled):
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
            "Flags": 8  # tfTransferable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT buyer offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_3.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])

    # broker deal (NFTokenMiner as broker)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_3, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_as_issuer(fx_rippled):
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
            "Flags": 8  # tfTransferable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT buyer offer
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_3.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])

    # broker deal (issuer as broker)
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_3, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_nft_broker_settling_for_same_buyer_and_seller(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    token_id = rippled_server.get_nft_tokens(alice.account_id)[0]

    # NFT buyer offer
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "Owner": alice.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": alice.account_id,
            "NFTokenID": token_id,
            "Amount": 0,  # gifting it to buyer
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": bob.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(alice, token_id=token_id)[0]
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob])

    # Now bob creates a sell offer that he has the free NFT from alice
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": bob.account_id,
            "NFTokenID": token_id,
            "Amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT)+100),
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": bob.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[bob])

    # broker deal
    broker = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": broker.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(bob, token_id=token_id, offer_type=1)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(bob, token_id=token_id, offer_type=0)[0]
        },
        "secret": broker.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice, bob, broker],
                               response_result="tecCANT_ACCEPT_OWN_NFTOKEN_OFFER")


def test_nft_offer_accept_broker_mode_with_zero_broker_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)
    broker_fee = 0
    buy_amount = int(constants.DEFAULT_TRANSFER_AMOUNT) + broker_fee

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(buy_amount),
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBrokerFee": int(broker_fee)
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="temMALFORMED")


def test_nft_offer_accept_broker_mode_with_negative_broker_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)
    broker_fee = -10
    buy_amount = int(constants.DEFAULT_TRANSFER_AMOUNT) + broker_fee

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(buy_amount),
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBrokerFee": int(broker_fee)
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="temMALFORMED")


def test_nft_offer_accept_broker_mode_with_valid_broker_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)
    broker_fee = 100
    buy_amount = int(constants.DEFAULT_TRANSFER_AMOUNT) + broker_fee

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(buy_amount),
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBrokerFee": broker_fee
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_nft_offer_accept_broker_mode_deposit_set_on_broker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)
    broker_fee = 100
    buy_amount = int(constants.DEFAULT_TRANSFER_AMOUNT) + broker_fee

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(buy_amount),
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)
    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_3)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0],
            "NFTokenBrokerFee": broker_fee
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_create_sell_nft_offer_buyer_as_destination_and_broker_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,  # buyer as destination
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT buyer offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])


def test_create_buy_nft_offer_seller_as_destination_and_broker_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "Destination": account_1.account_id,  # seller as destination
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3],
                               response_result="tecNO_PERMISSION")

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_1.account_id,
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1,account_2])


def test_create_sell_nft_offer_broker_as_destination_settle_broker_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)  # broker

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,  # broker as destination
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT buyer offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_create_buy_nft_offer_broker_as_destination_settle_broker_mode(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)  # broker

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "Destination": account_3.account_id,  # broker as destination
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


def test_create_nft_buy_offer_with_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": -100,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_nft_buy_offer_with_zero_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": 0,
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")  # No to "I'll take that NFT off your hands for free."


def test_create_nft_sell_offer_with_negative_amount(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": -100,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1], response_result="temBAD_AMOUNT")


def test_create_nft_sell_offer_with_zero_amount(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": 0,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_2.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0]
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response,
                               accounts=[account_1, account_2])  # "I'm giving this NFT away"


def test_create_nft_buy_offer_with_zero_iou(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)
    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": 0,
                "issuer": issuer.account_id
            },
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_nft_buy_offer_with_negative_iou(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    # account to accept NFT offer
    account_2 = rippled_server.create_account(fund=True)
    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": -10,
                "issuer": issuer.account_id
            },
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_nft_sell_offer_with_zero_iou(fx_rippled):
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

    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)
    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": 0,
                "issuer": issuer.account_id
            },
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_nft_sell_offer_with_negative_iou(fx_rippled):
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

    # Create a trustline to support IOU
    issuer = rippled_server.create_account(fund=True)
    # account to accept NFT sell offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": {
                "currency": "USD",
                "value": -10,
                "issuer": issuer.account_id
            },
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_nft_offer_accept_broker_mode_seller_first_broker_low_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    broker_balance = int(int(constants.DEFAULT_ACCOUNT_BALANCE)/2)
    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=constants.DEFAULT_ACCOUNT_BALANCE)

    # NFT seller offer
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(broker_balance + 1),  # more than broker balance
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    # NFT buyer offer
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_2.account_id,
            "Owner": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": str(broker_balance + 1),  # more than broker balance
            # "Flags": 1  # sell offer
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    # broker deal
    account_3 = rippled_server.create_account(fund=True, amount=str(broker_balance))

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenAcceptOffer",
            "Account": account_3.account_id,
            "NFTokenSellOffer": rippled_server.get_token_offers(account_1, token_id=token_id)[0],
            "NFTokenBuyOffer": rippled_server.get_token_offers(account_2, token_id=token_id)[0]
        },
        "secret": account_3.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2, account_3])


@pytest.mark.skip("Too long to run this test - run manually when required")
@pytest.mark.longrun
def test_create_500_plus_offers_and_burn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    amount_to_fund = str(550 * (int(constants.DEFAULT_TRANSFER_AMOUNT) + int(constants.OWNER_RESERVE)) +
                         int(constants.BASE_RESERVE))
    account_1 = rippled_server.create_account(fund=True, amount=amount_to_fund)

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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1
        },
        "secret": account_1.master_seed
    }
    for count in range(1, 502):
        log.info("NFT Offer: {}".format(count))
        rpc_response = rippled_server.execute_transaction(payload=payload, verbose=False)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenBurn",
            "Account": account_1.account_id,
            "NFTokenID": token_id
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

