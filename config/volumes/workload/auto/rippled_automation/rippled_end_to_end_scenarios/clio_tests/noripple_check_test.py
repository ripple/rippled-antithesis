import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper, helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_noripple_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_default_ripple_flag_and_role_as_gateway(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 2, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 2, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response = rippled_server.account_set(account_1, 8)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_no_ripple_flag_and_role_as_gateway(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 2, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 2, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": 0
            },
            "Flags": 262144,
            "Sequence": rippled_server.get_account_sequence(account_1.account_id)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 1, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_default_ripple_flag_no_ripple_flag_and_role_as_gateway(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 2, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 2, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": 0
            },
            "Flags": 262144,
            "Sequence": rippled_server.get_account_sequence(account_1.account_id)
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 1, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response = rippled_server.account_set(account_1, 8)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 0, "Problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 0, "Problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_role_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")

    clio_response = clio_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_default_ripple_flag_and_role_as_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 1, "Problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response = rippled_server.account_set(account_2, 8)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 2, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 2, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_with_no_ripple_flag_and_role_as_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 1, "Problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(clio_response["problems"]) == 1, "Problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "Flags": 131072,
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

    response = rippled_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 0, "Two problems not found: {}".format(response)

    clio_response = clio_server.get_noripple_check(account_2.account_id, role="user")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")
    assert len(response["problems"]) == 0, "Two problems not found: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_transactions_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id, transactions=False)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")

    clio_response = clio_server.get_noripple_check(account_1.account_id, transactions=False)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # NOTE: As rippling is not enabled to move currency all the way down,
    # this test should pass with "problems" in method: noripple_check call
    # response = rippled_server.account_set(account_1, 8)  # asfDefaultRipple

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

    response = rippled_server.get_noripple_check(account_1.account_id, limit=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="noripple_check")

    clio_response = clio_server.get_noripple_check(account_1.account_id, limit=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="noripple_check")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_without_role(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "account": account.account_id,
            "limit": 2,
            "transactions": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="noripple_check")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="noripple_check",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="noripple_check")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="noripple_check",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "role": "gateway",
            "limit": 2,
            "transactions": True
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="noripple_check")
    test_validator.verify_test(rippled_server, response, method="noripple_check", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="noripple_check")
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_noripple_check(account_id=account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account],
                               method="noripple_check",
                               response_result="actNotFound")

    clio_response = clio_server.get_noripple_check(account_id=account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account],
                               method="noripple_check",
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account_id=account.account_id,
                                                 ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="noripple_check",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_noripple_check(account_id=account.account_id,
                                                   ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="noripple_check",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account_id=account.account_id,
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="noripple_check",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_noripple_check(account_id=account.account_id,
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="noripple_check",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_invalid_role(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account_id=account.account_id, role="fgh")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="noripple_check",
                               response_result="invalidParams")

    clio_response = clio_server.get_noripple_check(account_id=account.account_id, role="fgh")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="noripple_check",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_noripple_check(account_id="r7x8JFCExiWopq7YuhK8AXjLhZe4fQ5e")
    test_validator.verify_test(rippled_server, response, method="noripple_check", response_result="actMalformed")

    clio_response = clio_server.get_noripple_check(account_id="r7x8JFCExiWopq7YuhK8AXjLhZe4fQ5e")
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", response_result="actMalformed")

    # assert helper.compare_dict(response, clio_response, ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    # Clio issue: https://ripplelabs.atlassian.net/browse/CLIO-298


def test_noripple_check_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="noripple_check")

    clio_response = clio_server.get_noripple_check(account.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", accounts=[account],
                               response_result="invalidParams")

    # assert helper.compare_dict(response, clio_response,
    #                            ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    # Rippled issue: https://github.com/XRPLF/rippled/issues/4541


def test_noripple_check_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, method="noripple_check", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_noripple_check(account.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_invalid_transactions(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account.account_id, transactions="ghj")
    test_validator.verify_test(rippled_server, response, method="noripple_check", accounts=[account])

    clio_response = clio_server.get_noripple_check(account.account_id, transactions="ghj")
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_noripple_check_with_invalid_transactions_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_noripple_check(account.account_id, transactions="ghj", api_version=2)
    test_validator.verify_test(rippled_server, response, method="noripple_check", accounts=[account],
                               response_result="invalidParams")

    clio_response = clio_server.get_noripple_check(account.account_id, transactions="ghj", api_version=2)
    test_validator.verify_test(clio_server, clio_response, method="noripple_check", accounts=[account],
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
