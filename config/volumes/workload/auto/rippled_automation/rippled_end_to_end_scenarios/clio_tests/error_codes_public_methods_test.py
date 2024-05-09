from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


def test_manifest_without_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(rippled_server, response, method="manifest", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(clio_server, clio_response, method="manifest", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_manifest_with_malformed_public_key(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "public_key": "nHUFE9prPXPrHcG3SkwP1UzAQbSphqyQkQK9ATXLZsfkezhhda3"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(rippled_server, response, method="manifest", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="manifest")
    test_validator.verify_test(clio_server, clio_response, method="manifest", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_submit_only_with_invalid_tx_blob(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "tx_blob": "12000022800000002401408B7C6140000000000027106840000000000000147321024776336CD51BC5D0F74902ECE8E3DE491ABC7291698B52794E7B8B36A340CD00744630440220254B7B63F79DDF99D35A5FAD88BE0939DACB5543715190DD92645FCA0F280B9E0220269E2E77E6DBD1AE512E850D48331C62E2933BB55BC525BAB858843E4104999781147029D5084E4D8398DA4C8D63D1A0F1C3574CDBAB8314093708BF6E4A7F4F37455312372BE799788F846Da"
        }
    }

    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, response_result="invalidTransaction")

    clio_response = clio_server.execute_transaction(payload)
    test_validator.verify_test(clio_server, clio_response, response_result="invalidTransaction")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_submit_only_without_tx_blob(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }

    response = rippled_server.execute_transaction(payload, method="submit")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="submit")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams")


def test_submit_multisigned_with_empty_tx_json(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }

    response = rippled_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_submit_multisigned_with_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "Account": "rN2E6TWNdrQWyr5nf8TjqYKakRDQ2i4uKPa",
            "Amount": constants.DEFAULT_TRANSFER_AMOUNT,
            "Destination": "rNbCao7aZsKZe5iJ4a2jphifJgTtH9hJAg",
            "Fee": "30000",
            "Flags": 2147483648,
            "Sequence": 19527746,
            "Signers": [
                {
                    "Signer": {
                        "Account": "rrsiLoJKyZXmPjM9y9MVhRnkFqEg9ry8RG",
                        "SigningPubKey": "03BD578163A16737EA6FABB5D7C64B67079E985EB599B48019A3C8BB91F633B063",
                        "TxnSignature": "304402201A9705A43883B07016F874F8A1B012A3D7AC4323A7BC81329FADBC5767ACDF260220733983E72317F5FF3077CB1184A5FC43F8C690D56DC69417E5D9A1FB8315523B"
                    }
                }
            ],
            "SigningPubKey": "",
            "TransactionType": "Payment",
            "hash": "425F4AADF3CAEAF228BB147E0E7D8F36C43036C8FB8105CC0220D7E5004FE675"
        }
    }

    response = rippled_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(rippled_server, response, response_result="srcActMalformed")

    clio_response = clio_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(clio_server, clio_response, response_result="srcActMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_submit_multisigned_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "Account": account.account_id,
            "Amount": "11000000",
            "Destination": "rNbCao7aZsKZe5iJ4a2jphifJgTtH9hJAg",
            "Fee": "30000",
            "Flags": 2147483648,
            "Sequence": 19527746,
            "Signers": [
                {
                    "Signer": {
                        "Account": "rrsiLoJKyZXmPjM9y9MVhRnkFqEg9ry8RG",
                        "SigningPubKey": "03BD578163A16737EA6FABB5D7C64B67079E985EB599B48019A3C8BB91F633B063",
                        "TxnSignature": "304402201A9705A43883B07016F874F8A1B012A3D7AC4323A7BC81329FADBC5767ACDF260220733983E72317F5FF3077CB1184A5FC43F8C690D56DC69417E5D9A1FB8315523B"
                    }
                }
            ],
            "SigningPubKey": "",
            "TransactionType": "Payment",
            "hash": "425F4AADF3CAEAF228BB147E0E7D8F36C43036C8FB8105CC0220D7E5004FE675"
        }
    }

    response = rippled_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="srcActNotFound")

    clio_response = clio_server.execute_transaction(payload, method="submit_multisigned")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="srcActNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
