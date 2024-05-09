import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_channel_authorize(fx_rippled):
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
            "SettleDelay": constants.DEFAULT_PAYCHAN_SETTLE_DELAY,
            "PublicKey": account_1.public_key_hex
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "seed": account_1.master_seed,
            "key_type": "secp256k1",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_invalid_channel_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "42AC583481E3CA98F8918A7616D333D473FD66C3807BFB10D6348AA97E3E8C3",
            "secret": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize", response_result="channelMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="channelMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_invalid_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "secret": "snaHt9CNVuHMcqof7NKV9ry9iHDn",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "secret": "snaHt9CNVuHMcqof7NKV9ry9iHDn",
            "amount": -10000
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="channelAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="channelAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_non_xrp_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "secret": "snaHt9CNVuHMcqof7NKV9ry9iHDn",
            "amount": 10.000
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="channelAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="channelAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_secp256k1_and_master_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "secp256k1",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_secp256k1_and_invalid_master_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "secp256k1",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="badSeed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="badSeed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_master_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_invalid_master_seed(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="badSeed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="badSeed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_invalid_key_type(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed255191",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "secret": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_seed_and_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "seed": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "secret": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_passphrase(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "passphrase": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_invalid_passphrase(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "passphrase": "ssRbYZ4kH5KTRDjyJHLyTam38F3G",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_passphrase_and_secret(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "key_type": "ed25519",
            "passphrase": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "secret": "ssRbYZ4kH5KTRDjyJHLyTam38F3G8",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_seed_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "key_type": "ed25519",
            "seed_hex": "29EF22150032A759AE63B21332C19F43",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_and_invalid_seed_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "key_type": "ed25519",
            "seed_hex": "AC02846B26A6EA008F9FBE32EBC248D",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="badSeed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="badSeed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_authorize_with_key_type_ed25519_secret_and_seed_hex(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "key_type": "ed25519",
            "secret": "ssHBj4CpzcBmBuewUHh11hjSrUaxp",
            "seed_hex": "29EF22150032A759AE63B21332C19F43",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(rippled_server, response, method="channel_authorize",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_authorize")
    test_validator.verify_test(clio_server, clio_response, method="channel_authorize",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
