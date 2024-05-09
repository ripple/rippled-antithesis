import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()

limit = 51


@pytest.mark.smoke
def test_account_nfts(fx_rippled):
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

    rippled_response = rippled_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts")

    clio_response = clio_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_no_nfts_created(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1])

    clio_response = clio_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account()

    rippled_response = rippled_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="actNotFound")

    clio_response = clio_server.get_account_nfts(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="actNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    rippled_response = rippled_server.get_account_nfts(account_id="rhuEDQ2Q9UeTfu1LBWq7ZzxgrfYV6P5")
    test_validator.verify_test(rippled_server, rippled_response, method="account_nfts", response_result="actMalformed")

    clio_response = clio_server.get_account_nfts(account_id="rhuEDQ2Q9UeTfu1LBWq7ZzxgrfYV6P5")
    test_validator.verify_test(clio_server, clio_response, method="account_nfts", response_result="actMalformed")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        }
    }
    rippled_response = rippled_server.execute_transaction(payload, method="account_nfts")
    test_validator.verify_test(rippled_server, rippled_response, method="account_nfts", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_nfts")
    test_validator.verify_test(clio_server, clio_response, method="account_nfts", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id,
                                                       ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_nfts(account_1.account_id,
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_incorrect_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id,
                                                       ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_nfts(account_1.account_id,
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_min_invalid_ledger_index(fx_rippled):
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

    ledger_index_min = rippled_server.get_ledger_index_min()

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, ledger_index=ledger_index_min - 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_account_nfts(account_1.account_id, ledger_index=ledger_index_min - 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_max_invalid_ledger_index(fx_rippled):
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

    rippled_response = rippled_server.get_account_nfts(account_1.account_id,
                                                       ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_nfts(account_1.account_id,
                                                 ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_zero(fx_rippled):
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

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=0)
    test_validator.verify_test(rippled_server, rippled_response, method="account_nfts", accounts=[account_1])

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    # assert helper.compare_dict(rippled_response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4313


def test_account_nfts_with_limit_as_negative_value(fx_rippled):
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

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=-10)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=-10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_as_non_integer(fx_rippled):
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

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit="10.5")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit="10.5")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_less_than_20(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=15)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1])

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=15)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_greater_than_400(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=410)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1])

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=410)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1])

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_and_marker(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_account_nfts(account_id="ra1egD7jzyZWhcDaPD1eFPKzdSMVQCTsXM")
    test_validator.verify_test(clio_server, clio_response)

    clio_response_1 = clio_server.get_account_nfts(account_id="ra1egD7jzyZWhcDaPD1eFPKzdSMVQCTsXM", limit=20)
    test_validator.verify_test(clio_server, clio_response_1, method="account_nfts")

    clio_response_2 = clio_server.get_account_nfts(account_id="ra1egD7jzyZWhcDaPD1eFPKzdSMVQCTsXM", limit=20,
                                                   marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, method="account_nfts")

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="account_nfts")

    # Not comparing rippled and clio responses as rippled is using limit for limiting account_nfts
    # whereas clio is using limit for limiting pages.


def test_account_nfts_with_limit_and_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=20,
                                                       marker="000000004C17E5B8E33245D98126F4A6DF4EA57FF71C027B6E5D19AB0000001")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=20,
                                                 marker="000000004C17E5B8E33245D98126F4A6DF4EA57FF71C027B6E5D19AB0000001")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_account_nfts_with_limit_and_unassociated_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_response = rippled_server.get_account_nfts(account_1.account_id, limit=20,
                                                       marker="000000004C17E5B8E33245D98126F4A6DF4EA57FF71C027B6E5D19AB0000001")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_nfts(account_1.account_id, limit=20,
                                                 marker="000000004C17E5B8E33245D98126F4A6DF4EA57FF71C027B6E5D19AB0000001")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_nfts",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_no_offer_nft_id(fx_rippled):
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

    rippled_response = rippled_server.get_nft_sell_offers(nft_id=token_id)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="objectNotFound")

    clio_response = clio_server.get_nft_sell_offers(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="objectNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_without_nft_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        },
    }
    rippled_response = rippled_server.execute_transaction(payload, method="nft_sell_offers")
    test_validator.verify_test(rippled_server, rippled_response, method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="nft_sell_offers")
    test_validator.verify_test(clio_server, clio_response, method="nft_sell_offers", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_malformed_nft_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    rippled_response = rippled_server.get_nft_sell_offers(
        nft_id="00080000B99F877D1AA8CD9C4C0110DA670BCB86138D54CF16E5DA9C0000")
    test_validator.verify_test(rippled_server, rippled_response, method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(
        nft_id="00080000B99F877D1AA8CD9C4C0110DA670BCB86138D54CF16E5DA9C0000")
    test_validator.verify_test(clio_server, clio_response, method="nft_sell_offers", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_invalid_ledger_hash(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                          ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                    ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_malformed_ledger_hash(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                          ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                    ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_invalid_min_ledger_index(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    ledger_index_min = rippled_server.get_ledger_index_min()

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                          ledger_index=ledger_index_min - 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                    ledger_index=ledger_index_min - 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_invalid_max_ledger_index(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                          ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                    ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_zero(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=0)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1])

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams")

    # assert (helper.compare_dict(rippled_response, clio_response,
    #                             ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"

    # Rippled issue : https://github.com/XRPLF/rippled/issues/4315


def test_nft_sell_offers_with_limit_negative_value(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=-10)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=-10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_non_integer(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit="10.5")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit="10.5")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_less_than_50(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=10)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers")

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_greater_than_500(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=510)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=510)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers")

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True, amount=str(5 * int(constants.DEFAULT_ACCOUNT_BALANCE)))

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

    for i in range(0, 60):
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

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    rippled_response_1 = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=limit)
    test_validator.verify_test(rippled_server, rippled_response_1, accounts=[account_1], method="nft_sell_offers")

    clio_response_1 = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=limit)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1], method="nft_sell_offers")

    assert helper.compare_dict(rippled_response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    rippled_response_2 = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                            marker=rippled_response_1["marker"])
    test_validator.verify_test(rippled_server, rippled_response_2, accounts=[account_1], method="nft_sell_offers")

    clio_response_2 = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"],
                                                      marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1], method="nft_sell_offers")

    assert (helper.compare_dict(rippled_response_2, clio_response_2,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="offers")


def test_nft_sell_offers_with_limit_and_malformed_marker(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=1,
                                                          marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C63168")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=1,
                                                    marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C63168")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_limit_and_unassociated_marker(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=1,
                                                          marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C631683C")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"], limit=1,
                                                    marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C631683C")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_sell_offers_with_buy_offer_nft_id(fx_rippled):
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

    rippled_response = rippled_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="objectNotFound")

    clio_response = clio_server.get_nft_sell_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_sell_offers",
                               response_result="objectNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_no_offer_nft_id(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(nft_id=token_id)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="objectNotFound")

    clio_response = clio_server.get_nft_buy_offers(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="objectNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_without_nft_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        },
    }
    rippled_response = rippled_server.execute_transaction(payload, method="nft_buy_offers")
    test_validator.verify_test(rippled_server, rippled_response, method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="nft_buy_offers")
    test_validator.verify_test(clio_server, clio_response, method="nft_buy_offers", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_malformed_nft_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    rippled_response = rippled_server.get_nft_buy_offers(nft_id="dsfghj")
    test_validator.verify_test(rippled_server, rippled_response, method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(nft_id="dsfghj")
    test_validator.verify_test(clio_server, clio_response, method="nft_buy_offers", response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_invalid_ledger_hash(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                         ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_malformed_ledger_hash(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                         ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB1827")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB1827")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_invalid_min_ledger_index(fx_rippled):
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

    ledger_index_min = rippled_server.get_ledger_index_min()

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                         ledger_index=ledger_index_min - 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    ledger_index_min = clio_server.get_ledger_index_min()

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                   ledger_index=ledger_index_min - 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_invalid_max_ledger_index(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                         ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                   ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="lgrNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_zero(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=0)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1])

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], response_result="invalidParams")

    # assert (helper.compare_dict(rippled_response, clio_response,
    #                             ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"

    # Rippled issue : https://github.com/XRPLF/rippled/issues/4315


def test_nft_buy_offers_with_limit_negative_value(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=-10)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=-10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_non_integer(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit="10.5")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit="10.5")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_less_than_50(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=10)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=10)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers")

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_greater_than_500(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=510)
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=510)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers")

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_and_marker(fx_rippled):
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
    account_2 = rippled_server.create_account(fund=True, amount=str(5 * int(constants.DEFAULT_ACCOUNT_BALANCE)))

    for i in range(0, 60):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    rippled_response_1 = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=51)
    test_validator.verify_test(rippled_server, rippled_response_1, accounts=[account_1], method="nft_buy_offers")

    clio_response_1 = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=51)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1], method="nft_buy_offers")

    assert helper.compare_dict(rippled_response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    rippled_response_2 = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                           marker=rippled_response_1["marker"])
    test_validator.verify_test(rippled_server, rippled_response_2, accounts=[account_1], method="nft_buy_offers")

    clio_response_2 = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"],
                                                     marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1], method="nft_buy_offers")

    assert helper.compare_dict(rippled_response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="offers")


def test_nft_buy_offers_with_limit_and_malformed_marker(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=50,
                                                         marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C63168")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=50,
                                                   marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C63168")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    assert (helper.compare_dict(rippled_response, clio_response,
                                ignore=constants.CLIO_IGNORES)), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_limit_and_unassociated_marker(fx_rippled):
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

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=50,
                                                         marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C631683C")
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"], limit=50,
                                                   marker="5D71D16859E0C01A0D6BB5BCA19EDCA0F487E59FCFE5DCEA617CF899C631683C")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="invalidParams")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_buy_offers_with_sell_offer_nft_id(fx_rippled):
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
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1])

    rippled_response = rippled_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="objectNotFound")

    clio_response = clio_server.get_nft_buy_offers(rpc_response["tx_json"]["NFTokenID"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_buy_offers",
                               response_result="objectNotFound")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "Mismatch in rippled and clio response"


def test_nft_info(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")


def test_nft_info_with_ledger_index_current(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id, ledger_index="current")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="invalidParams")


def test_nft_info_with_ledger_index_closed(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id, ledger_index="closed")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="invalidParams")


def test_nft_info_with_no_nft_id(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nft_info")
    test_validator.verify_test(clio_server, clio_response, method="nft_info", response_result="invalidParams")


def test_nft_info_with_invalid_nft_id(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_nft_info(nft_id="00080000B4F4AFC5FBCBD76873F18006173D2193467D3EE70000099B00000000")
    test_validator.verify_test(clio_server, clio_response, method="nft_info", response_result="objectNotFound")


def test_nft_info_with_malformed_nft_id(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_nft_info(nft_id="00000000B99F877D1AA8CD9C4C0110DA670BCB86138D54CF0000099B000000")
    test_validator.verify_test(clio_server, clio_response, method="nft_info", response_result="invalidParams")


def test_nft_info_with_invalid_ledger_hash(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id,
                                             ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="lgrNotFound")


def test_nft_info_with_incorrect_ledger_hash(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id,
                                             ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="invalidParams")


def test_nft_info_with_min_invalid_ledger_index(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id, ledger_index=ledger_index_min - 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="lgrNotFound")


def test_nft_info_with_max_invalid_ledger_index(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id, ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info",
                               response_result="lgrNotFound")


def test_nft_info_without_uri_in_NFTokenMint(fx_rippled):
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

    clio_response = clio_server.get_nft_info(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")

    assert not clio_response["uri"], "uri is not an empty string: {}".format(clio_response)


def test_nft_info_with_uri_in_NFTokenMint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    token_id = rippled_server.get_nft_tokens(account_1.account_id)[0]

    clio_response = clio_server.get_nft_info(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")

    assert clio_response["uri"], "uri is an empty string: {}".format(clio_response)


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1021")
def test_nft_info_with_uri_in_NFTokenMint_and_NFTokenBurn(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    clio_response = clio_server.get_nft_info(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")

    assert not clio_response["uri"], "uri is not an empty string: {}".format(clio_response)


@pytest.mark.skip("https://github.com/XRPLF/clio/issues/1021")
def test_nft_info_retrieve_uri_with_burned_NFT(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    ledger_index = rippled_server.tx(tx_id=rpc_response["tx_json"]["hash"])["ledger_index"]

    clio_response = clio_server.get_nft_info(nft_id=token_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")

    assert not clio_response["uri"], "uri is not an empty string: {}".format(clio_response)

    clio_response = clio_server.get_nft_info(nft_id=token_id, ledger_index=ledger_index - 1)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="nft_info")

    assert clio_response["uri"], "uri is an empty string: {}".format(clio_response)
