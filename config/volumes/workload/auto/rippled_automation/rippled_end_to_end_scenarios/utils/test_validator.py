import time

from rippled_automation.rippled_end_to_end_scenarios.utils import helper, log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils.amm import amm_validator
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

log = log_helper.get_logger()


def validate_account_balance(rippled_server, accounts, can_have_deleted_account=False, verbose=False):
    """
        Compares the account object acting in the test to state of account on xrpl
    """
    log.info("")
    log.info("Validate account balance...")

    if not skip_account_balance_validation(rippled_server, accounts):
        for account_object in accounts:
            ledger_account_balance = int(rippled_server.get_account_balance(account_object.account_id, verbose=verbose))
            xrp_balance = rippled_server.get_xrp_balance(account_object.account_id)
            if ledger_account_balance != int(constants.NON_FUNDED_ACCOUNT_BALANCE):
                log.info("  '{}': {} (ledger: {})".format(account_object.account_id, xrp_balance, ledger_account_balance))
                assert xrp_balance == ledger_account_balance, "Account balance mismatch"
            else:
                assert can_have_deleted_account, "'{}' is not created/funded".format(account_object.account_id)
                log.info("  '{}': Non existent (non funded)/deleted account".format(account_object.account_id))

        log.info("Account balances validated successfully")


def skip_account_balance_validation(rippled_server, accounts):
    skip_validation = False
    if not rippled_server.standalone_mode:
        for account_object in accounts:
            if account_object in rippled_server.reward_accounts.values():
                skip_validation = True
            else:
                skip_validation = False
                break

    if skip_validation:
        log.info("  Skipped reward accounts (network mode)")
    return skip_validation


def validate_ledger_data_with_type(response, ledger_data_type):
    if response["state"]:
        for value in response["state"]:
            log.debug(value)
            assert value["LedgerEntryType"] == ledger_data_type, "ledger_data of type other than {} found in {}".format(
                ledger_data_type, response)
    else:
        log.info("No entries for {} found in the response".format(ledger_data_type))


def verify_transaction(rippled_server, response, engine_result="tesSUCCESS"):
    log.info("")
    log.info("Verify transaction...")
    skipped = False

    if "error" in response:
        assert response["error"] == engine_result
    elif "engine_result" in response:
        if response["engine_result"] == "tesSUCCESS" or response["engine_result"] == "terQUEUED":
            assert rippled_server.is_transaction_validated(response, engine_result=engine_result, verbose=False), \
                f"Expected result '{engine_result}' does not match response " + response["engine_result"]
        else:
            assert response["engine_result"] == engine_result, \
                f"Expected result '{engine_result}' does not match response " + response["engine_result"]
    elif "status" in response:
        log.info("Validating non submit transaction")
        if engine_result == "tesSUCCESS":
            engine_result = "success"  # Default status as success
        assert response["status"] == engine_result, \
            f"Expected result '{engine_result}' does not match response " + response["status"]
    else:
        log.info("  Skipped")
        skipped = True
    if not skipped:
        log.info("  successful")


def verify_rippled_method_objects(response, method, ignore_account_objects=False, verbose=False):
    object_verified = False

    # public method validations
    error_status = False
    try:
        if response["error"]:
            error_status = True
    except KeyError:
        pass

    if error_status:
        log.debug("Ignoring account_objects due to error in response")
    else:
        if method == "account_channels":
            assert response["channels"], "Channels not found: {}".format(response)
            assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            if "limit" in response:
                assert len(response["channels"]) <= response["limit"], "limit value mismatched"
            object_verified = True
        elif method == "account_currencies":
            assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            assert response["send_currencies"], "Currencies not found: {}".format(response)
            object_verified = True
        elif method == "account_info":
            try:
                assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["account_data"], "account_data not found: {}".format(response)
            object_verified = True
        elif method == "nft_info":
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            assert response["nft_id"], "nft_id not found: {}".format(response)
            assert response["owner"], "owner not found: {}".format(response)
            assert response["is_burned"] is not None, "is_burned not found: {}".format(response)
            assert response["flags"] is not None, "flags not found: {}".format(response)
            assert response["transfer_fee"] is not None, "transfer_fee not found: {}".format(response)
            assert response["issuer"], "issuer not found: {}".format(response)
            assert response["nft_taxon"] is not None, "nft_taxon not found: {}".format(response)
            assert response["nft_serial"] is not None, "nft_serial not found: {}".format(response)
            object_verified = True
        elif method == "nfts_by_issuer":
            assert response["issuer"], "issuer not found: {}".format(response)
            assert response["nfts"], "nfts not found: {}".format(response)
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            object_verified = True
        elif method == "account_lines":
            try:
                assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
                assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["lines"], "lines not found: {}".format(response)
            if "limit" in response:
                assert len(response["lines"]) <= response["limit"], "limit value mismatched"
            object_verified = True
        elif method == "account_objects":
            try:
                assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["account_objects"], "account_objects not found: {}".format(response)
            if "limit" in response:
                assert len(response["account_objects"]) <= response["limit"], "limit value mismatched"
            object_verified = True
        elif method == "account_offers":
            try:
                assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
                assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["offers"], "offers not found: {}".format(response)
            if "limit" in response:
                assert len(response["offers"]) <= response["limit"], "limit value mismatched"
            object_verified = True
        elif method == "account_tx":
            assert response["transactions"], "transactions not found: {}".format(response)
            object_verified = True
        elif method == "account_nfts":
            assert response["account_nfts"], "account_nfts not found: {}".format(response)
            object_verified = True
        elif method == "nft_sell_offers":
            assert response["offers"], "NFT offers not found: {}".format(response)
            object_verified = True
        elif method == "nft_buy_offers":
            assert response["offers"], "NFT offers not found: {}".format(response)
            object_verified = True
        elif method == "nft_history":
            assert response["nft_id"], "NFT id not found: {}".format(response)
            assert response["ledger_index_min"], "ledger_index_min not found: {}".format(response)
            assert response["ledger_index_max"], "ledger_index_max not found: {}".format(response)
            object_verified = True
        elif method == "gateway_balances":
            assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            object_verified = True
        elif method == "noripple_check":
            try:
                assert response["ledger_current_index"], "ledger_index not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            object_verified = True
        elif method == "ledger":
            if "closed" and "open" in response:
                assert response["closed"]["ledger"], "ledger not found: {}".format(response)
                assert response["open"]["ledger"], "ledger not found: {}".format(response)
            else:
                assert response["ledger"], "ledger not found: {}".format(response)
                assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            object_verified = True
        elif method == "ledger_closed":
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            object_verified = True
        elif method == "ledger_current":
            assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
            object_verified = True
        elif method == "ledger_data":
            assert response["state"] is not None, "state not found: {}".format(response)
            object_verified = True
        elif method == "ledger_entry":
            assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
            assert response["ledger_index"], "ledger_index not found: {}".format(response)
            assert response["node"], "node not found: {}".format(response)
            object_verified = True
        elif method == "transaction_entry":
            try:
                assert response["delivered_amount"], "delivered_amount not found: {}".format(response)
                assert response["metadata"], "metadata not found: {}".format(response)
                assert response["meta"], "meta not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            object_verified = True
        elif method == "tx":
            try:
                assert response["meta"], "meta not found: {}".format(response)
                assert response["meta_blob"], "meta not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["ctid"], "ctid not found: {}".format(response)
            object_verified = True
        elif method == "tx_history":
            assert response["txs"], "txs not found: {}".format(response)
            object_verified = True
        elif method == "book_offers":
            try:
                assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
                assert response["ledger_hash"], "ledger_hash not found: {}".format(response)
                assert response["ledger_index"], "ledger_index not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            assert response["offers"], "offers not found: {}".format(response)
            if "limit" in response:
                assert len(response["offers"]) <= response["limit"], "limit value mismatched"
            object_verified = True
        elif method == "deposit_authorized":
            assert response["deposit_authorized"], "deposit_authorized not found: {}".format(response)
            object_verified = True
        elif method == "ripple_path_find":
            assert response["alternatives"], "alternatives not found: {}".format(response)
            object_verified = True
        elif method == "channel_authorize":
            assert response["signature"], "signature not found: {}".format(response)
            object_verified = True
        elif method == "channel_verify":
            assert response["signature_verified"], "signature_verified: {}".format(response)
            object_verified = True
        elif method == "fee":
            assert response["expected_ledger_size"], "expected_ledger_size not found: {}".format(response)
            assert response["ledger_current_index"], "ledger_current_index not found: {}".format(response)
            assert response["max_queue_size"], "max_queue_size not found: {}".format(response)
            assert response["drops"], "drops not found: {}".format(response)
            object_verified = True
        elif method == "manifest":
            assert response["status"] == "success", "Error fetching manifest: {}".format(response)
            object_verified = True
        elif method == "server_info":
            assert response["info"], "info not found: {}".format(response["info"])
            assert response["info"]["complete_ledgers"], "complete_ledgers not found: {}".format(response)
            assert response["info"]["validated_ledger"], "validated_ledger not found: {}".format(response)
            assert response["info"]["validation_quorum"], "validation_quorum not found: {}".format(response)
            assert response["info"]["load_factor"], "load_factor not found: {}".format(response)
            try:
                assert response["info"]["build_version"], "rippled version not found: {}".format(response)
                assert response["info"]["rippled_version"], "clio rippled version not found: {}".format(response)
                assert response["info"]["clio_version"], "clio version not found: {}".format(response)
            except KeyError as e:
                log.info(e)
            object_verified = True
        elif method == "server_state":
            assert response["state"], "state not found: {}".format(response)
            object_verified = True
        elif method == "ping":
            assert response["status"] == "success", "status: {}".format(response)
            object_verified = True
        elif method == "random":
            assert response["random"], "random not found: {}".format(response)
            object_verified = True
        elif method == "witness":
            assert response, "Witness response is empty"
            assert response["Signature"] is not None, "Signature not found: {}".format(response)
            assert response["XChainClaimID"] is not None, "XChainClaimID not found: {}".format(response)
            object_verified = True

        elif method == "witness_account_create":
            assert response, "Witness response is empty"
            assert response["Signature"] is not None, "Signature not found: {}".format(response)
            assert response["XChainAccountCreateCount"] is not None, "XChainAccountCreateCount not found: {}".format(
                response)
            object_verified = True

        elif method == "amm_info":
            amm_info = response['amm']
            for key in ['account', 'amount', 'amount2',
                        'asset2_frozen', 'auction_slot',
                        'lp_token', 'trading_fee', 'vote_slots']:
                assert str(amm_info[key]), f"{key} not found"

            assert 0 <= int(amm_info['trading_fee']) <= int(constants.MAX_AMM_TRADING_FEE), f"Trading fee outside allowed range 0 to {constants.MAX_AMM_TRADING_FEE}"
            object_verified = True

        elif method == "deposit_authorized":
            assert response["deposit_authorized"] is not None, "deposit_authorized not found: {}".format(response)
            assert response["destination_account"], "destination_account not found: {}".format(response)
            assert response["source_account"], "max_queue_size not found: {}".format(response)

        # admin method validations
        elif method == "validation_create":
            assert response["validation_key"], "validation_key not found: {}".format(response)
            assert response["validation_seed"], "validation_seed not found: {}".format(response)
            assert response["validation_public_key"], "validation_public_key not found: {}".format(response)
            object_verified = True
        elif method == "wallet_propose":
            assert response["account_id"], "account_id not found: {}".format(response)
            assert response["master_seed"], "master_seed not found: {}".format(response)
            assert response["public_key"], "public_key not found: {}".format(response)
            object_verified = True
        elif method == "can_delete":
            advisory_delete_value = helper.get_config_value(section="node_db", key="advisory_delete")
            online_delete_value = helper.get_config_value(section="node_db", key="online_delete")
            if advisory_delete_value == "1" and online_delete_value is not None:
                assert response["can_delete"], "can_delete not found: {}".format(response)
                object_verified = True
            else:
                assert response["error"] == "notEnabled", "{} found".format(response)
                object_verified = True
        elif method == "crawl_shards":
            assert response["complete_shards"], "complete_shards not found: {}".format(response)
            assert response["peers"], "peers not found: {}".format(response)
            object_verified = True
        elif method == "download_shard":
            assert response["message"], "message not found: {}".format(response)
            object_verified = True
        elif method == "node_to_shard":
            assert response["message"], "message not found: {}".format(response)
            object_verified = True
        elif method == "connect":
            assert response["message"].startswith(("connecting", "attempting connection to")) and response[
                "status"] == "success", "message: {}".format(response)
            object_verified = True
        elif method == "peer_reservations_add":
            assert response["status"] == "success", "status: {}".format(response)
            object_verified = True
        elif method == "peer_reservations_list":
            assert "reservations" in response, "reservations: {}".format(response)
            object_verified = True
        elif method == "peer_reservations_del":
            assert "previous" in response, "previous: {}".format(response)
            object_verified = True
        elif method == "consensus_info":
            assert response["info"]["peer_positions"], "peer_positions not found: {}".format(response)
            object_verified = True
        elif method == "feature":
            assert response["status"] == "success", "status: {}".format(response)
            object_verified = True
        elif method == "fetch_info":
            assert response["info"], "info not found: {}".format(response)
            object_verified = True
        elif method == "get_counts":
            assert response["uptime"], "uptime not found: {}".format(response)
            object_verified = True
        elif method == "validator_list_sites":
            assert response["validator_sites"], "validator_sites not found: {}".format(response)
            object_verified = True
        elif method == "validators":
            assert response["publisher_lists"], "publisher_lists not found: {}".format(response)
            object_verified = True
        elif method == "get_aggregate_price":
            assert 'ledger_current_index' in response, f"ledger_current_index field not found: {response}"
            assert 'median' in response, f"median field not found: {response}"
            assert 'status' in response, f"status field not found: {response}"
            assert 'time' in response, f"time field not found: {response}"
            assert 'validated' in response, f"validated field not found: {response}"
            assert 'mean' in response["entire_set"], f"mean field not found in entire_set: {response}"
            assert 'size' in response["entire_set"], f"size field not found in entire_set: {response}"
            assert 'standard_deviation' in response["entire_set"], f"standard_deviation field not found in entire_set: {response}"
            if "trimmed_set" in response:
                assert 'mean' in response["trimmed_set"], f"mean field not found in trimmed_set: {response}"
                assert 'size' in response["trimmed_set"], f"size field not found in trimmed_set: {response}"
                assert 'standard_deviation' in response["trimmed_set"], f"standard_deviation field not found in trimmed_set: {response}"
            object_verified = True

        assert object_verified, "objects not verified"
        log.info("  objects verified")


def verify_account_objects(rippled_server, response, response_result="tesSUCCESS", offer_crossing=None,
                           offer_cancelled=None, ignore_account_objects=False, method=None, verbose=False):
    perform_account_object_verification = True
    log.debug("Response to verify: {}".format(response))

    if response == constants.SIDECHAIN_IGNORE_VALIDATION:
        log.debug(constants.SIDECHAIN_IGNORE_VALIDATION)
        return

    if method:
        log.info("")
        log.info("Verifying objects for public/admin methods...")
        verify_rippled_method_objects(response, method, ignore_account_objects=ignore_account_objects, verbose=verbose)
    else:
        if "engine_result_code" in response and response["engine_result_code"] != 0:
            perform_account_object_verification = False
        elif response["status"] != "success" or "tx_json" not in response:
            perform_account_object_verification = False

        if perform_account_object_verification:
            transaction_type = response["tx_json"]["TransactionType"]
            log.debug("TransactionType: {}".format(transaction_type))
            account_id = response["tx_json"]["Account"]
            log.info("")
            log.info("Verifying account objects...")

            if transaction_type in constants.transactions["CREATING_OBJECTS"]:
                log.debug("Verifying if objects are present...")
                assert rippled_server.is_transaction_validated(response, engine_result=response_result,
                                                               verbose=verbose), "Transaction not validated"
                account_objects = []
                token_id = None
                offer_crossing_status = None
                nft_account_objects = []

                hash_from_previous_txn = response["tx_json"]["hash"]
                if transaction_type == "NFTokenMint":
                    account_objects_response = rippled_server.get_account_objects(account_id, verbose=verbose)["account_objects"]
                    log.debug("Verifying account_object for NFTokenMint")

                    for account_object in account_objects_response:
                        if account_object["LedgerEntryType"] == "NFTokenPage":
                            for NFToken in account_object["NFTokens"]:
                                nft_account_objects.append(NFToken["NFToken"]["NFTokenID"])

                    nft_tokens = rippled_server.get_nft_tokens(account_id, verbose=verbose)
                    assert nft_tokens, "nft_tokens not found"

                    non_fungible_tokens = []
                    tx_response = rippled_server.tx(hash_from_previous_txn, verbose=False)
                    for affected_node in tx_response["meta"]["AffectedNodes"]:
                        log.debug("Parsing affected node: {}...".format(affected_node))
                        try:
                            if "CreatedNode" in affected_node and affected_node["CreatedNode"]["LedgerEntryType"] == "NFTokenPage":
                                non_fungible_tokens_object = affected_node["CreatedNode"]["NewFields"]["NFTokens"]
                                log.debug("New NFToken object created: {}".format(non_fungible_tokens_object))
                                log.debug("# of objects from CreatedNode: {}".format(len(non_fungible_tokens_object)))
                                assert len(non_fungible_tokens_object) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, \
                                    "NFToken page objects more than {} [{}]".format(
                                        constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT,
                                        len(non_fungible_tokens_object))

                                for item in non_fungible_tokens_object:
                                    non_fungible_token = item["NFToken"]["NFTokenID"]
                                    log.debug("Non Fungible Token from object: {}".format(non_fungible_token))
                                    non_fungible_tokens.append(non_fungible_token)

                            if "ModifiedNode" in affected_node and affected_node["ModifiedNode"]["LedgerEntryType"] == "NFTokenPage":
                                non_fungible_tokens_object = affected_node["ModifiedNode"]["FinalFields"]["NFTokens"]
                                log.debug("NFToken object added & modified: {}".format(non_fungible_tokens_object))
                                log.debug("No. of objects from ModifiedNode: {}".format(len(non_fungible_tokens_object)))
                                assert len(non_fungible_tokens_object) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, \
                                    "NFToken page objects more than {} [{}]".format(
                                        constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT,
                                        len(non_fungible_tokens_object))

                                for item in non_fungible_tokens_object:
                                    non_fungible_token = item["NFToken"]["NFTokenID"]
                                    log.debug("Non Fungible Token from object: {}".format(non_fungible_token))
                                    non_fungible_tokens.append(non_fungible_token)

                        except KeyError as e:
                            pass

                    log.debug("Total # of objects (non_fungible_tokens): {}".format(non_fungible_tokens))
                    log.debug("No. of non_fungible_tokens: {}".format(len(non_fungible_tokens)))
                    log.debug("No. of nft_tokens: {}".format(len(nft_tokens)))
                    if len(nft_tokens) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT:
                        assert set(non_fungible_tokens) == set(nft_tokens), "Non Fungible Token object count mismatch"

                    assert tx_response["meta"]["nftoken_id"] in non_fungible_tokens, \
                        "`nftoken_id` not found in NFTokenMint transaction"
                    log.debug("**** verified: {}".format(tx_response["meta"]["nftoken_id"]))

                elif transaction_type == "OracleSet":
                    account_objects_response = rippled_server.get_account_objects(account_id, verbose=verbose)["account_objects"]
                    assert len(account_objects_response) > 0, "No account objects were created for OracleSet"
                    assert 'OracleDocumentID' in response['tx_json'], "OracleDocumentID field not found in the response"
                    oracle_document_id = response['tx_json']['OracleDocumentID']
                    get_price_oracle_response = rippled_server.get_price_oracle(account_id, oracle_document_id, verbose=verbose)
                    oracle_found = False
                    for account_object in account_objects_response:
                        if account_object["LedgerEntryType"] == "Oracle":
                            oracle_found = True
                            assert hash_from_previous_txn == account_object["PreviousTxnID"], "PreviousTxnID does not match between response and account object"
                            assert response['tx_json']['Sequence'] + 1 <= account_object['PreviousTxnLgrSeq'], "PreviousTxnLgrSeq does not match between response and account object"

                            assert 'Account' in response['tx_json'], "Account field not found in the response"
                            assert response['tx_json']['Account'] == account_object['Owner'], "Account field does not match between response and account object"
                            assert response['tx_json']['Account'] == get_price_oracle_response['node']['Owner'], "Account field does not match between response and price oracle object"

                            tx_response = rippled_server.tx(hash_from_previous_txn, verbose=False)
                            for affected_node in tx_response["meta"]["AffectedNodes"]:
                                if "CreatedNode" in affected_node and affected_node['CreatedNode']['LedgerEntryType'] == 'Oracle':
                                    assert affected_node['CreatedNode']['NewFields']['PriceDataSeries'] == response['tx_json'][
                                        'PriceDataSeries'], "PriceDataSeries does not match"

                            for param in constants.PRICE_ORACLE_ACCOUNT_OBJECT_PARAMS:
                                if param in response["tx_json"] and response["tx_json"][param]:
                                    assert response["tx_json"][param] == account_object[param], f"Mismatch in account object param: '{param}'"
                                    assert response["tx_json"][param] == get_price_oracle_response['node'][param], f"Mismatch in GET price oracle response param: '{param}'"

                    assert oracle_found, "No Price Oracle was found"

                elif transaction_type == "NFTokenCreateOffer":
                    tx_response = rippled_server.tx(hash_from_previous_txn, verbose=False)
                    for affected_node in tx_response["meta"]["AffectedNodes"]:
                        log.debug("Parsing affected node: {}...".format(affected_node))
                        try:
                            if "CreatedNode" in affected_node and affected_node["CreatedNode"]["LedgerEntryType"] == "NFTokenOffer":
                                token_id = affected_node["CreatedNode"]["NewFields"]["NFTokenID"]
                                log.debug("New Token ID created: {}".format(token_id))
                                break
                        except KeyError as e:
                            pass
                    assert token_id, "Token ID not created"
                    assert tx_response["meta"]["offer_id"], "`offer_id` not found in NFTokenCreateOffer transaction"
                    log.debug("**** verified: {}".format(tx_response["meta"]["offer_id"]))

                    if "Owner" in response["tx_json"]:  # Buy offer
                        log.debug("  Not validating nft_tokens as this is a buy order")
                    else:
                        log.debug("Validating nft_tokens as this is a sell order")
                        nft_tokens = rippled_server.get_nft_tokens(account_id, verbose=verbose)
                        assert token_id in nft_tokens, "Token ID '{}' not found in NFToken: {}".format(token_id, nft_tokens)

                elif transaction_type == "NFTokenAcceptOffer":
                    old_owner = None
                    new_owner = None
                    ledger_index_buy_offer = None
                    ledger_index_sell_offer = None
                    broker_mode = False
                    if "NFTokenBuyOffer" in response["tx_json"]:  # Buy NFT offer
                        log.debug("  Buy NFT order")
                        ledger_index_buy_offer = response["tx_json"]["NFTokenBuyOffer"]
                    if "NFTokenSellOffer" in response["tx_json"]:  # Sell NFT offer
                        log.debug("  Sell NFT offer")
                        ledger_index_sell_offer = response["tx_json"]["NFTokenSellOffer"]
                    if ledger_index_buy_offer and ledger_index_sell_offer:
                        log.info("  ** Broker deal **")
                        broker_mode = True

                    tx_response = rippled_server.tx(hash_from_previous_txn, verbose=False)
                    for affected_node in tx_response["meta"]["AffectedNodes"]:
                        log.debug("Parsing affected node: {}...".format(affected_node))
                        ledger_index = None
                        try:
                            if "DeletedNode" in affected_node and \
                                    affected_node["DeletedNode"]["LedgerEntryType"] == "NFTokenOffer":
                                if affected_node["DeletedNode"]["FinalFields"]["Flags"] == 1:  # Sell NFT offer
                                    log.debug("  sell NFT offer")
                                    ledger_index = ledger_index_sell_offer

                                    old_owner = affected_node["DeletedNode"]["FinalFields"]["Owner"]
                                    assert old_owner, "Old Owner not found"

                                if affected_node["DeletedNode"]["FinalFields"]["Flags"] == 0:  # buy NFT offer
                                    log.debug("  buy NFT offer")
                                    ledger_index = ledger_index_buy_offer

                                    new_owner = affected_node["DeletedNode"]["FinalFields"]["Owner"]
                                    assert new_owner, "New Owner not found"

                                log.debug("Deleted Ledger Index: {}".format(ledger_index))
                                assert affected_node["DeletedNode"]["LedgerIndex"] == ledger_index, \
                                    "Ledger Index {} not found".format(ledger_index)

                                token_id = affected_node["DeletedNode"]["FinalFields"]["NFTokenID"]
                                assert tx_response["meta"]["nftoken_id"] == token_id, \
                                    "`nftoken_id` not found in NFTokenAcceptOffer transaction"
                                log.debug("**** verified: {}".format(tx_response["meta"]["nftoken_id"]))

                        except KeyError as e:
                            pass

                    if ledger_index_sell_offer:
                        assert ledger_index_sell_offer, "Ledger Index not deleted"
                    if ledger_index_buy_offer:
                        assert ledger_index_buy_offer, "Ledger Index not deleted"

                    if "NFTokenBuyOffer" in response["tx_json"]:  # Buy offer
                        log.debug("  Validating nft_tokens for buy offer")
                        if not broker_mode:
                            old_owner = account_id

                        nft_tokens = rippled_server.get_nft_tokens(old_owner, verbose=verbose)
                        assert token_id not in nft_tokens, "Token ID '{}' found in NFToken: {}".format(token_id, nft_tokens)

                        nft_tokens = rippled_server.get_nft_tokens(new_owner, verbose=verbose)
                        assert token_id in nft_tokens, "Token ID '{}' not found in NFToken: {}".format(token_id, nft_tokens)

                    if "NFTokenSellOffer" in response["tx_json"]:  # Sell offer
                        log.debug("  Validating nft_tokens for sell offer")
                        if not broker_mode:
                            new_owner = account_id

                        nft_tokens = rippled_server.get_nft_tokens(new_owner, verbose=verbose)
                        assert token_id in nft_tokens, "Token ID '{}' not found in NFToken: {}".format(token_id, nft_tokens)

                        nft_tokens = rippled_server.get_nft_tokens(old_owner, verbose=verbose)
                        assert token_id not in nft_tokens, "Token ID '{}' found in NFToken: {}".format(token_id, nft_tokens)

                elif transaction_type == 'AMMCreate':
                    tx_json = response['tx_json']
                    account = tx_json['Account']
                    asset_1, asset_2 = tx_json['Amount'], tx_json['Amount2']

                    single_asset = False
                    if isinstance(asset_1, str):
                        xrp_value = int(asset_1)
                        asset_1 = constants.XRP_ASSET
                        single_asset = True
                    amm_info = rippled_server.amm_info(asset_1, asset_2)
                    amm_id = amm_info['amm']['account']

                    assets = [asset_1, asset_2]
                    asset_1_string, asset_2_string = [f"{xrp_value/1e6} XRP" if asset['currency'] == 'XRP'
                                                      else f"{asset['value']} {asset['currency']}.{asset['issuer'][:6]}"
                                                      for asset in assets]
                    log.debug(f"{account} created AMM with:")
                    log.info(f"AMM ID: {amm_id}")
                    log.debug(f"{asset_1_string}")
                    log.debug(f"{asset_2_string}")

                    payload = {
                        "tx_json": {
                            "amm": {
                                "asset": asset_1,
                                "asset2": asset_2
                            },
                            "ledger_index": "validated"
                        }
                    }

                    data = rippled_server.execute_transaction(method="ledger_entry", payload=payload)
                    assert amm_id == data['node']['Account'], "Couldn't find AMM Account with ledger_entry"

                    amm_account = amm_info['amm']['account']

                    acct_objects = rippled_server.get_account_objects(amm_id)['account_objects']
                    payload = {"tx_json":{"amm": {"asset": asset_1, "asset2": asset_2}}}
                    ledger_entry = rippled_server.execute_transaction(payload=payload, method='ledger_entry')
                    ledger_entry_amm_id = ledger_entry['node']['Account']
                    assert amm_id == ledger_entry_amm_id, "AMM ids do not match"

                    # TODO: Calculate correct reserve is witheld

                    # Trust lines created
                    amm_account_lines = rippled_server.get_account_lines(amm_account)
                    if single_asset:
                        assert (len(amm_account_lines['lines']) == 2)
                        assert asset_2['issuer'] in [account['account']
                            for account in amm_account_lines['lines']]
                    else:
                        assert (len(amm_account_lines['lines']) == 3)
                        assert asset_1['issuer'] in [account['account']
                            for account in amm_account_lines['lines']]
                        assert asset_2['issuer'] in [account['account']
                            for account in amm_account_lines['lines']]

                else:
                    account_objects = wait_for_account_objects_in_ledger(rippled_server, account_id, verbose=verbose)

                    no_object_or_signerlist_found = False
                    if account_objects:
                        for account_object in account_objects:
                            if account_object["LedgerEntryType"] == "SignerList":
                                log.debug("Ignoring SignerList object for OfferCreate Transaction")
                                no_object_or_signerlist_found = True
                                break
                    else:
                        log.debug("No account object found")
                        no_object_or_signerlist_found = True

                    offer_crossing_status = False
                    if "Flags" in response["tx_json"] and response["tx_json"]["Flags"] in constants.OFFER_CROSSING_FLAGS and \
                            offer_crossing is False and no_object_or_signerlist_found:
                        log.debug("  OfferCreate flag: {} applied".format(response["tx_json"]["Flags"]))
                        offer_crossing_status = True
                    else:
                        assert account_objects, "Account object not created in ledger"

                no_of_objects_matched = 0
                for account_object in account_objects:
                    log.debug("Parsing account object: {}".format(account_object))
                    if hash_from_previous_txn == account_object["PreviousTxnID"]:
                        no_of_objects_matched += 1
                        if account_object["LedgerEntryType"] == "SignerList" or \
                                account_object["LedgerEntryType"] == "RippleState":
                            assert response["tx_json"]["Account"] == \
                                   rippled_server.get_account_objects(account_id, verbose=verbose)['account']

                        elif account_object["LedgerEntryType"] == "DID":
                            ledger_index = rippled_server.get_did_ledger_index(response)
                            ledger_entry_response = rippled_server.get_ledger_entry(index=ledger_index,
                                                                                    verbose=False)
                            assert ledger_entry_response["node"]["LedgerEntryType"] == "DID", \
                                f"Incorrect LedgerEntryType: {ledger_entry_response['node']['LedgerEntryType']}"
                            assert ledger_entry_response["node"]["Account"] == response["tx_json"]["Account"], \
                                f"Account mismatch: {ledger_entry_response['node']['Account']}"

                            # Verify DID params
                            for param in constants.DID_PARAMS:
                                if param in response["tx_json"] and response["tx_json"][param]:
                                    assert response["tx_json"][param] == account_object[param], f"Mismatch in '{param}'"
                                    log.debug(f"  verified param: '{param}' ({account_object[param]})")

                        else:
                            assert response["tx_json"]["Account"] == \
                                   rippled_server.get_account_objects(account_id, verbose=verbose)['account']

                        if transaction_type in constants.PAY_CHANNEL_TRANSACTIONS:
                            assert account_object['LedgerEntryType'] == "PayChannel"
                            if transaction_type == "PaymentChannelCreate":
                                account_channels_response = rippled_server.get_account_channels(response["tx_json"]["Account"])
                                verify_rippled_method_objects(account_channels_response, method="account_channels")
                        elif transaction_type == "TrustSet":
                            assert account_object['LedgerEntryType'] == "RippleState"
                        elif transaction_type == "XChainCreateBridge":
                            assert account_object['XChainClaimID'] == "0", "XChainSequence not initialized to 0"
                        elif transaction_type == "XChainCreateClaimID":
                            assert account_object['LedgerEntryType'] == "XChainOwnedClaimID"
                        elif transaction_type == "OfferCreate":
                            if offer_crossing:
                                if account_object['LedgerEntryType'] == "RippleState":  # Offer claim
                                    log.info("  * Offer Crossed")
                                    offer_crossing_status = True
                            elif offer_crossing is False:
                                if account_object['LedgerEntryType'] == "Offer":  # Failing offer claim
                                    log.info("  * As expected, no offer Crossed")
                                    offer_crossing_status = True
                            else:
                                if account_object['LedgerEntryType'] == "Offer":  # Offer Create
                                    log.info("  * Offer Created")
                                    offer_crossing_status = True

                        elif transaction_type == "EscrowCreate":
                            assert response["tx_json"]["Destination"] == account_object['Destination']
                            assert response["tx_json"]["Amount"] == account_object['Amount']
                            assert response["tx_json"]["FinishAfter"] == account_object['FinishAfter']
                            if "CancelAfter" in account_object:
                                assert response["tx_json"]["CancelAfter"] == account_object['CancelAfter']

                        elif transaction_type == "CheckCreate":
                            assert response["tx_json"]["Destination"] == account_object['Destination']
                            assert response["tx_json"]["SendMax"] == account_object['SendMax']

                        elif transaction_type == "NFTokenCreateOffer":
                            assert account_object['LedgerEntryType'] == "NFTokenOffer"
                            assert account_object['NFTokenID'] == token_id
                        else:
                            assert account_object['LedgerEntryType'] in response["tx_json"][
                                "TransactionType"], "TransactionType mismatch: {} [Expected: {}]".format(
                                account_object['LedgerEntryType'], transaction_type)

                if transaction_type == "TicketCreate":
                    log.info("  No. of Tickets Created: {}".format(no_of_objects_matched))
                    assert response["tx_json"][
                               "TicketCount"] == no_of_objects_matched, "No. of account objects and tickets mismatch"
                    expected_account_sequence = rippled_server.get_last_recorded_account_sequence(
                        account_id) + no_of_objects_matched + 1
                    assert rippled_server.get_account_sequence(
                        account_id) == expected_account_sequence, "Account Sequence not progressed to {}".format(
                        expected_account_sequence)
                elif transaction_type == "OfferCreate":
                    assert offer_crossing_status, "Offer Object validation failed"

            elif transaction_type in constants.transactions["CLEARING_OBJECTS"]:
                log.debug("Verifying if objects are settled/cleared...")
                try:
                    account_id = response["tx_json"]["Owner"]
                except KeyError as e:
                    account_id = response["tx_json"]["Account"]
                hash_from_previous_txn = response["tx_json"]["hash"]

                ledger_index = None
                previous_txn_id = None
                object_removed = False
                deleted_node_found = False
                account_object_found = False

                account_object_rsp = rippled_server.get_account_objects(account_id, verbose=verbose)

                if transaction_type == "AccountDelete":  # AccountDelete Txn
                    if "error" in account_object_rsp and account_object_rsp["error"] == "actNotFound":
                        log.debug("Probably, account does not exist")
                        object_removed = True

                elif transaction_type == "OracleDelete":
                    assert 'OracleDocumentID' in response['tx_json'], "OracleDocumentID field not found in the response"
                    oracle_document_id = response['tx_json']['OracleDocumentID']
                    get_price_oracle_response = rippled_server.get_price_oracle(account_id, oracle_document_id, verbose=verbose)
                    assert get_price_oracle_response["error"] == "entryNotFound", "PriceOracle not deleted"
                    object_removed = True


                elif transaction_type == "DIDDelete":
                    log.debug("Verify if DID object is removed")
                    ledger_index = rippled_server.get_did_ledger_index(response)
                    ledger_entry_response = rippled_server.get_ledger_entry(index=ledger_index,
                                                                            verbose=False)
                    assert ledger_entry_response["error"] == "entryNotFound", "DID not deleted"
                    log.debug(f"  DID '{ledger_index}' deleted")
                    object_removed = True

                elif not account_object_rsp["account_objects"]:  # empty account_objects as expected
                    log.debug("account objects empty")
                    object_removed = True
                    deleted_node_found = True
                else:
                    tx_response = rippled_server.tx(hash_from_previous_txn, verbose=False)
                    for affected_node in tx_response["meta"]["AffectedNodes"]:
                        log.debug("Parsing affected node: {}...".format(affected_node))
                        try:
                            if "DeletedNode" in affected_node and \
                                    transaction_type == tx_response["TransactionType"]:
                                log.debug("Found deleted node: {}".format(affected_node))
                                deleted_node_found = True
                                ledger_index = affected_node["DeletedNode"]["LedgerIndex"]
                                previous_txn_id = affected_node["DeletedNode"]["FinalFields"]["PreviousTxnID"]
                                break
                        except KeyError as e:
                            pass
                    log.debug("LedgerIndex from DeletedNode: {}".format(ledger_index))
                    log.debug("PreviousTxnID from DeletedNode: {}".format(previous_txn_id))

                    for account_object in account_object_rsp["account_objects"]:
                        log.debug("account_object: {}".format(account_object))
                        if account_object["index"] == ledger_index or account_object["PreviousTxnID"] == previous_txn_id:
                            if transaction_type == "OfferCancel" and account_object["LedgerEntryType"] == "RippleState":
                                log.debug(
                                    "Not waiting for txt to be cleared, as Trustline exists until it's in default state")
                                break
                            else:
                                log.error("account object not removed")
                                account_object_found = True
                                break

                    if previous_txn_id and not account_object_found:
                        log.debug("  account object removed")
                        object_removed = True

                    if object_removed and transaction_type == "NFTokenCancelOffer":
                        assert tx_response["meta"]["nftoken_ids"], \
                            "`nftoken_ids` is empty in NFTokenAcceptOffer transaction"
                        log.debug("**** verified: {}".format(tx_response["meta"]["nftoken_ids"]))

                if not object_removed and not deleted_node_found and not account_object_found:
                    log.info("  DeletedNode not created for transaction type: {}".format(transaction_type))
                    log.info("  Probably, an invalid RPC request returns success as expected")
                    assert previous_txn_id is None, "DeletedNode created for transaction type: {}".format(
                        transaction_type)
                    assert ignore_account_objects, \
                        "If response is expected to succeed, " \
                        "pass 'ignore_account_objects=True' for transaction validation"
                else:
                    log.debug("  account object cleared for txn '{}'".format(hash_from_previous_txn))
                    assert object_removed, "account object not cleared for txn '{}'".format(hash_from_previous_txn)

            elif transaction_type in constants.transactions["NOT_CREATING_OBJECTS"]:
                log.debug("Verifying if no objects are created...")
                try:
                    account_id = response["tx_json"]["Owner"]
                except KeyError as e:
                    account_id = response["tx_json"]["Account"]

                account_objects = rippled_server.get_account_objects(account_id, verbose=verbose)
                for account_object in account_objects["account_objects"]:
                    log.debug("Parsing account object: {}".format(account_object))
                    assert transaction_type not in account_object[
                        'LedgerEntryType'], "Account object created for Transaction Type: {}".format(transaction_type)

                if transaction_type == 'AMMBid':
                    asset = response['tx_json']['Asset']
                    asset2 = response['tx_json']['Asset2']
                    amm_info = rippled_server.amm_info(asset, asset2)
                    amm_validator.verify_auction_slot(account_id, amm_info)
            else:
                log.error("Missing entry for '{}' in 'constants.transactions'".format(transaction_type))
                assert False, "Missing entry for '{}' in 'constants.transactions'".format(transaction_type)

            log.info("  '{}': verified".format(account_id))
        else:
            log.debug("Skipping account objects verification for response: {}".format(response))


def verify_account_flags(rippled_server, response, verbose=False):
    try:
        transaction_type = response["tx_json"]["TransactionType"]
    except KeyError as e:
        log.debug("Skipping account_flags verification")
        return

    if transaction_type == "AccountSet":
        set_flag = None
        account_info_response = None
        try:
            account_id = response["tx_json"]["Account"]
            account_info_response = rippled_server.get_account_info(account_id, verbose=verbose)
            set_flag = response["tx_json"]["SetFlag"]
        except KeyError as e:
            pass

        if set_flag == constants.FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback:
            allow_trustline_clawback_flag = account_info_response["account_flags"]["allowTrustLineClawback"]
            if response["engine_result"] in ("tesSUCCESS", "terQUEUED"):
                assert allow_trustline_clawback_flag, "Flag 'allowTrustLineClawback' not True"
            else:
                assert not allow_trustline_clawback_flag, "Flag 'allowTrustLineClawback' not False"

        log.info("")
        log.info("Account flags verified")


def verify_test(rippled_server, response=None, accounts=None, response_result="tesSUCCESS",
                offer_crossing=None, offer_cancelled=None, method=None, ignore_account_objects=False, stream_validation=False):
    if response:
        verify_account_flags(rippled_server, response)
        verify_account_objects(rippled_server, response, response_result=response_result,
                               offer_crossing=offer_crossing, offer_cancelled=offer_cancelled, method=method,
                               ignore_account_objects=ignore_account_objects)
        verify_transaction(rippled_server, response, engine_result=response_result)
        if accounts:
            validate_account_balance(rippled_server, accounts, can_have_deleted_account=True)
    else:
        assert stream_validation, "response should be none only for stream data validation"

    if stream_validation:
        time.sleep(2)
        assert not rippled_server.stream_queue.empty()
        while not rippled_server.stream_queue.empty():
            stream_data = rippled_server.stream_queue.get()
            validate_stream_data(rippled_server, response=response, stream_response=stream_data)
            time.sleep(5)
        log.info("Stream data validated")


def wait_for_account_objects_in_ledger(rippled_server, account_id, verbose=True):
    max_timeout = 20  # max sec for ledger close
    start_time = time.time()
    end_time = start_time + max_timeout
    account_objects = None
    while time.time() <= end_time and not account_objects:
        log.debug("Try after 1 second...")
        time.sleep(1)
        res_account_objects = rippled_server.get_account_objects(account_id, verbose=verbose)
        account_objects = res_account_objects["account_objects"]
        log.debug("account_objects: {}".format(account_objects))

    return account_objects


def validate_stream_data(rippled_server, response=None, stream_response=None):
    log.info("validating stream data.....")

    object_verified = False

    log.debug(response)
    log.debug(stream_response)

    if response and stream_response:
        if not stream_response["status"] == "proposed":
            meta_data = rippled_server.tx(response["tx_json"]["hash"])["meta"]
            assert meta_data == stream_response["meta"], "{} transaction meta do not match with subscribe meta {}".format(
                meta_data, stream_response["meta"])
    if stream_response:
        if stream_response["type"] in constants.STREAM_PARAMS:
            if stream_response["type"] == "transaction":
                if stream_response["status"] == "proposed":
                    verify_parameters_in_stream_response(stream="transaction_proposed", stream_response=stream_response)
                else:
                    verify_parameters_in_stream_response(stream=stream_response["type"], stream_response=stream_response)
                if "tx_json" in stream_response:
                    assert stream_response["tx_json"], "tx_json not found: {}".format(stream_response)
                    assert stream_response["hash"], "hash not found: {}".format(stream_response)
                else:
                    assert stream_response["transaction"], "transaction not found: {}".format(stream_response)
                object_verified = True
            else:
                verify_parameters_in_stream_response(stream=stream_response["type"], stream_response=stream_response)
                object_verified = True
        elif stream_response["type"] == "response":
            assert stream_response["status"] == "success", "status is not success: {}".format(stream_response)
            object_verified = True
        else:
            log.info("Unknown type found")

        assert object_verified, "objects not verified"
    else:
        assert False, "No stream data to validate {}".format(stream_response)


def verify_parameters_in_stream_response(stream, stream_response):
    for value in stream_response:
        assert value in constants.STREAM_PARAMS[stream] and stream_response[
            value] is not None, f"{stream} stream has extra parameters {stream_response}"
