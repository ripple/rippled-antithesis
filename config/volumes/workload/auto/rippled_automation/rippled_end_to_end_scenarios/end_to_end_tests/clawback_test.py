#!/usr/bin/env python
import pytest
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def verify_after_clawback(rippled_server, issuer, source, amount, response_result="tesSUCCESS"):
    bob = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": amount,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": source.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": amount,
                "issuer": issuer.account_id
            },
        },
        "secret": source.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[source, bob], response_result=response_result)


@pytest.mark.smoke
def test_clawback_full_amount_and_add_more_iou(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")

    log.info("")
    log.info("** Add more IOU after clawback")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount)


def test_clawback_partial_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = int(int(constants.DEFAULT_TRANSFER_AMOUNT)/3)
    transfer_amount = str(int(trustline_max) - clawback_amount)

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount)


def test_clawback_multiple_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")

    # 2nd account
    bob = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": bob.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, bob])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": bob.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice, bob])
    verify_after_clawback(rippled_server, issuer, bob, amount=transfer_amount, response_result="tecPATH_DRY")


def test_clawback_when_funds_not_available(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecINSUFFICIENT_FUNDS")


def test_clawback_multiple_times(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice],
                               response_result="tecINSUFFICIENT_FUNDS")


def test_clawback_zero_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = 0

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="temBAD_AMOUNT")


def test_clawback_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = "-10000000"

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="temBAD_AMOUNT")


def test_clawback_decimal_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = "100.5"
    transfer_amount = str(int(trustline_max) - float(clawback_amount))

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount)


def test_clawback_decimal_non_string(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = 10.5

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="invalidParams")


def test_clawback_more_than_iou(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = str(int(constants.DEFAULT_TRANSFER_AMOUNT) * 2)
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")


def test_clawback_with_no_flag_set(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    # Not enabling flag 'asfAllowTrustLineClawback'
    # account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    # test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_with_nofreeze_flag_set(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    enable_no_freeze_rsp = rippled_server.account_set(issuer, flag=constants.FLAGS_NO_FREEZE_asfNoFreeze)
    test_validator.verify_test(rippled_server, enable_no_freeze_rsp, accounts=[issuer])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer], response_result="tecNO_PERMISSION")


def test_clawback_on_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": "10000",
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer], response_result="temBAD_AMOUNT")


def test_clawback_with_flag_set_on_iou_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    account_set_response = rippled_server.account_set(alice, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_as_iou_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": alice.account_id,  # as IOU user
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="temBAD_AMOUNT")


def test_clawback_without_sub_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                # "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="invalidParams")


def test_clawback_without_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                # "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="invalidParams")


def test_clawback_with_mismatch_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "ABC",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_LINE")


def test_clawback_with_mismatch_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": alice.master_seed  # mismatch seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="badSecret")


def test_clawback_as_new_user(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    bob = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice, bob],
                               response_result="tecNO_PERMISSION")


def test_clawback_on_non_existent_iou_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    bob = rippled_server.create_account(fund=False)  # non-existent account
    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": bob.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="terNO_ACCOUNT")


def test_clawback_with_no_trustline(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])
    rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    # Skip creating TrustSet

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_LINE")


def test_clawback_on_preauth_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=issuer)
    rippled_server.deposit_preauthorize(account_object=issuer, third_party_account=bob)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice], response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_trustset(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    # Set flag after creating Trustset
    # account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    # test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_check(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": issuer.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_create_check_enable_flag_cash_check_and_clawback(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "CheckCreate",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "SendMax": constants.DEFAULT_CHECK_MAX_SEND
        },
        "secret": issuer.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    log.info("")
    log.info("** Now cash check and set flag again to clawback...")
    payload = {
        "tx_json": {
            "TransactionType": "CheckCash",
            "Account": alice.account_id,
            "CheckID": rippled_server.get_check_ids(issuer)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")


def test_clawback_enable_flag_after_paychan(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": issuer.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": alice.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": issuer.public_key_hex,
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_escrow(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "EscrowCreate",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "FinishAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_FINISH_AFTER),
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_ESCROW_CANCEL_AFTER)
        },
        "secret": issuer.master_seed
    }
    escrow_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, escrow_create_response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": issuer.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": issuer.account_id,
                "value": "2"
            },
        },
        "secret": issuer.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_nft_mint(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": issuer.account_id,
            "NFTokenTaxon": 0
        },
        "secret": issuer.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[issuer])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice])  # will not restrict clawback

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])
    verify_after_clawback(rippled_server, issuer, alice, amount=transfer_amount, response_result="tecPATH_DRY")


def test_clawback_enable_flag_after_nft_create_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT
    transfer_amount = trustline_max

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": issuer.account_id,
            "NFTokenTaxon": 0
        },
        "secret": issuer.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[issuer])

    token_id = rippled_server.get_nft_tokens(issuer.account_id)[0]
    payload = {
        "tx_json": {
            "TransactionType": "NFTokenCreateOffer",
            "Account": issuer.account_id,
            "NFTokenID": token_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": 1  # 1:sell offer, otherwise buy offer
        },
        "secret": issuer.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[issuer])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_ticket_create(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": issuer.account_id,
            "Sequence": rippled_server.get_account_sequence(issuer),
            "TicketCount": 1
        },
        "secret": issuer.master_seed
    }
    ticket_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, ticket_create_response, accounts=[issuer, alice])

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")


def test_clawback_enable_flag_after_signerlist(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    trustline_max = constants.DEFAULT_TRANSFER_AMOUNT
    clawback_amount = constants.DEFAULT_TRANSFER_AMOUNT

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    signer_1 = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "Account": issuer.account_id,
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
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    account_set_response = rippled_server.account_set(issuer, flag=constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback)
    test_validator.verify_test(rippled_server, account_set_response, accounts=[issuer, alice],
                               response_result="tecOWNERS")

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": trustline_max,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": trustline_max,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice])

    payload = {
        "tx_json": {
            "TransactionType": "Clawback",
            "Account": issuer.account_id,
            "Amount": {
                "currency": "USD",
                "value": clawback_amount,
                "issuer": alice.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[issuer, alice], response_result="tecNO_PERMISSION")

