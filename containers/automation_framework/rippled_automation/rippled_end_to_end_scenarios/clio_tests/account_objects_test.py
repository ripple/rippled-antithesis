import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.price_oracle import price_oracle_test_data as test_data
from ..utils import log_helper, helper
from ..utils import test_validator
from ..utils.amm.amm_helper import setup_env

log = log_helper.get_logger()


def test_account_objects_offer(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="offer")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "Offer", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="offer")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "Offer", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_ripplestate(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="state")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "RippleState", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="state")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "RippleState", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_signerlist(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    assert response["account_objects"][0]["LedgerEntryType"] == "SignerList", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="signer_list")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "SignerList", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_escrow(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="escrow")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "Escrow", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="escrow")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "Escrow", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_paychannel(fx_rippled):
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
            "SettleDelay": 80,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="payment_channel")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "PayChannel", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="payment_channel")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "PayChannel", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_check(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="check")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "Check", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="check")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "Check", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_deposit_preauth(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    # Set deposit auth
    account_2 = rippled_server.create_account(fund=True)
    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.deposit_preauthorize(account_object=account_1, third_party_account=account_2)

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="deposit_preauth")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "DepositPreauth", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="deposit_preauth")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "DepositPreauth", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_ticket(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="ticket")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "Ticket", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="ticket")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "Ticket", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_nft_sell_offer(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="nft_offer")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "NFTokenOffer", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="nft_offer")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "NFTokenOffer", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_nft_buy_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": account_2.account_id,
            "NFTokenTaxon": 0,
            "Flags": 8  # tfTransferable
        },
        "secret": account_2.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    token_id = rippled_server.get_nft_tokens(account_2.account_id)[0]

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": account_1.account_id,
            "Owner": account_2.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="nft_offer")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "NFTokenOffer", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="nft_offer")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "NFTokenOffer", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_nft_page(fx_rippled):
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

    response = rippled_server.get_account_objects(account_1.account_id, ledger_object_type="nft_page")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "NFTokenPage", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(account_1.account_id, ledger_object_type="nft_page")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "NFTokenPage", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_AMMBid(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, asset_1, asset_2)
    asset_1 = constants.XRP_ASSET
    lp_token = rippled_server.get_amm_lp_token(asset_1, asset_2)

    rippled_server.create_trustline(alice, lp_token)

    payment = dict(lp_token, value=constants.DEFAULT_AMM_TOKEN_TRANSFER)
    rippled_server.make_payment(gw, alice, payment)

    bid_response = rippled_server.amm_bid(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, bid_response)

    amm_account = rippled_server.get_amm_id(asset_1, asset_2)

    response = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(rippled_server, response, accounts=[gw, alice], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(clio_server, clio_response, accounts=[gw, alice], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_AMMCreate(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.DEFAULT_AMM_XRP_CREATE
    asset_2 = {"currency": "USD", "issuer": alice.account_id, "value": constants.DEFAULT_AMM_TOKEN_CREATE}

    amm_create_response = rippled_server.amm_create(alice, asset_1, asset_2)
    test_validator.verify_test(rippled_server, amm_create_response, accounts=[alice])

    amm_account = rippled_server.get_amm_id(asset_1, asset_2)

    response = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("https://ripplelabs.atlassian.net/browse/RIP-930")
def test_account_objects_AMMDelete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    xrp_asset = constants.XRP_ASSET
    usd_asset = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }
    rippled_server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, usd_asset)

    amm_account = rippled_server.get_amm_id(constants.DEFAULT_AMM_XRP_CREATE, usd_asset)

    currency = rippled_server.get_amm_lp_token(xrp_asset, usd_asset)
    trustline_limit = dict(currency, value="10000000")

    setup_env(rippled_server, number_of_accounts=520, currency=currency, trustline_limit=trustline_limit)

    rippled_server.withdraw_all(gw, xrp_asset, usd_asset)

    amm_delete_txn = {
        "tx_json": {
            "TransactionType": "AMMDelete",
            "Account": alice.account_id,
            "Asset": xrp_asset,
            "Asset2": usd_asset,
        },
    }

    amm_delete_response = rippled_server.execute_transaction(payload=amm_delete_txn, secret=alice.master_seed)
    test_validator.verify_test(rippled_server, amm_delete_response)

    response = rippled_server.get_account_objects(amm_account)
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_objects",
                               response_result="actNotFound")

    clio_response = clio_server.get_account_objects(amm_account)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_objects",
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_AMMDeposit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, constants.DEFAULT_AMM_XRP_CREATE, asset_2)

    xrp_amount = constants.DEFAULT_AMM_XRP_DEPOSIT

    deposit_response = rippled_server.amm_deposit(alice, asset_1, asset_2, xrp_amount)
    test_validator.verify_test(rippled_server, deposit_response)

    amm_account = rippled_server.get_amm_id(asset_1, asset_2)

    response = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(rippled_server, response, method="account_objects")

    # TODO: Add account balance validation to verify_test after it was implemented.

    assert response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(clio_server, clio_response, method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_AMMVote(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    gw = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": gw.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(gw, xrp, usd)
    rippled_server.amm_deposit(alice, asset_1=constants.XRP_ASSET, asset_2=usd,
                               amount=constants.DEFAULT_AMM_XRP_DEPOSIT, )

    response = rippled_server.amm_vote(alice, constants.XRP_ASSET, usd)
    test_validator.verify_test(rippled_server, response)

    amm_account = rippled_server.get_amm_id(xrp, usd)

    response = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(rippled_server, response, method="account_objects")

    # TODO: Add account balance validation to verify_test after it was implemented.

    assert response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(clio_server, clio_response, method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_AMMWithdraw(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    asset_1 = constants.XRP_ASSET
    asset_2 = {
        "currency": "USD",
        "issuer": alice.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    rippled_server.amm_create(alice, constants.DEFAULT_AMM_XRP_CREATE, asset_2)
    amount = constants.DEFAULT_AMM_XRP_WITHDRAWAL

    withdraw_response = rippled_server.amm_withdraw(alice, asset_1, asset_2, amount, mode="tfSingleAsset")
    test_validator.verify_test(rippled_server, withdraw_response)

    amm_account = rippled_server.get_amm_id(asset_1, asset_2)

    response = rippled_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(rippled_server, response, method="account_objects")

    # TODO: Add account balance validation to verify_test after it was implemented.

    assert response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(amm_account, ledger_object_type="amm")
    test_validator.verify_test(clio_server, clio_response, method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "AMM", "type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("Amendment not enabled")
def test_account_objects_DIDSet_txn(fx_rippled):
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

    response = rippled_server.get_account_objects(alice.account_id, ledger_object_type="DIDSet")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_objects")

    assert response["transactions"][0]["tx"]["TransactionType"] == "DIDSet", "Transaction type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(alice.account_id, ledger_object_type="DIDSet")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_objects")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "DIDSet", "Transaction type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("Amendment not enabled")
def test_account_objects_with_DIDDelete_txn(fx_rippled):
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

    response = rippled_server.get_account_objects(alice.account_id, ledger_object_type="DIDDelete")
    test_validator.verify_test(rippled_server, response, accounts=[alice, alice], method="account_objects")

    assert response["transactions"][0]["tx"]["TransactionType"] == "DIDDelete", "Transaction type mismatch: {}".format(
        response)

    clio_response = clio_server.get_account_objects(alice.account_id, ledger_object_type="DIDDelete")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice, alice], method="account_objects")

    assert clio_response["transactions"][0]["tx"]["TransactionType"] == "DIDDelete", "Transaction type mismatch: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_different_markers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response_1 = rippled_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL", limit=10)
    test_validator.verify_test(rippled_server, response_1, method="account_objects")

    clio_response_1 = clio_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL", limit=10)
    test_validator.verify_test(clio_server, clio_response_1, method="account_objects")

    # To verify nft marker
    response_2 = rippled_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL", limit=10,
                                                    marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, method="account_objects")

    clio_response_2 = clio_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL", limit=10,
                                                      marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, method="account_objects")

    # To verify generic marker
    response_3 = rippled_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL",
                                                    marker=response_2["marker"])
    test_validator.verify_test(rippled_server, response_3, method="account_objects")

    clio_response_3 = clio_server.get_account_objects(account_id="rD2yanvPvPHksRjZTor7VizZxFz4J9vXnL",
                                                      marker=clio_response_2["marker"])
    test_validator.verify_test(clio_server, clio_response_3, method="account_objects")

    # Not comparing as Clio traverses nft_page from the last page while rippled traverses from the first page


def test_account_objects_nft_page_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response_1 = rippled_server.get_account_objects(account_id="rJVWhBp9j8aCD3Qf6aemyro5mDubsd9XuP", limit=10)
    test_validator.verify_test(rippled_server, response_1, method="account_objects")

    clio_response_1 = clio_server.get_account_objects(account_id="rJVWhBp9j8aCD3Qf6aemyro5mDubsd9XuP", limit=10)
    test_validator.verify_test(clio_server, clio_response_1, method="account_objects")

    assert clio_response_1["marker"].partition(',')[
               0] == "BFDE09F5442DEA6AA440C62889055BBDF157332CF157332C5EB8D96E00018CD3"

    # Not comparing as Clio traverses nft_page from the last page while rippled traverses from the first page


def test_account_objects_nft_page_without_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_objects(account_id="rJVWhBp9j8aCD3Qf6aemyro5mDubsd9XuP",
                                                  ledger_object_type="nft_page")
    test_validator.verify_test(rippled_server, response, method="account_objects")

    clio_response = clio_server.get_account_objects(account_id="rJVWhBp9j8aCD3Qf6aemyro5mDubsd9XuP",
                                                    ledger_object_type="nft_page")
    test_validator.verify_test(clio_server, clio_response, method="account_objects")

    # TODO: Make compare_dict robust enough to handle shuffled list values and add response comparison.


def test_account_objects_with_deletion_blockers_only_true(fx_rippled):
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

    # As deletion_blockers_only is defaulted to false, so all the account_objects created should be returned.
    response = rippled_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")
    assert len(response["account_objects"]) == 2, "All account_objects not listed"

    clio_response = clio_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")
    assert len(clio_response["account_objects"]) == 2, "All account_objects not listed"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # As deletion_blockers_only is true, so only includes objects that would block this account from being deleted.
    response = rippled_server.get_account_objects(account_1.account_id, deletion_blockers_only=True)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")
    assert len(response["account_objects"]) == 1, "all account_objects are listed"

    clio_response = clio_server.get_account_objects(account_1.account_id, deletion_blockers_only=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")
    assert len(clio_response["account_objects"]) == 1, "All account_objects are listed"

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.longrun
def test_account_objects_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True, amount="210000000")
    account_2 = rippled_server.create_account(fund=True)

    for channel_count in range(85):
        payload = {
            "tx_json": {
                "Account": account_1.account_id,
                "TransactionType": "PaymentChannelCreate",
                "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
                "Destination": account_2.account_id,
                "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
                "PublicKey": account_1.public_key_hex,
            },
            "secret": account_1.master_seed
        }

        response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_objects")

    clio_response = clio_server.get_account_objects(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_objects")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_objects(account_1.account_id, limit=40)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2], method="account_objects")

    clio_response_1 = clio_server.get_account_objects(account_1.account_id, limit=40)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2], method="account_objects")

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_objects(account_1.account_id, marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2], method="account_objects")

    clio_response_2 = clio_server.get_account_objects(account_1.account_id, marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1, account_2], method="account_objects")

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="account_objects")


def test_account_objects_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id,
                                                  ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_objects",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_objects(account.account_id,
                                                    ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_objects",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id,
                                                  ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_objects",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_objects(account.account_id,
                                                    ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_objects",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_objects(account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_objects",
                               response_result="actNotFound")

    clio_response = clio_server.get_account_objects(account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_objects",
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_objects")
    test_validator.verify_test(rippled_server, response, method="account_objects",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="account_objects")
    test_validator.verify_test(clio_server, clio_response, method="account_objects",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_malformed_type(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id, ledger_object_type="fghj")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_objects",
                               response_result="invalidParams")

    clio_response = clio_server.get_account_objects(account.account_id, ledger_object_type="dfgh")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_objects",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_objects(account_id="rnMmQy371RWLaBPwMd5awF5PEqSAaHrMi")
    test_validator.verify_test(rippled_server, response, method="account_objects",
                               response_result="actMalformed")

    clio_response = clio_server.get_account_objects(account_id="rnMmQy371RWLaBPwMd5awF5PEqSAaHrMi")
    test_validator.verify_test(clio_server, clio_response, method="account_objects",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_objects(account.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issues: https://github.com/XRPLF/rippled/issues/4541


def test_account_objects_with_limit_less_than_10(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id, limit=5)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_objects(account.account_id, limit=5)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_limit_greater_than_400(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id, limit=405)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_objects(account.account_id, limit=405)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, method="account_objects",
                               accounts=[account], response_result="invalidParams")

    clio_response = clio_server.get_account_objects(account.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, method="account_objects",
                               accounts=[account], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id,
                                                  marker="044C3E9F80DDA8381673FB0B149C642045952FC2DF82243AF80F5F2997988B15,0")
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_objects(account.account_id,
                                                    marker="3C378D0E2427D7130910F7FBB59DF9445AAE7E0610D34DFCB5220B6EBAFBAE1B,1")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4542


def test_account_objects_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_objects(account.account_id,
                                                  marker="B739DB0D825690B8ADAE8C6A96C97A7F8A2B356E2EBFBE9828BFD6F494A0072E")
    test_validator.verify_test(rippled_server, response, method="account_objects", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_account_objects(account.account_id,
                                                    marker="B739DB0D825690B8ADAE8C6A96C97A7F8A2B356E2EBFBE9828BFD6F494A0072E")
    test_validator.verify_test(clio_server, clio_response, method="account_objects", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_for_DIDSet(fx_rippled):
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

    response = rippled_server.get_account_objects(account_id=alice.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_objects")

    clio_response = clio_server.get_account_objects(account_id=alice.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_objects")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_for_DIDDelete(fx_rippled):
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

    response = rippled_server.get_account_objects(account_id=alice.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    clio_response = clio_server.get_account_objects(account_id=alice.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_for_OracleSet(fx_rippled):
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
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    response = rippled_server.get_account_objects(alice.account_id, ledger_object_type="oracle")
    test_validator.verify_test(rippled_server, response, accounts=[alice], method="account_objects")

    assert response["account_objects"][0]["LedgerEntryType"] == "Oracle", "type mismatch: {}".format(response)

    clio_response = clio_server.get_account_objects(alice.account_id, ledger_object_type="oracle")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="account_objects")

    assert clio_response["account_objects"][0]["LedgerEntryType"] == "Oracle", "type mismatch: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_objects_for_OracleDelete(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)
    response = rippled_server.oracle_set(alice, oracle_document_id=test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleDelete",
            "Account": alice.account_id,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    response = rippled_server.get_account_objects(alice.account_id, ledger_object_type="oracle")
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    assert not response["account_objects"], "account_objects found: {}".format(response)

    clio_response = clio_server.get_account_objects(alice.account_id, ledger_object_type="oracle")
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert not clio_response["account_objects"], "account_objects found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
