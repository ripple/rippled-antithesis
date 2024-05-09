#!/usr/bin/env python
import os
import sys
import time

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import helper
from ..utils import test_validator

log = log_helper.get_logger()


@pytest.mark.smoke
def test_offer_create_offer_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_claim_before_expiration(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_OFFER_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_claim_after_expiration(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Expiration": rippled_server.get_rippled_epoch_time(constants.DEFAULT_OFFER_EXPIRATION_IN_SECONDS)
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    rippled_server.wait_before_executing_transaction(wait_time=constants.DEFAULT_OFFER_EXPIRATION_IN_SECONDS)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_on_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account()
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
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="srcActNotFound")


def test_offer_create_to_self(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_1.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_1.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1],
                               offer_crossing=False)


def test_offer_create_with_zero_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 0,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="temBAD_OFFER")


def test_offer_create_with_decimal_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": "10.5",
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")

def test_offer_create_with_negative_taker_gets(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": -5000,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="temBAD_OFFER")


def test_offer_create_with_xrp_on_taker_pays(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="temBAD_OFFER")


def test_offer_create_with_exact_account_balance_and_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False))
    bob_offer = int(alice_offer)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_1_drop_over_available_balance_and_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) + 1
    bob_offer = int(alice_offer)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_1_drop_less_than_available_balance_and_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) - 1
    bob_offer = int(alice_offer)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_1_xrp_over_available_balance_and_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) + 1000000
    bob_offer = int(alice_offer)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_bob_offers_one_drop_less_than_alice1(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = constants.DEFAULT_ACCOUNT_BALANCE
    bob_offer = int(alice_offer) - 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": alice_offer,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_bob_offers_one_drop_more_than_alice1(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = constants.DEFAULT_ACCOUNT_BALANCE
    bob_offer = int(alice_offer) + 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": alice_offer,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_bob_offers_two_drops_less_than_alice(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = constants.DEFAULT_ACCOUNT_BALANCE
    bob_offer = int(alice_offer) - 2

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": alice_offer,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_bob_offers_two_drops_more_than_alice(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = constants.DEFAULT_ACCOUNT_BALANCE
    bob_offer = int(alice_offer) + 2

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": alice_offer,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_bob_offers_one_drop_less_than_alice_not_default_low_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) - 1
    bob_offer = int(alice_offer) - 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_bob_offers_one_drop_more_than_alice_not_default_low_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) - 1
    bob_offer = int(alice_offer) + 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_bob_offers_one_drop_less_than_alice_not_default_high_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) + 1
    bob_offer = int(alice_offer) - 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])


    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_bob_offers_one_drop_more_than_alice_not_default_high_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    alice_offer = int(rippled_server.get_account_balance(account_1.account_id, verbose=False)) + 1
    bob_offer = int(alice_offer) + 1

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(alice_offer),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(bob_offer),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_claim_over_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(int(constants.DEFAULT_TRANSFER_AMOUNT) * 2),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_with_invalid_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": "INVALID_CURRENCY",
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_offer_create_with_exact_base_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=constants.BASE_RESERVE)
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
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_OFFER")


def test_offer_create_with_no_enough_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True, amount=str(
        int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE) - 1))
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
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="tecINSUF_RESERVE_OFFER")


def test_offer_create_on_account_with_upto_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True,
                                              amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE)))
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
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_claim_on_account_with_just_base_reserve_and_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True,
                                              amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE)))
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
            }
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_2.account_id,
            "Destination": account_1.account_id,
            "Amount": constants.DEFAULT_TRANSACTION_FEE
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_claim_without_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)

    log.info("")
    log.info("Claiming without an available offer")
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_claim_with_no_matching_issued_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "USD",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_claim_with_no_matching_value_in_issued_currency(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GTO",
                "issuer": account_2.account_id,
                "value": "20"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_make_payment_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": account_1.account_id,
            "Destination": account_2.account_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_partial_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 5000,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 3000,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_partial_claim_hitting_owner_reserve(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    amount = int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE) + 2000
    account_1 = rippled_server.create_account(fund=True, amount=str(amount))
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 3000,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 2000,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_create_multiple_offers_claim_multiple_full_offers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 3000,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    for i in range(1, 3):
        log.info("")
        log.info("Creating Offer: {}".format(i))
        offer_create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 3000,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    for i in range(1, 3):
        log.info("")
        log.info("Claiming Offer: {}".format(i))
        offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
        test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                                   offer_crossing=True)


def test_create_multiple_offers_claim_multiple_partial_offers(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 3000,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_1.master_seed
    }
    for i in range(1, 3):
        log.info("")
        log.info("Creating Offer: {}".format(i))
        offer_create_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 2500,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    for i in range(1, 3):
        log.info("")
        log.info("Claiming Offer: {}".format(i))
        offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
        test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                                   offer_crossing=True)


def test_offer_create_claim_partial_offer_create_claim_full(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 3000,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 2500,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 3500,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 3500,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_claim_on_auth_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=account_2)

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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_claim_after_offer_create(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

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
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_offer_cancel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])


def test_cancel_a_cancelled_offer_cancel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])

    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])


def test_offer_cancel_with_non_existent_offer_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response) + 1
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2],
                               response_result="temBAD_SEQUENCE")


def test_offer_cancel_on_invalid_offer_sequence(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response) - 1
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    # cancelling with invalid offer sequence results in "tesSUCCESS"
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2],
                               offer_cancelled=False, ignore_account_objects=True)


def test_offer_cancel_by_taker_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_2.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_2.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])


def test_cancel_unfunded_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1),
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response_2 = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response_2, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])


def test_cancel_partial_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 5000,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 2000,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response_2 = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response_2, accounts=[account_1, account_2],
                               offer_crossing=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCancel",
            "Account": account_1.account_id,
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_1.master_seed
    }
    offer_cancel_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_cancel_response, accounts=[account_1, account_2])


def test_offer_create_offer_update_offer_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 5000,
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

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": 2000,
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "OfferSequence": rippled_server.get_txn_sequence(offer_create_response)
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": 2000,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_with_flag_tfPassive_offer_unclaimed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

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
            "Flags": "65536"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=False)


def test_offer_create_with_flag_tfPassive_crossing_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Flags": "65536"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_with_flag_tfImmediateOrCancel_to_cancel_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Flags": "131072"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="tecKILLED", offer_crossing=False)


def test_offer_create_with_flag_tfImmediateOrCancel_to_cross_offer_immediately(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

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
            "Flags": "131072"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_with_flag_tfFillOrKill_to_kill_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Flags": "262144"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="tecKILLED", offer_crossing=False)


def test_offer_create_with_flag_tfFillOrKill_to_fill_full_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

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
            "Flags": "262144"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_with_flag_tfFillOrKill_to_fill_partial_offer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_2.account_id,
            "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
            "TakerGets": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
        },
        "secret": account_2.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload, issuer=account_1.account_id)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "OfferCreate",
            "Account": account_1.account_id,
            "TakerGets": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1),
            "TakerPays": {
                "currency": "GKO",
                "issuer": account_2.account_id,
                "value": "2"
            },
            "Flags": "262144"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               offer_crossing=True)


def test_offer_create_with_invalid_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    # Create and fund account
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
            "Flags": "393216"
        },
        "secret": account_1.master_seed
    }
    offer_create_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, offer_create_response, accounts=[account_1, account_2],
                               response_result="temINVALID_FLAG", offer_crossing=False)


def test_rippled_respects_currency_code_case(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    issuer = rippled_server.create_account(fund=True)

    currencies = ["USD", "uSD"]
    book_directory = set()
    for currency in currencies:
        payload = {
            "tx_json": {
                "TransactionType": "OfferCreate",
                "Account": issuer.account_id,
                "TakerPays": constants.DEFAULT_TRANSFER_AMOUNT,
                "TakerGets": {
                    "currency": currency,
                    "issuer": issuer.account_id,
                    "value": "10"
                }
            },
            "secret": issuer.master_seed
        }
        rippled_server.execute_transaction(payload=payload)

        payload = {
            "tx_json": {
                "taker_pays": {
                    "currency": "XRP"
                },
                "taker_gets": {
                    "currency": currency,
                    "issuer": issuer.account_id,
                }
            }
        }
        offers = rippled_server.execute_transaction(payload=payload, method="book_offers")
        test_validator.verify_test(rippled_server, offers, method="book_offers")
        book_directory.add(offers["offers"][0]["BookDirectory"])

    assert len(book_directory) == len(set(currencies)), \
        f"{len(book_directory)} book directories found for {currencies}"
