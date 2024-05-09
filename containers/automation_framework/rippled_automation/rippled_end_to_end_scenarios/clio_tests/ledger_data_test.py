import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import helper
from ..utils import test_validator


def test_ledger_data_with_type_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="account")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="AccountRoot")

    clio_response = clio_server.get_ledger_data(ledger_type="account")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="AccountRoot")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_amendments(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="amendments")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="amendments")

    clio_response = clio_server.get_ledger_data(ledger_type="amendments")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="amendments")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_amm(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="amm")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="AMM")

    clio_response = clio_server.get_ledger_data(ledger_type="amm")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="AMM")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_fee(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="fee")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="fee")

    clio_response = clio_server.get_ledger_data(ledger_type="fee")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="fee")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_hashes(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="hashes")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="hashes")

    clio_response = clio_server.get_ledger_data(ledger_type="hashes")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="hashes")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="check")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="Check")

    clio_response = clio_server.get_ledger_data(ledger_type="check")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="Check")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_deposit_preauth(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="deposit_preauth")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="DepositPreauth")

    clio_response = clio_server.get_ledger_data(ledger_type="deposit_preauth")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="DepositPreauth")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_directory(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="directory")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="DirectoryNode")

    clio_response = clio_server.get_ledger_data(ledger_type="directory")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="DirectoryNode")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="escrow")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="Escrow")

    clio_response = clio_server.get_ledger_data(ledger_type="escrow")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="Escrow")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_nft_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="nft_offer")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="NFTokenOffer")

    clio_response = clio_server.get_ledger_data(ledger_type="nft_offer")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="NFTokenOffer")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="offer")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="Offer")

    clio_response = clio_server.get_ledger_data(ledger_type="offer")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="Offer")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_payment_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="payment_channel")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="PayChannel")

    clio_response = clio_server.get_ledger_data(ledger_type="payment_channel")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="PayChannel")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_signer_list(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="signer_list")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="SignerList")

    clio_response = clio_server.get_ledger_data(ledger_type="signer_list")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="SignerList")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_state(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="state")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="RippleState")

    clio_response = clio_server.get_ledger_data(ledger_type="state")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="RippleState")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_type_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="ticket")
    test_validator.verify_test(rippled_server, response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=response, ledger_data_type="Ticket")

    clio_response = clio_server.get_ledger_data(ledger_type="ticket")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
    test_validator.validate_ledger_data_with_type(response=clio_response, ledger_data_type="Ticket")

    # Not comparing Clio and Rippled as the responses are expected to differ


def test_ledger_data_with_ledger_index(fx_rippled):
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
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.get_ledger_data(ledger_index=rippled_server.get_txn_sequence(payment_response), limit=5)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_data")

    clio_response = clio_server.get_ledger_data(ledger_index=clio_server.get_txn_sequence(payment_response), limit=5)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_data")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_binary_as_false(fx_rippled):
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
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.get_ledger_data(ledger_index=rippled_server.get_txn_sequence(payment_response), limit=5,
                                              binary=False)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_data")

    clio_response = clio_server.get_ledger_data(ledger_index=clio_server.get_txn_sequence(payment_response), limit=5,
                                                binary=False)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_data")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_limit_and_marker(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    clio_response = clio_server.get_ledger_data(limit=85)
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")

    clio_response_1 = clio_server.get_ledger_data(limit=40)
    test_validator.verify_test(clio_server, clio_response_1, method="ledger_data")

    clio_response_2 = clio_server.get_ledger_data(marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, method="ledger_data")

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="state")


def test_ledger_data_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "binary": True,
            "ledger_index": rippled_server.ledger_current() + 100
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_hash": "E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="lgrNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_incorrect_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_hash": "E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_empty_parameters(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")


def test_ledger_data_with_ledger_hash(fx_rippled):
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
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    tx_response = rippled_server.tx(tx_id=payment_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "ledger_index": tx_response["ledger_index"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "ledger_hash": response["ledger_hash"]
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", accounts=[account_1, account_2])

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", accounts=[account_1, account_2])

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Commenting out till issue is resolved: https://github.com/XRPLF/rippled/issues/4755


def test_ledger_data_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "limit": 0
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response)

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4541


def test_ledger_data_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "limit": "5"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_ledger_index_and_api_version_2(fx_rippled):
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
    payment_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, payment_response, accounts=[account_1, account_2])

    response = rippled_server.get_ledger_data(ledger_index=rippled_server.get_txn_sequence(payment_response), limit=5,
                                              api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="ledger_data")

    clio_response = clio_server.get_ledger_data(ledger_index=clio_server.get_txn_sequence(payment_response), limit=5,
                                                api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="ledger_data")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "limit": 10,
            "marker": "000005B6929113043709D3E5E7D4BAEC924A0A4CFDC534C37054FAB1A6E57A9"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "limit": 10,
            "marker": "0DC1C3F1E5233C9CD72AEFDD6460EAD380E9C91245C114E2772F50ADC029E166,0"
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="ledger_data")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_binary_true_and_limit_greater_than_2048(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(limit=2050, binary=True)
    test_validator.verify_test(rippled_server, response, method="ledger_data")

    clio_response = clio_server.get_ledger_data(limit=2050, binary=True)
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Removing the comparison as it might be expected to differ


def test_ledger_data_with_binary_false_and_limit_greater_than_256(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(limit=260, binary=False)
    test_validator.verify_test(rippled_server, response, method="ledger_data")

    clio_response = clio_server.get_ledger_data(limit=260, binary=False)
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Removing the comparison as it might be expected to differ


def test_ledger_data_with_malformed_type(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="dfgh")
    test_validator.verify_test(rippled_server, response, method="ledger_data", response_result="invalidParams")

    clio_response = clio_server.get_ledger_data(ledger_type="dfgh")
    test_validator.verify_test(clio_server, clio_response, method="ledger_data", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_ledger_data_with_type_did(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_ledger_data(ledger_type="did", limit=5)
    test_validator.verify_test(rippled_server, response, method="ledger_data")

    clio_response = clio_server.get_ledger_data(ledger_type="did", limit=5)
    test_validator.verify_test(clio_server, clio_response, method="ledger_data")
