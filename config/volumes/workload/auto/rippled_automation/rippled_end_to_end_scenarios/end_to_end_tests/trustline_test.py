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


def test_trustline_one_currency_payment(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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


def test_create_trustline_with_disallow_incoming_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)

    rippled_server.account_set(alice, flag=constants.FLAGS_TRUSTLINE_asfDisallowIncomingTrustline)
    rippled_server.account_set(issuer, flag=constants.FLAGS_TRUSTLINE_asfDisallowIncomingTrustline)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[issuer, alice],
                               response_result="tecNO_PERMISSION")


@pytest.mark.smoke
def test_issued_currency_payment_to_another_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    # Enable rippling
    response = rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    alice = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    bob = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": issuer.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])


def test_issued_currency_payment_to_another_account_without_trustline(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    issuer = rippled_server.create_account(fund=True)
    # Enable rippling
    response = rippled_server.account_set(issuer, flag=8)  # asfDefaultRipple

    alice = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": issuer.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": issuer.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    bob = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": issuer.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob], response_result="tecPATH_DRY")


def test_trustline_ignore_default(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
    assert not rippled_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)["lines"], \
        "account_lines found"
    assert rippled_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)["lines"], \
        "account_lines not found"

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
    assert not rippled_server.get_account_lines(account_1.account_id, ignore_default=True, verbose=False)["lines"], \
        "account_lines found"
    assert rippled_server.get_account_lines(account_2.account_id, ignore_default=True, verbose=False)["lines"], \
        "account_lines not found"


def test_trustline_with_decimal_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
                "value": "10.5",
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])


def test_trustline_with_non_string_decimal_value(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
                "value": 10.5,  # non-string decimal value
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_trustline_invalid_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account()
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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="tecNO_DST")


def test_trustline_invalid_recipient(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

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
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="srcActNotFound")


def test_trustline_with_non_standard_currency_code(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "0158415500000000C1F76FF6ECB0BAC600000000",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2])


def test_trustline_with_invalid_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "---",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_trustline_with_invalid_currency_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USDX",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_trustline_to_self(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_1.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_1.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1], response_result="temDST_IS_SRC")


def test_trustline_with_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "XRP",
                "issuer": account_1.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_trustline_negative_limit_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": -100,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="temBAD_LIMIT")


def test_trustline_zero_limit_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": account_2.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": account_1.account_id,
                "value": 0,
            },
        },
        "secret": account_2.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[account_1, account_2],
                               response_result="tecNO_LINE_REDUNDANT")

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


def test_payment_amount_more_than_limit_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
                "value": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1),
                "issuer": account_1.account_id
            },
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecPATH_PARTIAL")


def test_cross_currencies_payment_btc_usd(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # Trustline for carol to finally receive currency
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # BTC for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "BTC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            # "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (USD) to carol (USD)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
            "Paths": [
                [
                    {
                        "currency": "USD",
                        "issuer": gw.account_id
                    }
                ]
            ],
            "SendMax": {
                "currency": "BTC",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])


def test_cross_currencies_payment_btc_usd_no_paths(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # Trustline for carol to finally receive currency
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # BTC for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "BTC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            # "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (USD) to carol (USD)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
            # No "Paths" specified
            "SendMax": {
                "currency": "BTC",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])


def test_cross_currencies_with_offer_and_payment_btc_usd(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    gw = rippled_server.create_account(fund=True)
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # BTC for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "BTC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            # "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # Offer from Alice
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": alice.account_id,
            # "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerPays": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": alice.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob],
                               offer_crossing=True)

    # alice (USD) to carol (USD)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])


def test_cross_currencies_xrp_usd(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # Trustline for carol to finally receive currency
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": 100,
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (XRP) to carol (USD)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
            "Paths": [
                [
                    {
                        "currency": "USD",
                        "issuer": gw.account_id
                    }
                ]
            ],
            "SendMax": "100",
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, carol])


def test_cross_currencies_to_self_usd_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True, amount=15000000)
    bob = rippled_server.create_account(fund=True, amount=50000000)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # USD for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": 35000000,
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (USD) to alice (self) (XRP)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": alice.account_id,
            "Flags": 131072,
            "Amount": "35000000",
            "SendMax": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    carol = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, carol])


def test_cross_currencies_usd_xrp(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True, amount=15000000)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # USD for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": 25000000,
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (USD) to carol (XRP)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": "25000000",
            "SendMax": {
                "currency": "USD",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, carol])


def test_cross_currencies_usd_xrp_no_sendmax(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True, amount=15000000)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # USD for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Offer from bob
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": 25000000,
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (USD) to carol (XRP)
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": 25000000,
            # No "SendMax" specified
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, carol],
                               response_result="temBAD_SEND_XRP_PARTIAL")


def test_cross_currencies_payment_btc_xrp_usd(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # Trustline for carol to finally receive currency
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # BTC for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "BTC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob: USD for XRP
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": 100,
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # Offer from bob: XRP for BTC
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": 100,
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (BTC) to carol (USD) claiming/via Bob's offer
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": 20,
                "issuer": gw.account_id
            },
            "Paths": [
                [
                    {
                        "currency": "XRP",
                    },
                    {
                        "currency": "USD",
                        "issuer": gw.account_id
                    }
                ]
            ],
            "SendMax": {
                "currency": "BTC",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol])


def test_cross_currencies_payment_btc_xrp_usd_no_paths(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    alice = rippled_server.create_account(fund=True)
    bob = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    # Issuer for currencies
    gw = rippled_server.create_account(fund=True)

    # Enable rippling to move currency all the way to carol
    response = rippled_server.account_set(gw, flag=8)  # asfDefaultRipple

    # Trustline for carol to finally receive currency
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": carol.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": carol.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[carol])

    # BTC for alice
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": alice.account_id,
            "LimitAmount": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": alice.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": alice.account_id,
            "Amount": {
                "currency": "BTC",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # USD for bob
    payload = {
        "tx_json": {
            "TransactionType": "TrustSet",
            "Account": bob.account_id,
            "LimitAmount": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
            },
        },
        "secret": bob.master_seed
    }
    create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, create_response, accounts=[bob])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": gw.account_id,
            "Destination": bob.account_id,
            "Amount": {
                "currency": "USD",
                "value": constants.DEFAULT_TRANSFER_AMOUNT,
                "issuer": gw.account_id
            },
        },
        "secret": gw.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])

    # Offer from bob: USD for XRP
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": 100,
            "TakerGets": {
                "currency": "USD",
                "issuer": gw.account_id,
                "value": "20"
            },
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # Offer from bob: XRP for BTC
    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": bob.account_id,
            "TakerPays": {
                "currency": "BTC",
                "issuer": gw.account_id,
                "value": "20"
            },
            "TakerGets": 100,
        },
        "secret": bob.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=alice.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[alice, bob])

    # alice (BTC) to carol (USD) claiming/via Bob's offer
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": alice.account_id,
            "Destination": carol.account_id,
            "Flags": 131072,
            "Amount": {
                "currency": "USD",
                "value": 20,
                "issuer": gw.account_id
            },
            # No "Paths" specified
            "SendMax": {
                "currency": "BTC",
                "value": "20",
                "issuer": gw.account_id
            },
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob, carol], response_result="tecPATH_DRY")


def test_issue_lowercase_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    issuer = rippled_server.create_account(fund=True)
    alice = rippled_server.create_account(fund=True)
    currency_code = 'usd'
    usd = {
                "currency": currency_code,
                "issuer": issuer.account_id,
            }
    rippled_server.create_trustline(alice, usd)
    trustlines = rippled_server.get_all_trustlines(alice.account_id)
    assert currency_code in [trustline['currency'] for trustline in trustlines], \
        f"No trustline with currency '{currency_code}' created."
