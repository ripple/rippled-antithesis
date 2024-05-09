from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_nft_history_with_NFTokenMint(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_with_api_version_2(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx_json"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenBurn(fx_rippled):
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

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenBurn", "nft history for NFTokenBurn not found: {}".format(clio_response)

    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenCreateOffer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenCreateOffer_NFTokenAcceptOffer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenAcceptOffer", "nft history for NFTokenAcceptOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][2]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenCreateOffer_NFTokenCancelOffer(fx_rippled):
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

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenCancelOffer", "nft history for NFTokenCancelOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][2]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenCreateOffer_NFTokenBurn(fx_rippled):
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
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenBurn", "nft history for NFTokenBurn not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][2]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_NFTokenMint_NFTokenCreateOffer_NFTokenCancelOffer_NFTokenBurn(fx_rippled):
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
            "NFTokenID": rippled_server.get_nft_tokens(account_1.account_id)[-1]
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    clio_response = clio_server.get_nft_history(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenBurn", "nft history for NFTokenBurn not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenCancelOffer", "nft history for NFTokenCancelOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][2]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][3]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_malformed_nft_id(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_nft_history(
        nft_id="000000000D330DB99CACE42106DB5672EE36488396CAD6A50000099B0000000")
    test_validator.verify_test(clio_server, clio_response, method="nft_history", response_result="invalidParams")


def test_nft_history_with_nft_id_out_of_ledger_range(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_nft_history(
        nft_id="00080000B4F4AFC5FBCBD76873F18006173D2193467D3EE70000099B00000000")
    test_validator.verify_test(clio_server, clio_response, method="nft_history")

    assert not clio_response["transactions"], "transactions found: {}".format(clio_response)


def test_nft_history_without_nft_id(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }

    clio_response = clio_server.execute_transaction(payload, method="nft_history")
    test_validator.verify_test(clio_server, clio_response, method="nft_history", response_result="invalidParams")


def test_nft_history_with_ledger_index_min_1(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_min=-1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_min_lower_than_min_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_min=ledger_index_min - 10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrIdxMalformed")


def test_nft_history_with_ledger_index_min_greater_than_max_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_min=rippled_server.ledger_current() + 10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrIdxMalformed")


def test_nft_history_with_ledger_index_min_as_string(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_min="28495092")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_min_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_min=2849509.2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_max_as_1(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=-1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_max_lower_than_min_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=ledger_index_min - 10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrIdxMalformed")


def test_nft_history_with_ledger_index_max_greater_than_max_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=rippled_server.ledger_current() + 10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrIdxMalformed")


def test_nft_history_with_ledger_index_max_as_string(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max="21377174")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_max_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=2137717.4)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_max_and_ledger_index_min(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index_max = rippled_server.ledger_current() - 10
    ledger_index_min = ledger_index_max - 100

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=ledger_index_max,
                                                ledger_index_min=ledger_index_min)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_max_lower_than_ledger_index_min(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index_min = clio_server.ledger_current() - 10
    ledger_index_max = ledger_index_min - 10

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index_max=ledger_index_max,
                                                ledger_index_min=ledger_index_min)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrIdxsInvalid")


def test_nft_history_with_valid_ledger_hash(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=rpc_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_invalid_ledger_hash(fx_rippled):
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

    tx_response = rippled_server.tx(tx_id=response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_1.account_id,
            "NFTokenTaxon": 0
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_hash=clio_response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="nft_history")


def test_nft_history_with_malformed_ledger_hash(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id,
                                                ledger_hash="BB19D26AFFA27156B095D6FF6414C5AEC8633B54224F877990E62C7B5F69C33")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_valid_ledger_index(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id,
                                                ledger_index=rpc_response["tx_json"]["Sequence"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_lower_than_min_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index = clio_server.get_ledger_index_min() - 10

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrNotFound")


def test_nft_history_with_ledger_index_greater_than_max_range(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index=clio_server.ledger_current() + 10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="lgrNotFound")


def test_nft_history_with_ledger_index_as_string(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index = rippled_server.ledger_current() - 10

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index=str(ledger_index))
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index=2849787.1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_ledger_index_min_ledger_index_max(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    ledger_index_max = clio_server.ledger_current() - 10
    ledger_index = ledger_index_max - 10
    ledger_index_min = ledger_index - 10

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index=ledger_index,
                                                ledger_index_min=ledger_index_min, ledger_index_max=ledger_index_max)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_as_validated(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_ledger_index_as_current(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index="current")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_ledger_index_as_closed(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, ledger_index="closed")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_binary_true(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, binary=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx_blob"], "binary format not found: {}".format(clio_response)


def test_nft_history_with_binary_true_and_api_version_2(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, binary=True, api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][0]["tx_blob"], "binary format not found: {}".format(clio_response)


def test_nft_history_with_binary_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, binary="ghj")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_forward_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id, forward=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert clio_response["transactions"][2]["tx"][
               "TransactionType"] == "NFTokenAcceptOffer", "nft history for NFTokenAcceptOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][1]["tx"][
               "TransactionType"] == "NFTokenCreateOffer", "nft history for NFTokenCreateOffer not found: {}".format(
        clio_response)
    assert clio_response["transactions"][0]["tx"][
               "TransactionType"] == "NFTokenMint", "nft history for NFTokenMint not found: {}".format(clio_response)


def test_nft_history_with_forward_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, forward="ghj")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    assert len(clio_response["transactions"]) == 1, "limit not followed: {}".format(clio_response)


def test_nft_history_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")

    clio_response = clio_server.get_nft_history(nft_id=token_id, marker=clio_response["marker"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_limit_zero(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_limit_as_malformed_value(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_limit_greater_than_100(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=101)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history")


def test_nft_history_with_limit_and_unassociated_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="nft_history")

    clio_response = clio_server.get_nft_history(nft_id=token_id, marker={
        "ledger": clio_server.ledger_current() - 50,
        "seq": 0
    })
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="nft_history")

    assert not clio_response["transactions"], "transactions found: {}".format(clio_response)


def test_nft_history_with_limit_and_malformed_ledger_in_marker(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=1, marker={
        "ledger": "28494826",
        "seq": 0
    })
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")


def test_nft_history_with_limit_and_malformed_sequence_in_marker(fx_rippled):
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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_history(nft_id=token_id, limit=1, marker={
        "ledger": clio_server.ledger_current() - 10,
        "seq": "10"
    })
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_history",
                               response_result="invalidParams")

