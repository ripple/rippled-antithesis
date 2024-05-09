import pytest
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper
from ..utils import test_validator
from ..utils import helper

log = log_helper.get_logger()


@pytest.mark.smoke
def test_deposit_authorized(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.deposit_preauthorize(account_object=account_1, third_party_account=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_authorized_src(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    pre_auth_response = rippled_server.deposit_preauthorize(account_object=account_1, third_party_account=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_index=pre_auth_response["tx_json"]["Sequence"])
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_index=pre_auth_response["tx_json"]["Sequence"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    pre_auth_response = rippled_server.deposit_preauthorize(account_object=account_1, third_party_account=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_index=pre_auth_response["tx_json"]["Sequence"])
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")

    rippled_response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                         ledger_hash=response["ledger_hash"])
    test_validator.verify_test(rippled_server, rippled_response, accounts=[account_1, account_2],
                               method="deposit_authorized")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_hash=response["ledger_hash"])
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized")

    assert helper.compare_dict(rippled_response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_authorized_dst(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2])

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_non_authorized_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_non_existent_src(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account()
    account_2 = rippled_server.create_account(fund=True)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="srcActNotFound")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="srcActNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_non_existent_dst(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account()

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="dstActNotFound")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="dstActNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_malformed_src(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "source_account": "rnFEAgEuT7cz5m7hAwJqewi15btjPT6qM",
            "destination_account": account_1.account_id,
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="deposit_authorized",
                               response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="deposit_authorized",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_malformed_dst(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": "rnFEAgEuT7cz5m7hAwJqewi15btjPT6qM",
            "source_account": account_1.account_id,
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="deposit_authorized",
                               response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="deposit_authorized",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_ledger_index_out_of_range(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.enable_deposit_auth(account_object=account_2)

    ledger_index = rippled_server.ledger_current() + 10

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_index=ledger_index)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="lgrNotFound")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_index=ledger_index)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_ledger_hash_out_of_range(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.enable_deposit_auth(account_object=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_hash="D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="lgrNotFound")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_hash="D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_malformed_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.enable_deposit_auth(account_object=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_index="cvbnm")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="invalidParams")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_index="cvbnm")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_with_malformed_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)
    rippled_server.enable_deposit_auth(account_object=account_2)

    response = rippled_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                 ledger_hash="D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401A")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="invalidParams")

    clio_response = clio_server.deposit_authorized(source_account=account_1, destination_account=account_2,
                                                   ledger_hash="D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401A")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="deposit_authorized",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_without_src(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "destination_account": account_1.account_id,
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="deposit_authorized",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="deposit_authorized",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_deposit_authorized_without_dst(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "source_account": account_1.account_id,
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="deposit_authorized",
                               response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload=payload, method="deposit_authorized")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="deposit_authorized",
                               response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
