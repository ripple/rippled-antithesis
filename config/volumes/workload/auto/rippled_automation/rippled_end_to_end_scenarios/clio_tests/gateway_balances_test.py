import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_gateway_balances(fx_rippled):
    # validating all three cases for one account i.e., assets, balances, obligations.

    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)
    account_4 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "CUC",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "CUC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "INR",
                "issuer": account_4.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_4.account_id,
            "Destination": account_1.account_id,
            "Amount": {
                "currency": "INR",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_4.account_id
            },
        },
        "secret": account_4.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "hotwallet": account_2.account_id,
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3, account_4],
                               method="gateway_balances")
    assert response["balances"], "balances not found: {}".format(response)
    assert response["obligations"], "obligations not found: {}".format(response)
    assert response["assets"], "assets not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, account_3, account_4],
                               method="gateway_balances")
    assert clio_response["balances"], "balances not found: {}".format(response)
    assert clio_response["obligations"], "obligations not found: {}".format(response)
    assert clio_response["assets"], "assets not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_and_validate_separately(fx_rippled):
    # validating all three cases separately i.e., assets, balances, obligations.

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

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "account": account_2.account_id,
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="gateway_balances")
    assert response["assets"], "assets not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="gateway_balances")
    assert clio_response["assets"], "assets not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="gateway_balances")
    assert response["obligations"], "obligations not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="gateway_balances")
    assert clio_response["obligations"], "obligations not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "hotwallet": account_2.account_id,
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="gateway_balances")
    assert response["balances"], "balances not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="gateway_balances")
    assert clio_response["balances"], "balances not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_hot_wallet_accounts_and_validate_balances(fx_rippled):
    # verifying list of accounts in hotwallet and validating balances.

    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "INR",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "INR",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "hotwallet": [
                account_2.account_id,
                account_3.account_id
            ],
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert len(response["balances"]) == 2, "balances not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert len(clio_response["balances"]) == 2, "balances not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_and_validate_balances_obligations(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "hotwallet": account_2.account_id,
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert len(response["balances"]) == 1, "balances not found: {}".format(response)
    assert len(response["obligations"]) == 1, "obligations not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert len(clio_response["balances"]) == 1, "balances not found: {}".format(response)
    assert len(clio_response["obligations"]) == 1, "obligations not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_obligations_overflow(fx_rippled):
    # verifying list of accounts in hotwallet and validating balances.

    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    account_3 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "9999999999999999e80",
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": {
                "currency": "USD",
                "value": "9999999999999999e80",
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_3.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": "9999999999999999e80",
            },
        },
        "secret": account_3.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_3.account_id,
            "Amount": {
                "currency": "USD",
                "value": "9999999999999999e80",
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3])

    payload = {
        "tx_json": {
            "account": account_1.account_id,
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert response["obligations"], "obligations not found: {}".format(response)

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2, account_3],
                               method="gateway_balances")
    assert clio_response["obligations"], "obligations not found: {}".format(response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    # Create and fund account
    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_gateway_balances(account_id=account.account_id,
                                                   ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="gateway_balances",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_gateway_balances(account_id=account.account_id,
                                                     ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="gateway_balances",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    # Create and fund account
    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_gateway_balances(account_id=account.account_id,
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="gateway_balances",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_gateway_balances(account_id=account.account_id,
                                                     ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="gateway_balances",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_gateway_balances(account_id=account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="gateway_balances")

    clio_response = clio_server.get_gateway_balances(account_id=account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="gateway_balances",
                               response_result="actNotFound")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4546


def test_gateway_balances_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, method="gateway_balances", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, method="gateway_balances", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_malformed_hot_wallet_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account": account.account_id,
            "hotwallet": [
                "rhKKk5KB8LuxmjvTSA7r3iYmJXGqnno7M"
            ],
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="gateway_balances",
                               response_result="invalidHotWallet")

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="gateway_balances",
                               response_result="invalidParams")

    # validating separately till the issues are fixed.
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4548
    # Clio issue: https://ripplelabs.atlassian.net/browse/CLIO-293


def test_gateway_balances_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_gateway_balances(account_id="rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2")
    test_validator.verify_test(rippled_server, response, method="gateway_balances",
                               response_result="actMalformed")

    clio_response = clio_server.get_gateway_balances(account_id="rMwjYedjc7qqtKYVLiAccJSmCwih4LnE2")
    test_validator.verify_test(clio_server, clio_response, method="gateway_balances",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_gateway_balances_with_non_existent_hot_wallet_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    hotwallet_account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "account": account.account_id,
            "hotwallet": [
                hotwallet_account.account_id
            ],
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidHotWallet")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4546


def test_gateway_balances_with_unassociated_hot_wallet(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    hotwallet_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account": account.account_id,
            "hotwallet": hotwallet_account.account_id,
            "ledger_index": "validated",
            "strict": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(rippled_server, response, accounts=[account, hotwallet_account])

    clio_response = clio_server.execute_transaction(payload=payload, method="gateway_balances")
    test_validator.verify_test(clio_server, clio_response, accounts=[account, hotwallet_account],
                               response_result="invalidHotWallet")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Rippled issue: https://github.com/XRPLF/rippled/issues/4549
