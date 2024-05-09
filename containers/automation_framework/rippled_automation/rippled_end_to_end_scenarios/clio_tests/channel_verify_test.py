import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_channel_verify(fx_rippled):
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

    # Get signature
    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "seed": account_1.master_seed,
            "key_type": "secp256k1",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_authorize")

    payload = {
        "tx_json": {
            "channel_id": rippled_server.get_channel_ids(account_1)[0],
            "public_key": account_1.public_key_hex,
            "signature": response["signature"],
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="channel_verify")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="channel_verify")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_invalid_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="channelMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="channelMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_unassociated_channel(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "30790949841D651573FF844E2E4C1EB59810419C88F75DD085EE50399A2E9A63",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response)
    assert not response["signature_verified"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_invalid_signature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E0",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response)
    assert not response["signature_verified"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_unassociated_signature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "304402207C7B67593A59BC7CD208939DE00AE868C2E5BCD81A339266559C03C4E2332D68022014B94054825B3A6782446A68D41711887195BDBC63EDD34E6A05364A8C02A783",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response)
    assert not response["signature_verified"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_invalid_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="publicMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="publicMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_unassociated_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "03A022119ACEBD3FBD7AED7F4E988D6F08A3D2F59D8B453326A8A497A500F2DD45",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response)
    assert not response["signature_verified"]

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response)
    assert not response["signature_verified"]

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_negative_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": -10000
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="channelAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify",
                               response_result="channelAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_with_non_xrp_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": 1.0000
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="channelAmtMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify",
                               response_result="channelAmtMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_without_channel_id(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_without_signature(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_without_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00",
            "amount": constants.DEFAULT_TRANSFER_AMOUNT
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_channel_verify_without_amount(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "channel_id": "85465AE2F1C9F0EE57643FB9B409C9D17A6D21C87C9EF584EAFBEAE9E7071BF4",
            "public_key": "02E46174127726CBBD23209F155B32542FFD329CEF36C5FC67A292BEDB112D095A",
            "signature": "A925E3F257C74F1A48C5F3E2A19BD1F616D5573389882AC923F132248EE77A92CE62F328DA183B859351F48D442783A0869A531AC2866C2CFAE8314186CD0E00"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(rippled_server, response, method="channel_verify", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="channel_verify")
    test_validator.verify_test(clio_server, clio_response, method="channel_verify", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
