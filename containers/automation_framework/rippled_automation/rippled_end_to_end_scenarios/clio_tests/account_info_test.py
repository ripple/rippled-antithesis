import pytest

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from ..utils import log_helper, helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_account_info(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_ident(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "ident": account_1.account_id,
            "ledger_index": "validated"
        }
    }

    response = rippled_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_signerlists_true(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, signer_lists=True, queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, signer_lists=True, queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_signerlists_true_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, signer_lists=True, queue=False,
                                               ledger_index="validated", api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, signer_lists=True, queue=False,
                                                 ledger_index="validated", api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_signerlists_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, signer_lists=False, queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, signer_lists=False, queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_defaultRipple_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 8)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["defaultRipple"], "defaultRipple flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["defaultRipple"], "defaultRipple flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_depositAuth_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    rippled_server.enable_deposit_auth(account_object=account_1)

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["depositAuth"], "depositAuth flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["depositAuth"], "depositAuth flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disableMasterKey_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    payload = {
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account_1.account_id,
            "SetFlag": 4
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    submit_blob_response = rippled_server.submit_blob(response)
    test_validator.verify_test(rippled_server, submit_blob_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["disableMasterKey"], "disableMasterKey flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["disableMasterKey"], "disableMasterKey flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disallowIncomingCheck_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 13)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["disallowIncomingCheck"], "disallowIncomingCheck flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["disallowIncomingCheck"], "disallowIncomingCheck flag not enabled: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disallowIncomingNFTokenOffer_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 12)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"][
        "disallowIncomingNFTokenOffer"], "disallowIncomingNFTokenOffer flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"][
        "disallowIncomingNFTokenOffer"], "disallowIncomingNFTokenOffer flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disallowIncomingPayChan_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 14)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"][
        "disallowIncomingPayChan"], "disallowIncomingPayChan flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"][
        "disallowIncomingPayChan"], "disallowIncomingPayChan flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disallowIncomingTrustline_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 15)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"][
        "disallowIncomingTrustline"], "disallowIncomingTrustline flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"][
        "disallowIncomingTrustline"], "disallowIncomingTrustline flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_disallowIncomingXRP_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 3)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"][
        "disallowIncomingXRP"], "disallowIncomingXRP flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"][
        "disallowIncomingXRP"], "disallowIncomingXRP flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_globalFreeze_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 7)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["globalFreeze"], "globalFreeze flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["globalFreeze"], "globalFreeze flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_noFreeze_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 6)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["noFreeze"], "noFreeze flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["noFreeze"], "noFreeze flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_passwordSpent_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "SetRegularKey",
            "Account": account_1.account_id,
            "RegularKey": account_2.account_id,
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    submit_blob_response = rippled_server.submit_blob(response)
    test_validator.verify_test(rippled_server, submit_blob_response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["passwordSpent"], "passwordSpent flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["passwordSpent"], "passwordSpent flag not enabled: {}".format(clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_requireAuthorization_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["requireAuthorization"], "requireAuthorization flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["requireAuthorization"], "requireAuthorization flag not enabled: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_of_requireDestinationTag_flag_enabled_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.account_set(account_1, 1)
    test_validator.verify_test(rippled_server, response, accounts=[account_1])

    response = rippled_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")
    assert response["account_flags"]["requireDestinationTag"], "requireDestinationTag flag not enabled: {}".format(response)

    clio_response = clio_server.get_account_info(account_1.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")
    assert clio_response["account_flags"]["requireDestinationTag"], "requireDestinationTag flag not enabled: {}".format(
        clio_response)

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_ledger_index_validated(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_info")

    clio_response = clio_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    response = rippled_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(rippled_server, response, method="account_info", accounts=[account],
                               response_result="actNotFound")

    clio_response = clio_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, method="account_info", accounts=[account],
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_ident_as_non_existent_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account()

    payload = {
        "tx_json": {
            "ident": account.account_id,
            "ledger_index": "validated",
            "strict": False
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(rippled_server, response, method="account_info", accounts=[account],
                               response_result="actNotFound")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(clio_server, clio_response, method="account_info", accounts=[account],
                               response_result="actNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_id=account.account_id, queue=False,
                                               ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_info",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_info(account_id=account.account_id, queue=False,
                                                 ledger_index=rippled_server.ledger_current() + 100)
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_info",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated",
                                               ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_info",
                               response_result="lgrNotFound")

    clio_response = clio_server.get_account_info(account_id=account.account_id, queue=False, ledger_index="validated",
                                                 ledger_hash="E74BAE8DD7F22B6C996B0C4C4BF044B80A6707D2FA763EFE811E61FB18270ED3")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_info",
                               response_result="lgrNotFound")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_without_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ledger_index": "validated"
        }
    }
    response = rippled_server.execute_transaction(payload,  method="account_info")
    test_validator.verify_test(rippled_server, response, method="account_info", response_result="invalidParams")

    clio_response = clio_server.execute_transaction(payload,  method="account_info")
    test_validator.verify_test(clio_server, clio_response, method="account_info", response_result="invalidParams")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    response = rippled_server.get_account_info(account_id="rUNcc6x9hMnahibdvaw5ZgmnqjnAdRTNA", queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, method="account_info",
                               response_result="actMalformed")

    clio_response = clio_server.get_account_info(account_id="rUNcc6x9hMnahibdvaw5ZgmnqjnAdRTNA", queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, response, method="account_info",
                               response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_ident_as_malformed_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "ident": "rUNcc6x9hMnahibdvaw5ZgmnqjnAdRTNA",
            "ledger_index": "validated",
            "strict": False
        },
    }
    response = rippled_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(rippled_server, response,  method="account_info", response_result="actMalformed")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(clio_server, clio_response, method="account_info", response_result="actMalformed")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_ident_and_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "ident": account.account_id,
            "account": account.account_id,
            "ledger_index": "validated",
            "strict": False
        },
    }

    response = rippled_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(rippled_server, response, accounts=[account], method="account_info")

    clio_response = clio_server.execute_transaction(payload=payload, method="account_info")
    test_validator.verify_test(clio_server, clio_response, accounts=[account], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_malformed_signerlists(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, signer_lists="fgh", queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, signer_lists="fgh", queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


@pytest.mark.skip("Rippled issue: https://github.com/XRPLF/rippled/issues/4830")
def test_account_info_with_malformed_signerlists_and_api_version_2(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)
    account_2 = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": account_1.account_id,
            "SignerQuorum": 2,
            "SignerEntries": [
                {
                    "SignerEntry": {
                        "Account": account_2.account_id,
                        "SignerWeight": 2
                    }
                }
            ],
        },
        "secret": account_1.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2])

    response = rippled_server.get_account_info(account_1.account_id, signer_lists="fgh", queue=False,
                                               ledger_index="validated", api_version=2)
    test_validator.verify_test(rippled_server, response, accounts=[account_1, account_2], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, signer_lists="fgh", queue=False,
                                                 ledger_index="validated", api_version=2)
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1, account_2], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_strict_false(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_1.account_id, strict=False, queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, strict=False, queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def test_account_info_with_malformed_strict(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    account_1 = rippled_server.create_account(fund=True)

    response = rippled_server.get_account_info(account_1.account_id, strict="fgh", queue=False,
                                               ledger_index="validated")
    test_validator.verify_test(rippled_server, response, accounts=[account_1], method="account_info")

    clio_response = clio_server.get_account_info(account_1.account_id, strict="fgh", queue=False,
                                                 ledger_index="validated")
    test_validator.verify_test(clio_server, clio_response, accounts=[account_1], method="account_info")

    assert helper.compare_dict(response, clio_response,
                               ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
