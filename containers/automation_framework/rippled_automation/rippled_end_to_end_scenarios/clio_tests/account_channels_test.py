import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_account_channels(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

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

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True, amount="210000000")
    account_2 = rippled_server.create_account(fund=True)

    for channel_count in range(85):
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

    response = rippled_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account_1.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_1 = rippled_server.get_account_channels(account_1.account_id, limit=40)
    test_validator.verify_test(rippled_server, response_1, accounts=[account_1, account_2],
                               method="account_channels")

    clio_response_1 = clio_server.get_account_channels(account_1.account_id, limit=40)
    test_validator.verify_test(clio_server, clio_response_1, accounts=[account_1, account_2],
                               method="account_channels")

    assert helper.compare_dict(response_1, clio_response_1,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    response_2 = rippled_server.get_account_channels(account_1.account_id, marker=response_1["marker"])
    test_validator.verify_test(rippled_server, response_2, accounts=[account_1, account_2],
                               method="account_channels")

    clio_response_2 = clio_server.get_account_channels(account_1.account_id, marker=clio_response_1["marker"])
    test_validator.verify_test(clio_server, clio_response_2, accounts=[account_1, account_2],
                               method="account_channels")

    assert helper.compare_dict(response_2, clio_response_2,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"

    assert clio_server.compare_responses(response=clio_response, response_1=clio_response_1, response_2=clio_response_2,
                                         key="channels")


def test_account_channels_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_channels(account.account_id)
    test_validator.verify_test(rippled_server, response, response_result="actNotFound", accounts=[account],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id)
    test_validator.verify_test(clio_server, clio_response, response_result="actNotFound", accounts=[account],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_non_existent_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)
    destination_account = rippled_server.create_account()

    response = rippled_server.get_account_channels(account.account_id,
                                                   destination_account=destination_account.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[account, destination_account])

    clio_response = clio_server.get_account_channels(account.account_id,
                                                     destination_account=destination_account.account_id)
    test_validator.verify_test(clio_server, clio_response, accounts=[account, destination_account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id,
                                                   ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="lgrNotFound",
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id,
                                                     ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="lgrNotFound",
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id,
                                                   ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="lgrNotFound",
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id,
                                                     ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="lgrNotFound",
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        },
    }
    response = rippled_server.execute_transaction(payload, method="account_channels")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams",
                               method="account_channels")

    clio_response = clio_server.execute_transaction(payload, method="account_channels")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams",
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_channels(account_id="rwzbuFaqDW2o4kVgFgAe7LZPoYRpaycXQ")
    test_validator.verify_test(rippled_server, response, response_result="actMalformed", method="account_channels")

    clio_response = clio_server.get_account_channels(account_id="rwzbuFaqDW2o4kVgFgAe7LZPoYRpaycXQ")
    test_validator.verify_test(clio_server, clio_response, response_result="actMalformed", method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_malformed_destination(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account_id=account.account_id,
                                                   destination_account="rwzbuFaqDW2o4kVgFgAe7LZPoYRpaycXQ")
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="actMalformed")

    clio_response = clio_server.get_account_channels(account_id=account.account_id,
                                                     destination_account="rwzbuFaqDW2o4kVgFgAe7LZPoYRpaycXQ")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit=0)
    test_validator.verify_test(rippled_server, response, accounts=[account], response_result="invalidParams")

    clio_response = clio_server.get_account_channels(account.account_id, limit=0)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit="10")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id, limit="10")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit=10,
                                                   marker="0F2B3316E00B7167141646777CC0F1B7A5FE7B0A74D137AFA62D0AF9DE808A692FEC454B303E4E6B53403704292D5FE67F0FE211E80F4C66626454AA3D3797F0")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id, limit=10,
                                                     marker="0F2B3316E00B7167141646777CC0F1B7A5FE7B0A74D137AFA62D0AF9DE808A692FEC454B303E4E6B53403704292D5FE67F0FE211E80F4C66626454AA3D3797F0")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit=10,
                                                   marker="0F2B3316E00B7167141646777CC0F1B7A5FE7B0A74D137AFA62D0AF9DE808A69")
    test_validator.verify_test(rippled_server, response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    clio_response = clio_server.get_account_channels(account.account_id, limit=10,
                                                     marker="0F2B3316E00B7167141646777CC0F1B7A5FE7B0A74D137AFA62D0AF9DE808A69")
    test_validator.verify_test(clio_server, clio_response, response_result="invalidParams", accounts=[account],
                               method="account_channels")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_limit_less_than_10(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit=5)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_channels(account.account_id, limit=5)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_channels_with_limit_greater_than_400(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_channels(account.account_id, limit=405)
    test_validator.verify_test(rippled_server, response, accounts=[account])

    clio_response = clio_server.get_account_channels(account.account_id, limit=405)
    test_validator.verify_test(clio_server, clio_response, accounts=[account])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
