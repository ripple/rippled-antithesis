import pytest

from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper, test_validator, helper
from . import price_oracle_test_data as test_data
from .. import constants

log = log_helper.get_logger()


@pytest.mark.smoke
def test_create_oracle(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that the computed AssetPrice is correct.
    computed_asset_price = str(hex(test_data.DEFAULT_ASSET_PRICE).split('x')[-1])
    assert response['tx_json']['PriceDataSeries'][0]['PriceData']['AssetPrice'] == computed_asset_price, "Computed AssetPrice is incorrect"


def test_create_oracle_for_same_token_pair_under_different_accounts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    bob = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": bob.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": bob.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[bob])


def test_create_oracle_with_invalid_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "InvalidField": "InvalidValue"
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_account_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActMissing")


def test_create_oracle_without_asset_class_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_without_last_updated_time_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_oracle_document_id_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_price_data_series_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_asset_price_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                    "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_without_base_asset_price_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                    "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_quote_asset_price_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [{
                "PriceData": {
                    "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                    "BaseAsset": test_data.DEFAULT_BASE_ASSET
                }
            }],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_without_provider_field(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


@pytest.mark.parametrize("price_data_series", ["", 1, "Invalid", ([{}]), [{"PriceDataSeries": ""}]])
def test_create_oracle_invalid_price_data_series_inputs(fx_rippled, price_data_series):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": price_data_series,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("price_data_series", [None, ([])])
def test_create_oracle_empty_price_data_series_inputs(fx_rippled, price_data_series):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": price_data_series,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temARRAY_EMPTY")


@pytest.mark.parametrize("price_data_series", [test_data.DUPLICATE_PRICE_DATA_1,
                                               test_data.DUPLICATE_PRICE_DATA_2,
                                               test_data.DUPLICATE_PRICE_DATA_3,
                                               test_data.DUPLICATE_PRICE_DATA_4,
                                               test_data.SAME_BASE_QUOTE_ASSETS_PRICE_DATA_1,
                                               test_data.SAME_BASE_QUOTE_ASSETS_PRICE_DATA_2])
def test_create_oracle_malformed_price_data_series_inputs(fx_rippled, price_data_series):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": price_data_series,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_with_ten_price_data_entries(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_TEN_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_create_oracle_with_eleven_price_data_entries(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ELEVEN_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temARRAY_TOO_LARGE")


def test_create_oracle_with_five_price_data_entries_with_insufficient_reserves(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True,
                                          amount=str(int(constants.BASE_RESERVE) + int(constants.OWNER_RESERVE) - int(constants.DEFAULT_TRANSFER_AMOUNT)))
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_FIVE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINSUFFICIENT_RESERVE")


def test_create_oracle_with_six_price_data_entries_with_insufficient_reserves(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True,
                                          amount=str(int(constants.BASE_RESERVE) + (2 * int(constants.OWNER_RESERVE)) - int(constants.DEFAULT_TRANSFER_AMOUNT)))
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_SIX_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice],
                               response_result="tecINSUFFICIENT_RESERVE")


@pytest.mark.parametrize("account", [None, "", 123, "InvalidAccountAddress"])
def test_create_oracle_malformed_account_inputs(fx_rippled, account):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": account,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="srcActMalformed")


@pytest.mark.parametrize("last_updated_time", [None, "", "Invalid", -1, 1.2])
def test_create_oracle_invalid_last_updated_time_inputs(fx_rippled, last_updated_time):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": last_updated_time,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_incorrect_last_updated_time(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": 123,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINVALID_UPDATE_TIME")


def test_create_oracle_incorrect_future_last_updated_time(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time() + 400,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINVALID_UPDATE_TIME")


def test_create_oracle_incorrect_past_last_updated_time(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time() - 400,
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="tecINVALID_UPDATE_TIME")


@pytest.mark.parametrize("oracle_document_id", [None, "", "Invalid", -1, 1.2])
def test_create_oracle_invalid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": oracle_document_id,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("oracle_document_id", ["1", 0])
def test_create_oracle_valid_oracle_document_id_inputs(fx_rippled, oracle_document_id):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": oracle_document_id,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.parametrize("base_asset", [None, "Invalid", 123, -1, 0, 1.2, test_data.INVALID_NON_STANDARD_CURRENCY_CODE, "H", "HB", "HBAR"])
def test_create_oracle_invalid_base_asset_inputs_with_scale(fx_rippled, base_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": base_asset,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("base_asset", ["", test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_create_oracle_valid_base_asset_inputs_with_scale(fx_rippled, base_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": base_asset,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that empty BaseAsset gets set to XRP by default. 
    if base_asset == "":
        assert response['tx_json']['PriceDataSeries'][0]['PriceData']['BaseAsset'] == "XRP", "BaseAsset set to empty string did not default to XRP"


@pytest.mark.parametrize("quote_asset",
                         [None, "Invalid", 123, -1, 0, 1.2, test_data.INVALID_NON_STANDARD_CURRENCY_CODE,
                          "H", "HB", "HBAR"])
def test_create_oracle_invalid_quote_asset_inputs_with_scale(fx_rippled, quote_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": quote_asset,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("quote_asset", ["", test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_create_oracle_valid_quote_asset_inputs_with_scale(fx_rippled, quote_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": quote_asset,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that empty QuoteAsset gets set to XRP by default. 
    if quote_asset == "":
        assert response['tx_json']['PriceDataSeries'][0]['PriceData']['QuoteAsset'] == "XRP", "QuoteAsset set to empty string did not default to XRP"


@pytest.mark.parametrize("asset_price", [None, "", -1, 1.2, "gh123"])
def test_create_oracle_invalid_asset_price_inputs_with_scale(fx_rippled, asset_price):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": asset_price,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("asset_price", [0, 123, "abc123"])
def test_create_oracle_valid_asset_price_inputs_with_scale(fx_rippled, asset_price):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": asset_price,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.parametrize("base_asset", [None, "Invalid", 123, -1, 0, test_data.INVALID_NON_STANDARD_CURRENCY_CODE, "H", "HB", "HBAR"])
def test_create_oracle_invalid_base_asset_inputs_without_scale(fx_rippled, base_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": base_asset,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("base_asset", ["", test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_create_oracle_valid_base_asset_inputs_without_scale(fx_rippled, base_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": base_asset,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that empty BaseAsset gets set to XRP by default. 
    if base_asset == "":
        assert response['tx_json']['PriceDataSeries'][0]['PriceData']['BaseAsset'] == "XRP", "BaseAsset set to empty string did not default to XRP"


@pytest.mark.parametrize("quote_asset", [None, "Invalid", 123, -1, 0, 1.2, test_data.INVALID_NON_STANDARD_CURRENCY_CODE, "H", "HB", "HBAR"])
def test_create_oracle_invalid_quote_asset_inputs_without_scale(fx_rippled, quote_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": quote_asset
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("quote_asset", ["", test_data.VALID_NON_STANDARD_CURRENCY_CODE, "HBA"])
def test_create_oracle_valid_quote_asset_inputs_without_scale(fx_rippled, quote_asset):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": quote_asset
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that empty QuoteAsset gets set to XRP by default.
    if quote_asset == "":
        assert response['tx_json']['PriceDataSeries'][0]['PriceData']['QuoteAsset'] == "XRP", "QuoteAsset set to empty string did not default to XRP"


@pytest.mark.parametrize("asset_price", [None, "", -1, 1.2, "gh123"])
def test_create_oracle_invalid_asset_price_inputs_without_scale(fx_rippled, asset_price):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": asset_price,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("asset_price", [0, 123, "abc123"])
def test_create_oracle_valid_asset_price_inputs_without_scale(fx_rippled, asset_price):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": asset_price,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.parametrize("scale", [None, "", 0, -1, "Invalid", 1.2])
def test_create_oracle_invalid_scale_inputs(fx_rippled, scale):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": scale
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_malformed_scale_inputs(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": 21
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


@pytest.mark.parametrize("scale", [1, 20])
def test_create_oracle_valid_scale_inputs(fx_rippled, scale):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": test_data.DEFAULT_QUOTE_ASSET,
                        "Scale": scale
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_create_oracle_with_invalid_int_transaction_type(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": 123,
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result='internal')


def test_create_oracle_with_invalid_str_transaction_type(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "InvalidEntryShouldFail",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result='invalidParams')


def test_create_oracle_with_using_invalid_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=False)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result='srcActNotFound')


@pytest.mark.parametrize("provider", [None, 0, -1, 1, 1.2, "Invalid"])
def test_create_oracle_invalid_provider_inputs(fx_rippled, provider):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": provider
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_invalid_provider_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.INVALID_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_malformed_provider_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_valid_provider_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.VALID_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    # Verify that provider information is contained within the response.
    assert payload['tx_json']['Provider'].upper() in response['tx_json']['Provider'], "Provider field does not match between request payload and response"


@pytest.mark.parametrize("uri", [None, 0, -1, 1, 1.2, "Invalid"])
def test_create_oracle_invalid_uri_inputs(fx_rippled, uri):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "URI": uri
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_invalid_uri_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "URI": test_data.INVALID_URI
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


def test_create_oracle_malformed_uri_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "URI": ""
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_valid_uri_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "URI": test_data.VALID_URI
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.parametrize("asset_class", [None, 0, -1, 1, 1.2, "Invalid"])
def test_create_oracle_invalid_asset_class_inputs(fx_rippled, asset_class):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": asset_class,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="invalidParams")


@pytest.mark.parametrize("asset_class", [test_data.INVALID_ASSET_CLASS, ""])
def test_create_oracle_malformed_asset_class_input(fx_rippled, asset_class):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": asset_class,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="temMALFORMED")


def test_create_oracle_valid_asset_class_input(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.VALID_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_create_oracle_multisigned(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    carol = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "Account": alice.account_id,
            "TransactionType": "SignerListSet",
            "SignerQuorum": 1,
            "SignerEntries": [
                {
                    "SignerEntry":
                        {
                            "Account": carol.account_id,
                            "SignerWeight": 1
                        }
                }
            ]
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    assert rippled_server.verify_signer_list(response)

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": [
                {
                    "PriceData": {
                        "AssetPrice": test_data.DEFAULT_ASSET_PRICE,
                        "BaseAsset": test_data.DEFAULT_BASE_ASSET,
                        "QuoteAsset": "USD",
                        "Scale": test_data.DEFAULT_SCALE
                    }
                }
            ],
            "Provider": test_data.DEFAULT_PROVIDER,
            "SigningPubKey": "",
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "account": carol.account_id,
        "secret": carol.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload, method="sign_for")
    multi_signed_response = rippled_server.execute_transaction(payload=response, method="submit_multisigned")
    test_validator.verify_test(rippled_server, multi_signed_response, accounts=[alice])


def test_create_oracle_with_regular_key_when_master_key_disabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    rippled_server.add_regular_key_to_account(alice)  # Generate regular key
    rippled_server.disable_master_key(alice)  # Disable master key

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.regular_key_seed
    }
    response = rippled_server.execute_transaction(payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


@pytest.mark.longrun
def test_create_oracle_and_delete_account(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])
    rippled_server.wait_for_ledger_to_advance_for_account_delete(alice)
    bob = rippled_server.create_account(fund=True)

    # Delete source account
    payload = {
        "tx_json": {
            "TransactionType": "AccountDelete",
            "Account": alice.account_id,
            "Destination": bob.account_id,
            "Fee": constants.DEFAULT_DELETE_ACCOUNT_FEE,
            "Sequence": rippled_server.get_account_sequence(alice),
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice, bob])

    response = rippled_server.get_price_oracle(alice.account_id, test_data.DEFAULT_ORACLE_DOCUMENT_ID)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="entryNotFound")

    response = rippled_server.get_account_info(alice.account_id)
    test_validator.verify_test(rippled_server, response, accounts=[alice], response_result="actNotFound")


def test_create_oracle_on_account_with_deposit_auth_enabled(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)

    # Set deposit auth
    rippled_server.enable_deposit_auth(account_object=alice)

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])


def test_create_oracle_on_ticket(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]

    alice = rippled_server.create_account(fund=True)
    payload = {
        "tx_json": {
            "TransactionType": "TicketCreate",
            "Account": alice.account_id,
            "Sequence": rippled_server.get_account_sequence(alice),
            "TicketCount": 1
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])

    payload = {
        "tx_json": {
            "TransactionType": "OracleSet",
            "Account": alice.account_id,
            "AssetClass": test_data.DEFAULT_ASSET_CLASS,
            "LastUpdateTime": helper.get_unix_epoch_time(),
            "OracleDocumentID": test_data.DEFAULT_ORACLE_DOCUMENT_ID,
            "PriceDataSeries": test_data.DEFAULT_ONE_ENTRY_PRICE_DATA,
            "Provider": test_data.DEFAULT_PROVIDER,
            "TicketSequence": rippled_server.get_ticket_sequence(alice)[0]
        },
        "secret": alice.master_seed
    }
    response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, response, accounts=[alice])
