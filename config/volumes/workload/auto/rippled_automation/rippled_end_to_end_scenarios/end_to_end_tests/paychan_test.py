#!/usr/bin/env python
import os
import pytest
import sys
import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from . import constants
from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_verify_create_payment_channel_with_source_and_destination_tags(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 67890,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")


def test_verify_create_payment_channel_with_disallow_incoming_flag(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.account_set(account_2, constants.FLAGS_PAYCHAN_asfDisallowIncomingPayChan)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 67890,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_create_payment_channel_with_unfunded_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account()
    account_2 = rippled_server.create_account(fund=True)

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
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="srcActNotFound")


def test_create_payment_channel_with_unfunded_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

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
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_DST")


def test_create_payment_channel_with_amounts_non_xrp_verify_error(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": {"currency": "USD",
                       "value": 10000,
                       "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"},
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_payment_channel_with_negative_amounts_verify_error(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": -10000,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_create_payment_channel_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": "rwX2fSPGaz23vTxo3bhrNyAmnfc2jSZrn8",
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="tecNO_DST")


def test_create_payment_channel_to_itself(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_1.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='temDST_IS_SRC')


def test_create_payment_channel_with_zero_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": 0,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='temBAD_AMOUNT')


def test_create_payment_channel_with_decimal_value_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": 10.1,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='invalidParams')


def test_create_payment_channel_with_negative_settle_delay(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": -80,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='invalidParams')


def test_verify_create_payment_channel_with_zero_settle_delay(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": 0,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")


def test_create_payment_channel_with_mismatched_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": "shgvf6Qvz5BSmC91kkfW25fTVcEdD"
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="badSecret")


def test_verify_create_payment_channel_with_cancel_after(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 678,
            "CancelAfter": rippled_server.get_rippled_epoch_time(constants.DEFAULT_PAYCHAN_CANCEL_AFTER),
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")


def test_create_payment_channel_with_negative_cancel_after(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
            "SourceTag": 12345,
            "DestinationTag": 678,
            "CancelAfter": -533171558,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_validate_payment_channel_with_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # Creating 12 channels to verify limit parameter in account_channels method.
    # Initially considering channel_count parameter as '0' and using it as a counter.
    channels = 12
    channel_count = 0
    while channel_count < channels:
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
        channel_count += 1

    response = rippled_server.get_account_channels(account_1.account_id, limit=channels - 1)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")


def test_authorization_of_payment_channel_amount_without_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_authorization_of_amount_more_than_payment_channel_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1),
            "secret": account_1.master_seed
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_verify_authorization_of_payment_channel_amount_with_zero_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": '0',
            "secret": account_1.master_seed
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_authorization_of_payment_channel_amount_with_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": '-10000',
            "secret": account_1.master_seed
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="channelAmtMalformed")


def test_verify_authorization_of_payment_channel_amount_with_key_type_secp256k1_and_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed": account_1.master_seed,
            "key_type": "secp256k1"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_authorization_of_payment_channel_amount_with_key_type_secp256k1_and_mismatched_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G",
            "key_type": "secp256k1"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="badSeed")


def test_verify_authorization_of_payment_channel_amount_with_key_type_ed25519_and_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed": account_1.master_seed,
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_authorization_of_payment_channel_amount_with_key_type_ed25519_and_mismatched_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G",
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="badSeed")


def test_authorization_of_payment_channel_amount_with_invalid_key_type_ed25519_and_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed":  account_1.master_seed,
            "key_type": "ed25519fgd"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_authorization_of_payment_channel_amount_with_key_type_and_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "secret":  account_1.master_seed,
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_authorization_of_payment_channel_amount_with_key_type_seed_and_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed": account_1.master_seed,
            "secret":  account_1.master_seed,
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_verify_authorization_of_payment_channel_amount_with_key_type_and_passphrase(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "passphrase": account_1.master_seed,
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_authorization_of_payment_channel_amount_with_key_type_and_mismatched_passphrase(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "passphrase": "sRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_verify_authorization_of_payment_channel_amount_with_key_type_and_seed_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed_hex": account_1.master_seed_hex,
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_verify_authorization_of_payment_channel_amount_with_key_type_and_mismatched_seed_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "seed_hex": "4EBA09F024F92FC47980DC17328465A7",
            "key_type": "ed25519"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="channel_authorize")


def test_verify_payment_channel_authorized_funds(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount":  constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    channel_verify_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "signature": channel_authorize_response["signature"],
            "public_key": account_1.public_key_hex,
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
    }

    channel_verify_response = rippled_server.execute_transaction(payload=channel_verify_payload,
                                                                 method="channel_verify")
    test_validator.verify_test(rippled_server, channel_verify_response, accounts=[account_1, account_2],
                               method="channel_verify")


def test_verify_payment_channel_authorized_funds_with_mismatched_channel_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    """
    To verify the payment_channel_authorized_funds with mismatched channel_id using
    existing payment channel parameters signature,public_key, amount with mismatched channel_id
    instead of whole flow i.e., creating accounts, PaymentChannelcreate, channel_authorize and channel_verify.
    """

    payload = {
        "tx_json": {
            "channel_id": "0AFEDE508AD408B91F42F0C5705F9480951DCF9185E65C39085B308776A80D65",  # channel_id mismatch
            "signature": "3044022027C18BA3A613DA05CF5B0AA918CDB1E023AA4A2E80AB53F8D9CBD63B9615FE4D022034DE0E3D9E7E062E072FC684C355A3D6D006A03AAC1261C779FF293B0F72B4CD",
            "public_key": "0357A8397F0C1D77C80F68A9C8B1FF43480E6973092CA553D6FF0435EA3DAA8A34",
            "amount": "1000000"
        }

    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]


def test_verify_payment_channel_authorized_funds_with_mismatched_signature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    """
    To verify the test_verify_payment_channel_authorized_funds_with_mismatched_signature using
    existing payment channel parameters channel_id,public_key, amount with mismatched signature
    instead of whole flow i.e., creating accounts, PaymentChannelcreate, channel_authorize and channel_verify.
    """
    payload = {
        "tx_json": {
            "channel_id": "0AFEDE508AD408B91F42F0C5705F9480951DCF9185E65C39085B308776A80D66",
            "signature": "3044022027C18BA3A613DA05CF5B0AA918CDB1E023AA4A2E80AB53F8D9CBD63B9615FE4D022034DE0E3D9E7E062E072FC684C355A3D6D006A03AAC1261C779FF293B0F72B4CC",  # signature mismatch
            "public_key": "0357A8397F0C1D77C80F68A9C8B1FF43480E6973092CA553D6FF0435EA3DAA8A34",
            "amount": "1000000"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]


def test_verify_payment_channel_authorized_funds_with_mismatched_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    """
    To verify the test_verify_payment_channel_authorized_funds_with_mismatched_public_key using
    existing payment channel parameters channel_id,signature, amount with mismatched public_key
    instead of whole flow i.e., creating accounts, PaymentChannelcreate, channel_authorize and channel_verify.
    """
    payload = {
        "tx_json":         {
            "channel_id": "0AFEDE508AD408B91F42F0C5705F9480951DCF9185E65C39085B308776A80D66",
            "signature": "3044022027C18BA3A613DA05CF5B0AA918CDB1E023AA4A2E80AB53F8D9CBD63B9615FE4D022034DE0E3D9E7E062E072FC684C355A3D6D006A03AAC1261C779FF293B0F72B4CD",
            "public_key": "0357A8397F0C1D77C80F68A9C8B1FF43480E6973092CA553D6FF0435EA3DAA8A35",  # public_key mismatch
            "amount": "1000000"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]


def test_verify_payment_channel_authorized_funds_with_unauthorized_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    """
       To verify the test_verify_payment_channel_authorized_funds_with_unauthorized_amount using
       existing payment channel parameters channel_id,signature, public_key with mismatched amount
       instead of whole flow i.e., creating accounts, PaymentChannelcreate, channel_authorize and channel_verify.
       """
    payload = {
        "tx_json": {
            "channel_id": "0AFEDE508AD408B91F42F0C5705F9480951DCF9185E65C39085B308776A80D66",
            "signature": "3044022027C18BA3A613DA05CF5B0AA918CDB1E023AA4A2E80AB53F8D9CBD63B9615FE4D022034DE0E3D9E7E062E072FC684C355A3D6D006A03AAC1261C779FF293B0F72B4CD",
            "public_key": "0357A8397F0C1D77C80F68A9C8B1FF43480E6973092CA553D6FF0435EA3DAA8A34",
            "amount": "100000"# amount mismatch
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]


def test_verify_payment_channel_claim_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])


def test_payment_channel_claim_by_sender_with_mismatched_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": "snnTJKSbHpTDvPt794JCmAe63pTrP"
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="badSecret")


def test_payment_channel_claim_by_sender_with_mismatched_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    source_account = rippled_server.create_account(fund=True)
    dest_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": source_account.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": dest_account.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": source_account.public_key_hex,
        },
        "secret": source_account.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[source_account, dest_account])
    channel_id = rippled_server.get_channel_ids(source_account)[0]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": channel_id
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_verify_payment_channel_claim_by_sender_with_cumulative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])


def test_payment_channel_claim_by_sender_with_non_cumulative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": int(constants.DEFAULT_TRANSFER_AMOUNT)//2,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_PAYMENT")


def test_payment_channel_claim_by_sender_with_zero_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": "0",
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_sender_with_negative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": "-100000",
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_sender_with_decimal_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": "5000.1",
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="invalidParams")


def test_payment_channel_claim_by_sender_with_more_than_channel_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": int(constants.DEFAULT_TRANSFER_AMOUNT) + 1,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_PAYMENT")


@pytest.mark.smoke
def test_verify_payment_channel_claim_by_destination_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])


def test_payment_channel_claim_by_destination_account_with_mismatched_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    # As this is a negative test skipping the flow before Payment Channel Claim.
    # Using mismatched signature value because the test will fail at secret validation before moving to signature and channel validation.

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": "D88C26208ED26CE9D857307D0CD3400C3C9CA58107E0E267CDAA4FB5CA7D4F57",
            "Signature": "3045022100D319E0DA9EA6F265900D26B5F99B917B1E070415C7289C57AB4E61214C6323C302200F362481493512F0C26BBABF3456DE4916C00BA7448FBC0E3ECDAE1B0BFC5E52"
        },
        "secret": "snnTJKSbHpTDvPt794JCmAe63pTrP"
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="badSecret")


def test_payment_channel_claim_by_destination_with_more_than_authorized_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 1000),
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_SIGNATURE")


def test_payment_channel_claim_by_destination_with_less_than_authorized_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_account_with_less_than_cumulative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount":  str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_account_with_cumulative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": channel_authorize_payload["tx_json"]["amount"],
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": channel_authorize_payload["tx_json"]["amount"],
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])


def test_payment_channel_claim_by_destination_account_with_less_than_cumulative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": channel_authorize_payload["tx_json"]["amount"],
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": channel_authorize_payload["tx_json"]["amount"],
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT)//2),
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED_PAYMENT")


def test_payment_channel_claim_by_destination_account_with_zero_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": "0",
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_account_with_negative_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": "-5000",
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_with_balance_greater_than_authorized_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 100),
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_with_balance_greater_than_channel_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": str(int(constants.DEFAULT_TRANSFER_AMOUNT) + 100),
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_claim_by_destination_with_mismatched_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": "96DA1E8228CCD220870B78975A7724DB4ABE6FEE5C3EB6046E563FA36E907941",
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_SIGNATURE")


def test_payment_channel_claim_by_destination_with_mismatched_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": "02D334769B366937C52016E339A5D0C9A9ED6291F875162E0379C9AD8B08C5BC52",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": channel_authorize_response["signature"]
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_SIGNATURE")


def test_payment_channel_claim_by_destination_with_mismatched_signature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "PublicKey": account_1.public_key_hex,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Signature": "3045022100D319E0DA9EA6F265900D26B5F99B917B1E070415C7289C57AB4E61214C6323C302200F362481493512F0C26BBABF3456DE4916C00BA7448FBC0E3ECDAE1B0BFC5E52"
        },
        "secret": account_2.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="temBAD_SIGNATURE")


def test_verify_payment_channel_claim_by_pre_authorized_sender_with_deposit_auth_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_2)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    rippled_server.deposit_preauthorize(account_object=account_2, third_party_account=account_1)

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2])


def test_payment_channel_claim_by_sender_with_deposit_auth_destination_and_no_preauth_senders(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_2)
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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0],
        },
        "secret": account_1.master_seed
    }

    payment_channel_claim_response = rippled_server.execute_transaction(payload=payment_channel_claim_payload)
    test_validator.verify_test(rippled_server, payment_channel_claim_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_fund_an_invalid_channel_verify_error(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": 'B363279DAC9095C0A76A619AC9F2E2B17A3BB288B9C17B8358FA7C84AD9B7448'
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='tecNO_ENTRY')


def test_create_paychannel_with_not_enough_funds_verify_error(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": int(rippled_server.get_account_balance(account_1.account_id)) + 1,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex,
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='tecUNFUNDED')


def test_claim_paychanel_with_non_xrp_amounts_verify_error(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Amount": {"currency": "USD",
                       "value": 10000,
                       "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"},
            "Balance": {"currency": "USD",
                        "value": 10000,
                        "issuer": "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"},
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               response_result='temBAD_AMOUNT')


def test_verify_payment_channel_fund_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_channels")
    assert response["channels"][0]["amount"] == str(2 * int(constants.DEFAULT_TRANSFER_AMOUNT)), "Channel amount mismatched"


def test_payment_channel_fund_by_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_2.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_payment_channel_fund_by_third_party_before_settle_delay(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    another_account = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": another_account.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": another_account.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_payment_channel_fund_by_sender_with_mismatched_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": "sneCTo9tWbvW5Wb4pARgjWK8Mtj26"
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="badSecret")


def test_payment_channel_fund_by_sender_with_mismatched_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    source_account = rippled_server.create_account(fund=True)
    dest_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": source_account.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": dest_account.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": source_account.public_key_hex,
        },
        "secret": source_account.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[source_account, dest_account])
    channel_id = rippled_server.get_channel_ids(source_account)[0]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": channel_id,
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="tecNO_PERMISSION")


def test_payment_channel_fund_by_sender_with_zero_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": "0"
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_fund_by_sender_with_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": "-10000"
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="temBAD_AMOUNT")


def test_payment_channel_fund_with_amount_greater_than_sender_balance(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_ACCOUNT_BALANCE
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_response, accounts=[account_1, account_2],
                               response_result="tecUNFUNDED")


def test_verify_channel_close_with_claim(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channels = rippled_server.get_account_channels(account_1.account_id)
    assert (channels['channels'].__len__() == 1)
    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Flags": "131072"
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, offer_crossing=False, accounts=[account_1, account_2])
    channels = rippled_server.get_account_channels(account_1.account_id)
    assert (channels['channels'].__len__() == 0)


def test_verify_channel_close_with_unclaimed_xrp_by_sender(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payment_channel_fund_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelFund",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Expiration": rippled_server.get_rippled_epoch_time(seconds_elapsed=constants.DEFAULT_PAYCHAN_EXPIRATION)
        },
        "secret": account_1.master_seed
    }

    payment_channel_fund_payload_response = rippled_server.execute_transaction(payload=payment_channel_fund_payload)
    test_validator.verify_test(rippled_server, payment_channel_fund_payload_response, accounts=[account_1, account_2])

    channel_close_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Flags": "131072"
        },
        "secret": account_1.master_seed
    }

    channel_close_response = rippled_server.execute_transaction(payload=channel_close_payload)
    test_validator.verify_test(rippled_server, channel_close_response)
    """
     This flag closes the channel immediately if it has no more XRP allocated to it after processing the current claim,
      or if the destination address uses it. If the source address uses this flag when the channel still holds XRP, 
      this schedules the channel to close after SettleDelay seconds have passed.
      
      After the transaction is included in a validated ledger, either party can look up the currently-scheduled expiration 
      of the channel using the account_channels method and check for expiration in account channels response.
    """

    epoch_wait_time = rippled_server.get_rippled_epoch_time(seconds_elapsed=constants.DEFAULT_PAYCHAN_SETTLE_DELAY)
    rippled_server.wait_before_executing_transaction(epoch_wait_time=epoch_wait_time, verbose=False)

    epoch_wait_time = rippled_server.get_rippled_epoch_time(seconds_elapsed=constants. DEFAULT_PAYCHAN_EXPIRATION)
    rippled_server.wait_before_executing_transaction(epoch_wait_time=epoch_wait_time, verbose=False)

    payment_channel_claim_payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Balance": constants.DEFAULT_TRANSFER_AMOUNT,
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": account_1.master_seed
    }

    rippled_server.execute_transaction(payload=payment_channel_claim_payload)

    account_channel_response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, account_channel_response,
                               accounts=[account_1, account_2])
    assert (account_channel_response["channels"].__len__() == 0), "Channel is not closed"


def test_channel_close_by_sender_with_mismatched_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    source_account = rippled_server.create_account(fund=True)
    dest_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": source_account.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": dest_account.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": source_account.public_key_hex,
        },
        "secret": source_account.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[source_account, dest_account])
    channel_id = rippled_server.get_channel_ids(source_account)[0]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": channel_id,
            "Flags": "131072"
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, response_result="tecNO_PERMISSION")


def test_verify_channel_close_by_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Flags": "131072"
        },
        "secret": account_2.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, offer_crossing=False, accounts=[account_1, account_2])

    account_channel_response = rippled_server.get_account_channels(account_1.account_id)

    assert (account_channel_response["channels"].__len__() == 0)


def test_verify_channel_close_with_authorized_unclaimed_xrp_by_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

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

    channel_authorize_payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "secret": account_1.master_seed
        }
    }

    channel_authorize_response = rippled_server.execute_transaction(payload=channel_authorize_payload,
                                                                    method="channel_authorize")
    test_validator.verify_test(rippled_server, channel_authorize_response, accounts=[account_1, account_2],
                               method="channel_authorize")

    channel_close_payload = {
        "tx_json": {
            "Account": account_2.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": rippled_server.get_channel_ids(account_1)[0],
            "Flags": "131072"
        },
        "secret": account_2.master_seed
    }

    channel_close_response = rippled_server.execute_transaction(payload=channel_close_payload)
    test_validator.verify_test(rippled_server, channel_close_response, offer_crossing=False,
                               accounts=[account_1, account_2])

    account_channel_response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, account_channel_response,
                               accounts=[account_1, account_2])
    assert (account_channel_response["channels"].__len__() == 0)


def test_channel_close_by_third_party_account_before_expiration(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)
    third_party_account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": account_1.account_id,
            "TransactionType": "PaymentChannelCreate",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": account_2.account_id,
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }

    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "Account": third_party_account.account_id,
            "TransactionType": "PaymentChannelClaim",
            "Channel": rippled_server.get_channel_ids(account_1)[0]
        },
        "secret": third_party_account.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], offer_crossing=False,
                               response_result="tecNO_PERMISSION")


# def test_verify_third_party_can_close_after_cancel():
#     pass
#
# def test_verify_third_party_close_before_cancel_after_verify_tec_no_permission():
#     pass
#
# def test_verify_owner_can_close_after_settle_delay_time():
#     pass
#
# def test_verify_increase_the_expiration_time_verify_can_be_done():
#     pass
#
# def test_verify_decrease_the_expiration_but_still_above_min_expiration_verify_can_be_done():
#     pass
#
# def test_verify_decrease_the_expiration_below_min_expiration_verify_tem_bad_expiration():
#     pass

# Extend the expiration after the expiration has already passed.(TEST THIS BEHAVIOR NOT SURE WHAT MIGHT BE GOING ON OUT HERE)
#
# Owner closes, will close after settleDelay receiver can still claim past settleTime, channel will close
#
# Owner tries to close channel, but it will remain open (settle delay) -> claim the entire amount Channel is now dry, -> can close before expiration date
#
# Auth amount defaults to balance if not present -> Owner tries to close channel, but it will remain open (settle delay) -> Claim again
#
# Verify we can create a channel where dst disallows XRP
#
# Verify we can claim to a channel where dst disallows XRP


