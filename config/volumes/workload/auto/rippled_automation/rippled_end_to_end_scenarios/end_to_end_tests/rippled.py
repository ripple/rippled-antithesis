import asyncio
import copy
import json
import os
import queue
import threading
import time
from copy import deepcopy

import requests
import websocket
import websockets

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.price_oracle.price_oracle_test_data import \
    DEFAULT_ORACLE_DOCUMENT_ID, DEFAULT_ASSET_CLASS, DEFAULT_PROVIDER, DEFAULT_PRICE_DATA, DEFAULT_BASE_ASSET, \
    DEFAULT_ASSET_PRICE, DEFAULT_QUOTE_ASSET
from rippled_automation.rippled_end_to_end_scenarios.src.commands.account import Account
from rippled_automation.rippled_end_to_end_scenarios.utils import helper
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils.amm.amm_helper import AMM_mixin

log = log_helper.get_logger()


class RippledServer(AMM_mixin):
    def __init__(self, address=None, use_websockets=False, server_name=constants.RIPPLED_SERVER_NAME, rippled_exec=None,
                 rippled_config=None, standalone_mode=False, server_type=constants.SERVER_TYPE_RIPPLED):
        proto = "ws" if use_websockets else "http"
        self.websockets = use_websockets
        self.address = f"{proto}://{address}"
        self.name = server_name
        self.rippled_exec = rippled_exec
        self.rippled_config = rippled_config
        self.standalone_mode = standalone_mode
        self.rippled_as_clio = False
        self.server_type = server_type
        self.funding_account = None
        self.stream_queue = queue.Queue()
        self.stream_list = []

        # Sidechain specific
        self.door = None
        self.iou_door = None
        self.reward_accounts = {}
        self.issuer = None
        self.txn_submit = constants.SIDECHAIN_SUBMIT_ADD_ATTESTATION
        self.issuing_chain_master_account = None  # master account for funding test accounts in server mode

        if self.standalone_mode:
            if not os.path.isfile(rippled_exec):
                raise Exception("{} does not exist. Check help".format(rippled_exec))
            if not os.path.isfile(rippled_config):
                raise Exception("{} does not exist. Check help".format(rippled_config))

        if self.server_type in (constants.SERVER_TYPE_RIPPLED, constants.SERVER_TYPE_CLIO):
            self.network_id = self.get_network_id(verbose=False)

        if self.server_type == constants.SERVER_TYPE_RIPPLED:
            self.funding_account = self.create_funding_account()
            # Initialize test genesis account balance
            wallet = self.create_wallet_from_account_id(account_id=constants.TEST_GENESIS_ACCOUNT_ID,
                                                        master_seed=constants.TEST_GENESIS_ACCOUNT_SEED)
            test_genesis_account = self.create_account(wallet=wallet, verbose=False)

    def create_funding_account(self):
        funding_account = self.create_account(verbose=False)
        log.info(f"Creating funding account '{funding_account.account_id}' ({self.name})...")
        log.debug(f"Test Genesis account '{constants.TEST_GENESIS_ACCOUNT_ID}' balance: "
                  f"{self.get_account_balance(constants.TEST_GENESIS_ACCOUNT_ID, verbose=False)}")

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": constants.TEST_GENESIS_ACCOUNT_ID,
                "Destination": funding_account.account_id,
                "Amount": constants.RUNTIME_FUNDING_ACCOUNT_MAX_BALANCE,
                # "Sequence": DO NOT PASS SEQUENCE IN THIS PAYLOAD TO HANDLE tefPAST_SEQ
            },
            "secret": constants.TEST_GENESIS_ACCOUNT_SEED
        }
        response = self.execute_transaction(payload=payload, verbose=False)
        if self.is_transaction_validated(response, verbose=False):
            return funding_account

        log.error("**** Unable to create funding account")
        return None

    def convert_command(self, data):
        new_data = deepcopy(data)
        if 'command' not in data:
            command = new_data.get('method')
            del new_data['method']
            new_data.update({"command": command})
            params = new_data.get('params')[0]
            del new_data['params']
            new_data.update(params)
        log.debug(new_data)
        return new_data

    async def send_command(self, client, command):
        async with websockets.connect(client) as websocket:
            command = json.dumps(command)
            await websocket.send(command)
            resp = await websocket.recv()
            return resp

    def get_rippled_epoch_time(self, seconds_elapsed=0):
        return int(time.time() + seconds_elapsed) - constants.RIPPLE_EPOCH

    def get_rippled_version(self, verbose=True):
        rippled_version = None
        log.debug("Get rippled version...")
        try:
            rippled_version = self.get_server_info(verbose=verbose)["info"]["build_version"][:15]
        except KeyError as e:
            log.debug("Server is not rippled")
        log.debug("  version: {}".format(rippled_version))
        return rippled_version

    def get_clio_rippled_version(self, verbose=True):
        rippled_version = None
        clio_version = None
        log.debug("Get clio rippled version...")
        try:
            rippled_version = self.get_server_info(verbose=verbose)["info"]["rippled_version"][:15]
            clio_version = self.get_server_info(verbose=verbose)["info"]["clio_version"]
        except KeyError as e:
            log.debug("Server is not Clio")
        log.debug("  rippled version: {}".format(rippled_version))
        log.debug("  Clio version: {}".format(clio_version))

        return rippled_version, clio_version

    def get_network_id(self, verbose=True):
        network_id = None
        log.debug("Get Network ID...")
        try:
            network_id = self.get_server_info(verbose=verbose)["info"]["network_id"]
        except KeyError as e:
            log.debug("Network ID not found")
        log.debug("  Network ID: {}".format(network_id))
        return network_id

    def execute_transaction(self, payload=None, method=None, secret=None, wait_for_ledger_close=True,
                            submit_only=False, verbose=True, execution_time=None, **kwargs):
        sign_account = None
        transaction_type = None
        create_response = None
        calculate_balance = True
        if payload:
            tx_json = payload["tx_json"]
            if "secret" in payload:
                secret = payload["secret"]
            if "account" in payload:  # like in method: sign_for
                sign_account = payload["account"]
            self.add_default_fee(payload)
        else:
            tx_json = kwargs

            # TODO: This is to support old testcases with method: sign_for
            # TODO: Remove this after refactoring multisign_test.py
            if "sign_account" in kwargs:
                sign_account = kwargs.pop("sign_account")
                secret = kwargs.pop("sign_secret")
                tx_json = kwargs
                method = "sign_for"

        if "TransactionType" in tx_json:
            transaction_type = tx_json["TransactionType"]

        if submit_only:
            method = "sign"
        elif transaction_type and not sign_account and method is None:
            method = "submit"
        elif "tx_blob" in tx_json:
            log.debug("Setting method: submit for submit blob")
            method = "submit"
        elif "command" in tx_json:
            log.debug("Assigning command as method for websocket only requests explicitly due to validation purposes")
            method = tx_json["command"]
        if method is None:
            log.error("RPC method name missing in call to execute transaction")
            raise Exception("RPC method name missing in call to execute transaction")

        if verbose:
            request_method_or_txn_type = method
            if transaction_type:
                self.add_network_id(payload)
                request_method_or_txn_type = "{} ({})".format(method, transaction_type)
                log.info("")
            else:
                log.debug("No TransactionType in payload. Method: {}".format(method))

            if self.name != constants.RIPPLED_SERVER_NAME:
                request_method_or_txn_type = "{} ({})".format(request_method_or_txn_type, self.name)
            log.info("{}...".format(request_method_or_txn_type))

        # Task to be done before executing transaction
        if transaction_type == "TicketCreate":
            self.update_account_sequence(payload)

        elif transaction_type == "EscrowFinish":
            create_response = kwargs.get("create_response")

            log.debug("Calculating wait time for: {}".format(execution_time))
            if payload and create_response and execution_time:
                if execution_time == constants.EXECUTE_TRANSACTION_AFTER:
                    finish_after = create_response["tx_json"]["FinishAfter"]
                    epoch_wait_time = finish_after + 1
                elif execution_time == constants.EXECUTE_TRANSACTION_BEFORE:
                    epoch_wait_time = self.get_rippled_epoch_time(seconds_elapsed=0)
                else:
                    epoch_wait_time = self.get_rippled_epoch_time(0)  # constants.EXECUTE_TRANSACTION_NOW

                self.wait_before_executing_transaction(epoch_wait_time=epoch_wait_time, verbose=False)

        elif transaction_type == "EscrowCancel":
            create_response = kwargs.get("create_response")

            log.debug("Calculating wait time for: {}".format(execution_time))
            if payload and create_response and execution_time:
                if execution_time == constants.EXECUTE_TRANSACTION_AFTER:
                    cancel_after = create_response["tx_json"]["CancelAfter"]
                    epoch_wait_time = cancel_after + 1
                elif execution_time == constants.EXECUTE_TRANSACTION_BEFORE:
                    epoch_wait_time = self.get_rippled_epoch_time(seconds_elapsed=0)
                else:
                    epoch_wait_time = self.get_rippled_epoch_time(0)  # constants.EXECUTE_TRANSACTION_NOW

                self.wait_before_executing_transaction(epoch_wait_time=epoch_wait_time, verbose=False)

        elif transaction_type == "NFTokenAcceptOffer" or transaction_type == "NFTokenCancelOffer":
            create_response = kwargs.get("create_response")

            log.debug("Calculating wait time for: {}".format(execution_time))
            if payload and create_response and execution_time:
                if execution_time == constants.EXECUTE_TRANSACTION_AFTER:
                    expiration = create_response["tx_json"]["Expiration"]
                    epoch_wait_time = expiration + 1
                elif execution_time == constants.EXECUTE_TRANSACTION_BEFORE:
                    epoch_wait_time = self.get_rippled_epoch_time(seconds_elapsed=0)
                else:
                    epoch_wait_time = self.get_rippled_epoch_time(0)  # constants.EXECUTE_TRANSACTION_NOW

                self.wait_before_executing_transaction(epoch_wait_time=epoch_wait_time, verbose=False)

        elif transaction_type == "OfferCreate":
            issuer = None
            try:
                if "issuer" in kwargs:
                    issuer = kwargs.get("issuer")
                    log.debug("Issuer found")

                    account_balance = int(self.get_account_balance(issuer, verbose=False))
                    dest_account_id = payload["tx_json"]["Account"]
                    amount = int(payload["tx_json"]["TakerPays"])
                else:
                    log.debug("No issuer found")
                    account_balance = int(
                        self.get_account_balance(payload["tx_json"]["Account"], verbose=False))
                    dest_account_id = payload["tx_json"]["TakerPays"]["issuer"]
                    amount = int(payload["tx_json"]["TakerGets"])
            except Exception as e:
                log.debug("Unable to parse payload: {}".format(e))

        elif transaction_type in ("XChainAddClaimAttestation", "XChainAddAccountCreateAttestation"):
            if self.txn_submit:
                log.info("  ** auto-submit **")
                source_account = kwargs.get("source_account")
                if source_account is None:
                    log.error("Missing parameter: 'source_account' in execute_transaction()")
                    raise Exception("Missing parameter: 'source_account' in execute_transaction()")

                log.debug("  Validate AddAttestation transaction triggered by submission accounts...")
                add_attestation_txn_settled = False
                for submission_account in self.reward_accounts.values():  # Submission account is same as reward account
                    log.info("  Looking up submission account {}...".format(submission_account.account_id))
                    max_retries = 5
                    count = 1
                    transaction = None
                    transaction_found = False
                    wait_time = 5  # seconds to wait before retry
                    while not transaction_found and count < max_retries:
                        account_tx_responses = self.get_account_tx(submission_account.account_id, limit=5,
                                                                   verbose=False)
                        for transaction in account_tx_responses["transactions"]:
                            if transaction["tx"]["TransactionType"] in (
                                    "XChainAddClaimAttestation", "XChainAddAccountCreateAttestation") and \
                                    transaction["tx"]["Account"] == submission_account.account_id:
                                log.debug("  XChainAddClaimAttestation txn found. Checking for match...")

                                try:
                                    if transaction["tx"]["OtherChainSource"] == source_account:
                                        log.debug("  ** Matching XChainAddClaimAttestation "
                                                  "(XChainClaimAttestationBatch) for account {} found".
                                                  format(source_account))
                                        transaction_found = True
                                        break
                                except KeyError as e:
                                    pass  # Ignore if not matched/found

                        if not transaction_found:
                            count += 1
                            log.debug("  Retry [{}/{}] after {} seconds...".format(count, max_retries, wait_time))
                            time.sleep(wait_time)

                    if transaction_found:
                        txn_hash = None
                        max_timeout = 30  # max sec to fetch XChainAddClaimAttestation transaction
                        start_time = time.time()
                        end_time = start_time + max_timeout
                        while time.time() <= end_time:
                            txn_hash = transaction["tx"]["hash"]
                            if transaction["tx"]["TransactionType"] in (
                                    "XChainAddClaimAttestation", "XChainAddAccountCreateAttestation"):
                                log.debug("  Update AddAttestation txn auto-submit fee for account {}...".format(
                                    submission_account.account_id))
                                transaction_fee = self.tx(tx_id=txn_hash, verbose=False)["Fee"]
                                log.debug("AddAttestation txn Fee: {}".format(transaction_fee))
                                self.update_xrp_balance_with_txn_amount(submission_account.account_id, transaction_fee,
                                                                        mode=constants.XRP_DEBIT)
                                break

                        if txn_hash and not add_attestation_txn_settled and \
                                self.is_transaction_validated(tx_id=txn_hash, verbose=False):
                            log.debug("  XChainAddClaimAttestation Transaction validated: {}".format(txn_hash))
                            if self.xchain_validation(payload, txn_hash):
                                add_attestation_txn_settled = True
                    else:
                        log.info("No XChainAddClaimAttestation txn found for submission account: {}".format(
                            submission_account.account_id))

                return constants.SIDECHAIN_IGNORE_VALIDATION
            else:
                if tx_json["Signature"] is None:  # AddAttestation payload having "None" response from witness
                    log.info("  ** offline witness/no Attestation to add")
                    return constants.SIDECHAIN_IGNORE_VALIDATION

        elif transaction_type == "AMMCreate":
            amm_create_amounts = [tx_json['Amount'], tx_json['Amount2']]

            assets = [f"{int(amount) / 1e6} XRP" if not isinstance(amount, dict)
                      else f"{amount['value']} {amount['currency']}.{amount['issuer'][:5]} "
                      # TODO: User format_currency()
                      for amount in amm_create_amounts]
            lp_type = " - ".join([*assets])
            log.info(f"  Creating {lp_type} AMM")

        if method == "sign_for":
            request = {
                "method": method,
                "params": [dict(tx_json=tx_json, secret=secret,
                                account=sign_account)]
            }
        elif method == "submit_multisigned":
            request = {"method": method, "params": [dict(tx_json=tx_json)]}
        else:
            if secret:
                request = {
                    "method": method,
                    "params": [dict(tx_json=tx_json, secret=secret)]
                }
            else:
                request = {"method": method, "params": [tx_json]}

        if self.rippled_as_clio:
            log.debug("Clio running as rippled server")
            request = self.update_request_to_forward_to_rippled(request=request, method=method)
        if method == "subscribe":
            request = tx_json
        response = self.execute_command(json.dumps(request), verbose=verbose)
        if submit_only:
            response = self.submit_blob(response, verbose=True)
            calculate_balance = False  # submit_blob calculates balances
        if payload and "tx_blob" in tx_json:  # if submit_blob is called
            try:
                log.debug("This is submit_blob execution")
                transaction_type = response["tx_json"]["TransactionType"]
            except KeyError:
                pass

        # Parse transaction response
        if wait_for_ledger_close and method != constants.RIPPLED_STOP_METHOD:
            log.debug("Parsing response: {}".format(response))
            seq = self.get_txn_sequence(response, verbose=False)
            if "engine_result" in response and \
                    (response["engine_result"] == "tesSUCCESS" or response["engine_result"] == "terQUEUED"):

                if self.is_transaction_validated(response, verbose=False):
                    log.debug("Transaction validated")
                    if calculate_balance:
                        if transaction_type == "Payment":
                            log.debug("Payment transaction")
                            try:
                                account_id = response["tx_json"]["Account"]
                                dest_account_id = response["tx_json"]["Destination"]
                                debit_amount = credit_amount = response["tx_json"]["Amount"]
                                if 'SendMax' in response["tx_json"]:
                                    log.debug("SendMax found in response")
                                    debit_amount = response["tx_json"]["SendMax"]
                                self.update_xrp_balance_with_txn_amount(account_id, debit_amount,
                                                                        mode=constants.XRP_DEBIT)
                                self.update_xrp_balance_with_txn_amount(dest_account_id, credit_amount,
                                                                        mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))

                        elif transaction_type == "XChainCommit":
                            log.debug("XChainCommit transaction")
                            try:
                                account_id = response["tx_json"]["Account"]
                                debit_amount = response["tx_json"]["Amount"]
                                self.update_xrp_balance_with_txn_amount(account_id, debit_amount,
                                                                        mode=constants.XRP_DEBIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))

                        elif transaction_type == "XChainAccountCreateCommit":
                            log.debug("XChainAccountCreateCommit transaction")
                            try:
                                account_id = response["tx_json"]["Account"]
                                debit_amount = int(response["tx_json"]["Amount"])
                                reward_amount = int(response["tx_json"]["SignatureReward"])
                                self.update_xrp_balance_with_txn_amount(account_id, (debit_amount + reward_amount),
                                                                        mode=constants.XRP_DEBIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))

                        elif transaction_type in ("XChainClaim", "XChainAddClaimAttestation",
                                                  "XChainAddAccountCreateAttestation"):
                            txn_hash = response["tx_json"]["hash"]
                            self.xchain_validation(payload, txn_hash)

                        elif transaction_type == "PaymentChannelCreate" or \
                                transaction_type == "PaymentChannelFund" or \
                                transaction_type == "EscrowCreate":
                            log.debug("PaymentChannelCreate/EscrowCreate transaction")
                            try:
                                account_id = response["tx_json"]["Account"]
                                debit_amount = response["tx_json"]["Amount"]
                                self.update_xrp_balance_with_txn_amount(account_id, debit_amount,
                                                                        mode=constants.XRP_DEBIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "PaymentChannelClaim":
                            log.debug("PaymentChannelClaim transaction")
                            try:
                                tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
                                channel = response["tx_json"]["Channel"]
                                amount = 0
                                dest_account_id = None
                                src_account_id = None
                                previous_balance = 0
                                current_balance = 0
                                node = None
                                for affected_node in tx_response["meta"]["AffectedNodes"]:
                                    log.debug("Parsing affected node: {}...".format(affected_node))

                                    if affected_node.get("ModifiedNode"):
                                        node = affected_node["ModifiedNode"]
                                    elif affected_node.get("DeletedNode"):
                                        node = affected_node["DeletedNode"]
                                    try:
                                        if node["LedgerIndex"] == channel:
                                            dest_account_id = node["FinalFields"]["Destination"]
                                            src_account_id = node["FinalFields"]["Account"]
                                            amount = int(node["FinalFields"]["Amount"])
                                            current_balance = int(node["FinalFields"]["Balance"])
                                            try:
                                                previous_txn_id = node["PreviousTxnID"]
                                            except KeyError as e:
                                                previous_txn_id = node["FinalFields"]["PreviousTxnID"]
                                            log.debug(
                                                "Destination account: {} and Source account:{}".format(dest_account_id,
                                                                                                       src_account_id))
                                            previous_txn_response = self.tx(previous_txn_id, verbose=False)
                                            for Affected_node in previous_txn_response["meta"]["AffectedNodes"]:
                                                try:
                                                    if Affected_node["ModifiedNode"]["LedgerIndex"] == channel:
                                                        previous_balance = int(
                                                            Affected_node["ModifiedNode"]["FinalFields"]["Balance"])
                                                        log.debug(
                                                            "previous_balance fetched: {}".format(previous_balance))
                                                        break
                                                except KeyError as e:
                                                    pass
                                            break
                                    except KeyError as e:
                                        pass

                                balance = current_balance - previous_balance
                                amount -= current_balance
                                if response["tx_json"]["Flags"] == 131072 and amount:
                                    self.update_xrp_balance_with_txn_amount(src_account_id, amount,
                                                                            mode=constants.XRP_CREDIT)
                                if dest_account_id and balance:
                                    self.update_xrp_balance_with_txn_amount(dest_account_id, balance,
                                                                            mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "EscrowCancel":
                            log.debug("EscrowCancel transaction")
                            try:
                                account_id = create_response["tx_json"]["Account"]
                                amount = create_response["tx_json"]["Amount"]
                                self.update_xrp_balance_with_txn_amount(account_id, amount, mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "EscrowFinish":
                            log.debug("EscrowFinish transaction")
                            try:
                                account_id = create_response["tx_json"]["Destination"]
                                amount = create_response["tx_json"]["Amount"]
                                self.update_xrp_balance_with_txn_amount(account_id, amount, mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "CheckCash":
                            log.debug("CheckCash transaction")
                            tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
                            try:
                                src_account_id = None
                                dest_account_id = tx_response["Account"]
                                amount = tx_response["meta"]["delivered_amount"]
                                check_id = payload["tx_json"]["CheckID"]
                                for affected_node in tx_response["meta"]["AffectedNodes"]:
                                    log.debug("Parsing affected node: {}...".format(affected_node))
                                    try:
                                        if affected_node["DeletedNode"]["LedgerIndex"] == check_id:
                                            src_account_id = affected_node["DeletedNode"]["FinalFields"]["Account"]
                                            log.debug("Source account fetched: {}".format(src_account_id))
                                            break
                                    except KeyError as e:
                                        log.debug("key '{}' not found".format(e))

                                if src_account_id:
                                    log.debug("Source account ID found. Updating account balance")
                                    self.update_xrp_balance_with_txn_amount(src_account_id, amount,
                                                                            mode=constants.XRP_DEBIT)
                                    self.update_xrp_balance_with_txn_amount(dest_account_id, amount,
                                                                            mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))

                        elif transaction_type == "NFTokenAcceptOffer":
                            log.debug("NFTokenAcceptOffer transaction")
                            tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
                            try:
                                broker_fee = 0
                                buyer_amount = None
                                seller_amount = None
                                dest_account_id = None
                                src_account_id = None
                                for affected_node in tx_response["meta"]["AffectedNodes"]:
                                    log.debug("Parsing affected node: {}...".format(affected_node))
                                    try:
                                        if "DeletedNode" in affected_node and \
                                                affected_node["DeletedNode"]["LedgerEntryType"] == "NFTokenOffer":

                                            if affected_node["DeletedNode"]["FinalFields"][
                                                "Flags"] == 1:  # Sell NFT offer
                                                log.debug("  sell NFT offer")
                                                dest_account_id = affected_node["DeletedNode"]["FinalFields"]["Owner"]
                                                seller_amount = affected_node["DeletedNode"]["FinalFields"]["Amount"]

                                            if affected_node["DeletedNode"]["FinalFields"][
                                                "Flags"] == 0:  # Buy NFT offer
                                                log.debug("  buy NFT offer")
                                                src_account_id = affected_node["DeletedNode"]["FinalFields"]["Owner"]
                                                buyer_amount = affected_node["DeletedNode"]["FinalFields"]["Amount"]

                                    except KeyError as e:
                                        log.debug("key '{}' not found".format(e))

                                if not src_account_id:
                                    log.debug("  setting default src account")
                                    src_account_id = tx_response["Account"]
                                if not dest_account_id:
                                    log.debug("  setting default dest account")
                                    dest_account_id = tx_response["Account"]

                                if "NFTokenBrokerFee" in tx_response:
                                    log.info("broker fee found")
                                    broker_fee = int(tx_response["NFTokenBrokerFee"])
                                    account_id = response["tx_json"]["Account"]
                                    self.update_xrp_balance_with_txn_amount(account_id, broker_fee,
                                                                            mode=constants.XRP_CREDIT)
                                try:
                                    if buyer_amount:
                                        amount = int(buyer_amount) - broker_fee
                                    else:
                                        amount = int(seller_amount)

                                    log.debug("Source account fetched: {}".format(src_account_id))
                                    log.debug("Destination account fetched: {}".format(dest_account_id))
                                    log.debug("Broker fee (if broker mode): {}".format(broker_fee))
                                    log.debug("Amount: {}".format(amount))

                                    log.debug("Updating account balance...")
                                    self.update_xrp_balance_with_txn_amount(src_account_id, (amount + broker_fee),
                                                                            mode=constants.XRP_DEBIT)
                                    self.update_xrp_balance_with_txn_amount(dest_account_id, amount,
                                                                            mode=constants.XRP_CREDIT)
                                except TypeError as e:
                                    log.debug("Not calculating for issued currency")
                                    pass
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))

                        elif transaction_type == "AccountDelete":
                            tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
                            try:
                                account_id = tx_response["Account"]
                                dest_account_id = tx_response["Destination"]
                                amount = tx_response["meta"]["DeliveredAmount"]
                                self.update_xrp_balance_with_txn_amount(account_id, amount, mode=constants.XRP_DEBIT)
                                self.update_xrp_balance_with_txn_amount(dest_account_id, amount,
                                                                        mode=constants.XRP_CREDIT)
                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "OfferCreate":
                            log.debug("OfferCreate transaction")

                            tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
                            try:
                                offer_claimed = False
                                src_account_id = payload["tx_json"]["Account"]
                                log.debug("Source account id: {}".format(src_account_id))
                                for affected_node in tx_response["meta"]["AffectedNodes"]:
                                    log.debug("Parsing affected node: {}...".format(affected_node))
                                    try:
                                        if affected_node["CreatedNode"]["LedgerEntryType"] == "RippleState":
                                            log.debug("This transaction claims an offer")
                                            offer_claimed = True
                                    except KeyError as e:
                                        pass

                                    try:
                                        if affected_node["ModifiedNode"]["LedgerEntryType"] == "RippleState":
                                            log.debug("This transaction claims an offer")
                                            offer_claimed = True
                                    except KeyError as e:
                                        pass

                                    try:
                                        if "DeletedNode" in affected_node and \
                                                affected_node["DeletedNode"]["LedgerEntryType"] == "Offer":
                                            taker_pays = affected_node["DeletedNode"]["PreviousFields"]["TakerPays"]
                                            if isinstance(taker_pays, str):
                                                amount = int(taker_pays)
                                    except (KeyError, TypeError) as e:
                                        pass

                                    try:
                                        if "Owner" in affected_node["ModifiedNode"]["FinalFields"]:
                                            log.debug("Fetching source account id")
                                            if issuer and affected_node["ModifiedNode"]["FinalFields"][
                                                "Owner"] == issuer:
                                                src_account_id = affected_node["ModifiedNode"]["FinalFields"]["Owner"]
                                    except KeyError as e:
                                        pass

                                if offer_claimed and src_account_id:
                                    log.debug("Offer claimed and source account found")
                                    max_withdrawal_allowed = account_balance - \
                                                             int(constants.BASE_RESERVE) - \
                                                             int(constants.OWNER_RESERVE)
                                    try:
                                        if amount > max_withdrawal_allowed:
                                            log.info("Maximum possible match for offer closing: {}".format(
                                                max_withdrawal_allowed))
                                            amount = max_withdrawal_allowed

                                        self.update_xrp_balance_with_txn_amount(src_account_id, amount,
                                                                                mode=constants.XRP_DEBIT)
                                        self.update_xrp_balance_with_txn_amount(dest_account_id, amount,
                                                                                mode=constants.XRP_CREDIT)
                                    except Exception as e:
                                        log.error(e)

                            except KeyError as e:
                                log.debug("key '{}' not found".format(e))
                        elif transaction_type == "AMMCreate":
                            if any(map(lambda asset: isinstance(asset, str), amm_create_amounts)):
                                src_account_id = payload["tx_json"]["Account"]
                                [amm_create_amount] = [amount for amount in amm_create_amounts if
                                                       isinstance(amount, str)]
                                self.update_xrp_balance_with_txn_amount(src_account_id, amm_create_amount,
                                                                        constants.XRP_DEBIT)
                else:
                    raise Exception("Transaction not validated")

        return response

    def tx(self, tx_id, binary=False, min_ledger=None, max_ledger=None, api_version=None, verbose=True):
        payload = {
            "tx_json": {
                "transaction": tx_id,
                "binary": binary
            }
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if min_ledger:
            payload["tx_json"]["min_ledger"] = min_ledger
        if max_ledger:
            payload["tx_json"]["max_ledger"] = max_ledger
        return self.execute_transaction(payload=payload, method="tx", verbose=verbose)

    def ledger_current(self, verbose=True):
        payload = {
            "tx_json": {
            },
        }
        response = self.execute_transaction(payload=payload, method="ledger_current", verbose=verbose)
        return response['ledger_current_index']

    def get_ledger_close_time(self, verbose=True):
        payload = {
            "tx_json": {
                "ledger_index": "validated"
            },
        }
        response = self.execute_transaction(payload=payload, method="ledger", verbose=verbose)
        return response['ledger']['parent_close_time']

    def get_ledger(self, verbose=True, transactions=False, expand=False, owner_funds=False, ledger_index="validated",
                   ledger_hash=None, binary=None, queue=None, api_version=None, diff=None):
        payload = {
            "tx_json": {
                "transactions": transactions,
                "expand": expand,
                "owner_funds": owner_funds,
                "ledger_index": ledger_index
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if binary:
            payload["tx_json"]["binary"] = binary
        if queue:
            payload["tx_json"]["queue"] = queue
        if diff:
            payload["tx_json"]["diff"] = diff
        return self.execute_transaction(payload=payload, method="ledger", verbose=verbose)

    def get_ledger_entry(self, index, ledger_index="validated", binary=False, ledger_hash=None, verbose=True):
        payload = {
            "tx_json": {
                "index": index,
                "ledger_index": ledger_index,
                "binary": binary
            },
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="ledger_entry", verbose=verbose)

    def get_last_closed_ledger_index(self, verbose=True):
        ledger = self.get_ledger(verbose=verbose, ledger_index="validated")
        return ledger["ledger"]['ledger_index']

    def get_ledger_transactions(self, verbose=True, ledger_index="validated"):
        ledger = self.get_ledger(verbose=verbose, transactions=True, ledger_index='validated')
        return ledger['ledger']['transactions']

    def wallet_propose(self, seed=None, key_type=constants.DEFAULT_ACCOUNT_KEY_TYPE, verbose=True):
        payload = {
            "tx_json": {
                "ledger_index": "current"
            }
        }
        if seed:
            log.debug("wallet_propose for seed: {}".format(seed))
            payload["tx_json"]["seed"] = seed
            payload["tx_json"]["key_type"] = key_type

        return self.execute_transaction(payload=payload, method="wallet_propose", verbose=verbose)

    def create_account(self, fund=False, amount=constants.DEFAULT_ACCOUNT_BALANCE, wallet=None,
                       seed=None, key_type=constants.DEFAULT_ACCOUNT_KEY_TYPE, verbose=True):
        if verbose:
            log.info("")
            log.info("Create account...")

        max_retries = 5
        count = 1
        account_created = False
        account = None
        while not account_created and count <= max_retries:
            if not wallet:
                wallet = self.wallet_propose(seed=seed, key_type=key_type, verbose=verbose)
            log.debug("rippled: {}".format(self.address))
            log.debug("wallet: {}".format(wallet))
            account = Account(wallet, rippled=self)

            if fund:
                self.fund_account(wallet['account_id'], amount, verbose=verbose)

            account_created = self.is_account_created(account, fund, verbose=False)

            log.debug("Is account added to ledger: {}".format(account_created))

            if not account_created:
                if count < max_retries:
                    count += 1
                    log.info("")
                    log.info("  Re-creating new account (attempt {}/{})...".format(count, max_retries))
                else:
                    raise Exception("All {} attempts of account creation failed".format(max_retries))

        if verbose:
            log.info("account: {}".format(account.account_id))
        return account

    def get_trustline_info(self, account, peer=None, issues=None, verbose=False):
        account = account.account_id if isinstance(account, Account) else account
        peer = peer.account_id if isinstance(peer, Account) else peer

        account_lines = self.get_account_lines(account, peer=peer, verbose=verbose).get("lines")
        # peers = [peer] if isinstance(peer, str) else peer # TODO: handle list of peers?
        msg = f"Trustlines for {account}"
        if peer:
            msg += f" with {peer}"
        if issues:
            msg += f" in {issues}"
        log.debug(msg)
        trustline_info = [line for line in account_lines if issues is None or line["currency"] in issues]
        for info in trustline_info:
            log.debug(json.dumps(info, indent=2))
        if not trustline_info:
            log.debug(f"{account} has no account lines.")
        return trustline_info

    def fund_account(self, account_id, amount=constants.DEFAULT_ACCOUNT_BALANCE, verbose=True):
        src_account = self.funding_account
        log.debug("{}: funding from master account: {}".format(self.name, src_account.account_id))

        # Update XRP balance for test validation
        try:
            Account.last_recorded_account_sequence[self][account_id] = self.get_account_sequence(account_id)
        except KeyError as e:
            # Account not created yet
            pass

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": src_account.account_id,
                "Destination": account_id,
                "Amount": amount,
            },
            "secret": src_account.master_seed
        }

        return self.execute_transaction(payload=payload, verbose=verbose)

    def create_wallet_from_account_id(self, account_id, master_seed=None, verbose=False):
        if verbose:
            log.info("")
            log.info("Create wallet for account id: {}...".format(account_id))

        # wallet with just the account_id, as the rest of the values are "NOT KNOWN"
        wallet = {
            "account_id": account_id,
            "key_type": "NOT KNOWN",
            "master_key": "NOT KNOWN",
            "master_seed": "NOT KNOWN",
            "master_seed_hex": "NOT KNOWN",
            "public_key": "NOT KNOWN",
            "public_key_hex": "NOT KNOWN",
            "status": "success"
        }
        if master_seed:
            wallet["master_seed"] = master_seed
        return wallet

    def submit_blob(self, response, verbose=False):
        if verbose:
            log.info("")
            log.info("Submit tx_blob...")

        payload = {
            "tx_json": {
                "tx_blob": response["tx_blob"]
            }
        }
        return self.execute_transaction(payload=payload, method="submit", verbose=verbose)

    def get_account_channels(self, account_id, limit=None, marker=None, destination_account=None,
                             ledger_index="validated", ledger_hash=None, verbose=False):
        payload = {
            "tx_json": {
                "account": account_id,
                "strict": True,
                "ledger_index": ledger_index,
                "queue": True
            },
        }
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if destination_account:
            payload["tx_json"]["destination_account"] = destination_account
        if marker:
            payload["tx_json"]["marker"] = marker
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_channels", verbose=verbose)

    def get_account_info(self, account_id=None, ledger_index="current", signer_lists=None, strict=True, queue=True,
                         ledger_hash=None, api_version=None, verbose=True):
        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index,
                "strict": strict,
                "queue": queue
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if signer_lists:
            payload["tx_json"]["signer_lists"] = signer_lists
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_info", verbose=verbose)

    def get_ledger_index_min(self):
        ledger_range = self.get_server_info()["info"]["complete_ledgers"]
        ledger_index_min = int(ledger_range.partition("-")[0])
        return ledger_index_min

    def get_account_tx(self, account_id, binary=False, forward=False, verbose=True, ledger_index_max=None, tx_type=None,
                       ledger_index_min=None, ledger_hash=None, ledger_index=None, limit=None, marker=None,
                       api_version=None):
        payload = {
            "tx_json": {
                "account": account_id,
                "binary": binary,
                "forward": forward
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if tx_type:
            payload["tx_json"]["tx_type"] = tx_type
        if ledger_index_min:
            payload["tx_json"]["ledger_index_min"] = ledger_index_min
        if ledger_index_max:
            payload["tx_json"]["ledger_index_max"] = ledger_index_max
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        return self.execute_transaction(payload=payload, method="account_tx", verbose=verbose)

    def get_account_objects(self, account_id, ledger_object_type=None, limit=constants.MAX_ACCOUNT_OBJECTS_LIMIT,
                            deletion_blockers_only=False,
                            marker=None, ledger_index="validated", ledger_hash=None, verbose=True):
        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index,
                "limit": limit,
                "deletion_blockers_only": deletion_blockers_only
            },
        }
        if ledger_object_type:
            payload["tx_json"]["type"] = ledger_object_type
        if marker:
            payload["tx_json"]["marker"] = marker
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_objects", verbose=verbose)

    def get_account_nfts(self, account_id, ledger_hash=None, limit=None, marker=None, ledger_index="validated",
                         verbose=True):
        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index
            },
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        return self.execute_transaction(payload=payload, method="account_nfts", verbose=verbose)

    def get_price_oracle(self, account_id, oracle_document_id, ledger_index="validated", verbose=True):
        payload = {
            "tx_json": {
                "oracle": {
                    "account": account_id,
                    "oracle_document_id": oracle_document_id
                },
                "ledger_index": ledger_index
            },
        }
        return self.execute_transaction(payload=payload, method="ledger_entry", verbose=verbose)

    def oracle_set(self, account, asset_class=DEFAULT_ASSET_CLASS, oracle_document_id=DEFAULT_ORACLE_DOCUMENT_ID,
                   provider=DEFAULT_PROVIDER, price_data_series=None, uri=None, verbose=True):
        if price_data_series is None:
            price_data_series = [DEFAULT_PRICE_DATA]

        payload = {
            "tx_json": {
                "TransactionType": 'OracleSet',
                "Account": account.account_id,
                "AssetClass": asset_class,
                "LastUpdateTime": helper.get_unix_epoch_time(),
                "OracleDocumentID": oracle_document_id,
                "PriceDataSeries": price_data_series if price_data_series else [DEFAULT_PRICE_DATA],
                "Provider": provider
            },
            "secret": account.master_seed
        }

        if uri is not None:
            payload["tx_json"]["URI"] = uri

        return self.execute_transaction(payload=payload, verbose=verbose)

    def get_nft_sell_offers(self, nft_id, ledger_hash=None, ledger_index="validated", limit=None, marker=None,
                            verbose=True):
        payload = {
            "tx_json": {
                "nft_id": nft_id,
                "ledger_index": ledger_index
            },
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        return self.execute_transaction(payload=payload, method="nft_sell_offers", verbose=verbose)

    def get_nft_buy_offers(self, nft_id, ledger_hash=None, ledger_index="validated", limit=None, marker=None,
                           verbose=True):
        payload = {
            "tx_json": {
                "nft_id": nft_id,
                "ledger_index": ledger_index
            },
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        return self.execute_transaction(payload=payload, method="nft_buy_offers", verbose=verbose)

    def get_nft_info(self, nft_id, ledger_index="validated", ledger_hash=None, verbose=False):
        payload = {
            "tx_json": {
                "nft_id": nft_id,
                "ledger_index": ledger_index
            },
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="nft_info", verbose=verbose)

    def get_nft_history(self, nft_id, ledger_index="validated", ledger_index_min=None, ledger_index_max=None,
                        forward=False, binary=False, ledger_hash=None, limit=None, marker=None, api_version=None,
                        verbose=False):
        payload = {
            "tx_json": {
                "nft_id": nft_id,
                "binary": binary,
                "forward": forward,
                "ledger_index": ledger_index
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if ledger_index_min:
            payload["tx_json"]["ledger_index_min"] = ledger_index_min
        if ledger_index_max:
            payload["tx_json"]["ledger_index_max"] = ledger_index_max
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        return self.execute_transaction(payload=payload, method="nft_history", verbose=verbose)

    def get_nft_tokens(self, account_id, verbose=False):
        account_nfts = self.get_account_nfts(account_id, verbose=verbose)
        nft_tokens = []
        for item in account_nfts["account_nfts"]:
            nft_token = item['NFTokenID']
            log.debug("NFT Token: {}".format(nft_token))
            nft_tokens.append(nft_token)

        if verbose:
            log.info("")
            log.info("NFT Tokens: {}".format(nft_tokens))
        return nft_tokens

    def get_token_offers(self, account, token_id=None, offer_type=None, verbose=False):
        account_objects = self.get_account_objects(account.account_id, verbose=verbose)
        ledger_indexes = []
        for account_object in account_objects["account_objects"]:
            if account_object["LedgerEntryType"] == "NFTokenOffer":
                ledger_index = account_object["index"]
                if token_id:  # filter by matching token_id
                    if account_object["NFTokenID"] == token_id:
                        if offer_type is None:
                            ledger_indexes.append(ledger_index)
                        else:  # filter by matching offer_type
                            if offer_type == account_object["Flags"]:
                                ledger_indexes.append(ledger_index)
                else:
                    if offer_type is None:
                        ledger_indexes.append(ledger_index)
                    else:  # filter by matching offer_type
                        if offer_type == account_object["Flags"]:
                            ledger_indexes.append(ledger_index)

        log.info("")
        log.info("Ledger Indexes (token offers): {}".format(ledger_indexes))
        if token_id and len(ledger_indexes) == 0:
            log.error("Ledger Index not found for token '{}'".format(token_id))
            raise Exception("Ledger Index not found for token '{}'".format(token_id))
        return ledger_indexes

    def get_account_balance(self, account_id, verbose=True):
        response = self.get_account_info(account_id, verbose=verbose)
        try:
            account_balance = response['account_data']['Balance']
        except KeyError:
            account_balance = constants.NON_FUNDED_ACCOUNT_BALANCE
            if verbose:
                log.warning("'{}' is not a funded account".format(account_id))

        log.debug("Account balance: {}".format(account_balance))
        return account_balance

    def get_account_lines(self, account_id, peer=None, limit=None, marker=None, ledger_index="validated",
                          ledger_hash=None, ignore_default=False, verbose=True):
        if verbose:
            log.info("")
            log.info("Get account lines...")

        payload = {
            "tx_json": {
                "account": account_id,
                "ignore_default": ignore_default,
                "ledger_index": ledger_index
            },
        }
        if peer:
            payload["tx_json"]["peer"] = peer
        if limit or limit == 0:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_lines", verbose=verbose)

    def get_all_trustlines(self, account_id, verbose=True):
        if verbose:
            log.info("")
            log.info("Getting all trustlines...")

        lines = self.get_account_lines(account_id, verbose=verbose)
        try:
            account_lines = lines['lines']
        except KeyError:
            log.debug("Account has no trustlines!")
            return []
        marker = lines.get('marker')
        while marker:
            lines = self.get_account_lines(account_id, marker=marker, verbose=verbose)
            account_lines.extend(lines['lines'])
            marker = lines.get('marker')
        return account_lines

    def get_account_offers(self, account_id, limit=None, marker=None, ledger_index="validated", ledger_hash=None,
                           verbose=True):
        if verbose:
            log.info("")
            log.info("Get account offers...")

        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index
            },
        }
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_offers", verbose=verbose)

    def get_account_currencies(self, account, destination_account=None, strict=True, ledger_index="validated",
                               ledger_hash=None, verbose=True):
        if verbose:
            log.info("")
            log.info("Get account currencies...")

        payload = {
            "tx_json": {
                "account": account.account_id,
                "ledger_index": ledger_index,
                "strict": strict
            },
        }
        if destination_account:
            payload["tx_json"]["destination_account"] = destination_account.account_id
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="account_currencies", verbose=verbose)

    def get_gateway_balances(self, account_id, ledger_index="validated", ledger_hash=None,
                             verbose=True):
        if verbose:
            log.info("")
            log.info("Get gateway balances...")

        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index,
                "strict": True
            },
        }
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="gateway_balances", verbose=verbose)

    def get_noripple_check(self, account_id, ledger_index="validated", transactions=True, role="gateway",
                           ledger_hash=None, limit=None,
                           api_version=None, verbose=True):
        if verbose:
            log.info("")
            log.info("Get noripple check...")

        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": ledger_index,
                "role": role,
                "transactions": transactions
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if limit is not None:
            payload["tx_json"]["limit"] = limit
        return self.execute_transaction(payload=payload, method="noripple_check", verbose=verbose)

    def get_ledger_data(self, ledger_index="validated", ledger_type=None, ledger_hash=None, verbose=True, limit=None,
                        marker=None, api_version=None, binary=False):
        if verbose:
            log.info("")
            log.info("Get ledger data...")

        payload = {
            "tx_json": {
                "binary": binary,
                "ledger_index": ledger_index
            },
        }
        if api_version:
            payload["tx_json"]["api_version"] = api_version
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        if limit:
            payload["tx_json"]["limit"] = limit
        if marker:
            payload["tx_json"]["marker"] = marker
        if ledger_type:
            payload["tx_json"]["type"] = ledger_type
        return self.execute_transaction(payload=payload, method="ledger_data", verbose=verbose)

    def get_book_offers(self, response, limit=None, ledger_index="validated", ledger_hash=None, verbose=True):
        if verbose:
            log.info("")
            log.info("Get book offers...")

        taker_gets_currency = "XRP"
        taker_gets_issuer = None
        if "currency" in response["tx_json"]["TakerGets"]:
            taker_gets_currency = response["tx_json"]["TakerGets"]["currency"]
        if "issuer" in response["tx_json"]["TakerGets"]:
            taker_gets_issuer = response["tx_json"]["TakerGets"]["issuer"]
        taker_pays_currency = "XRP"
        taker_pays_issuer = None
        if "currency" in response["tx_json"]["TakerPays"]:
            taker_pays_currency = response["tx_json"]["TakerPays"]["currency"]
        if "issuer" in response["tx_json"]["TakerPays"]:
            taker_pays_issuer = response["tx_json"]["TakerPays"]["issuer"]

        payload = {
            "tx_json": {
                "taker": response["tx_json"]["Account"],
                "taker_gets": {
                    "currency": taker_gets_currency
                },
                "taker_pays": {
                    "currency": taker_pays_currency,
                    "issuer": response["tx_json"]["TakerPays"]["issuer"]
                },
                "ledger_index": ledger_index
            },
        }
        if limit:
            payload["tx_json"]["limit"] = limit
        if taker_gets_issuer:
            payload["tx_json"]["taker_gets"]["issuer"] = taker_gets_issuer
        if taker_pays_issuer:
            payload["tx_json"]["taker_pays"]["issuer"] = taker_pays_issuer
        if ledger_index:
            payload["tx_json"]["ledger_index"] = ledger_index
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash
        return self.execute_transaction(payload=payload, method="book_offers", verbose=verbose)

    def get_ticket_sequence(self, account, verbose=True):
        if verbose:
            log.info("")
            log.info("Get Ticket Sequence...")

        account_objects = self.get_account_objects(account.account_id, verbose=verbose)
        ticket_sequences = []
        for account_object in account_objects["account_objects"]:
            if account_object["LedgerEntryType"] == "Ticket":
                log.debug("Ticket Sequence: {}".format(account_object["TicketSequence"]))
                ticket_sequences.append(account_object['TicketSequence'])

        log.debug("All Ticket Sequences: {}".format(ticket_sequences))
        return ticket_sequences

    def get_xchain_account_claim_count(self, door_account, bridge_type, verbose=True):
        log.debug("Get XChain Account Claim Count")
        account_objects = self.get_account_objects(self.door.account_id, verbose=verbose)
        xchain_account_claim_count = constants.SIDECHAIN_INITIAL_ACCOUNT_CLAIM_COUNT
        for item in account_objects["account_objects"]:
            if "LedgerEntryType" in item and item["LedgerEntryType"] == "Bridge" and \
                    item["XChainBridge"]["LockingChainIssue"]["currency"] == bridge_type:
                xchain_account_claim_count = item["XChainAccountClaimCount"]
                log.debug("XChainAccountClaimCount: {}".format(xchain_account_claim_count))
                break
        return int(xchain_account_claim_count, 16)

    def get_xchain_claim_id(self, response):
        xchain_claim_id = None
        log.debug("Get XChain Claim ID")
        tx_response = self.tx(response["tx_json"]["hash"], verbose=False)
        try:
            for affected_node in tx_response["meta"]["AffectedNodes"]:
                log.debug("Parsing affected node: {}...".format(affected_node))
                try:
                    if "CreatedNode" in affected_node and \
                            affected_node["CreatedNode"]["LedgerEntryType"] == "XChainOwnedClaimID":
                        log.debug("Account object 'XChainOwnedClaimID' found")
                        xchain_claim_id = affected_node["CreatedNode"]["NewFields"]["XChainClaimID"]
                except KeyError as e:
                    pass
        except KeyError as e:
            pass

        if not xchain_claim_id:
            raise Exception("XChainClaimID not found")
        log.info("")
        log.info("XChain Claim ID: {}".format(xchain_claim_id))
        return xchain_claim_id

    def ticket_cancel(self, account_object, ticket_sequence=None):
        log.info("")
        log.info("Ticket Cancel...")

        if not ticket_sequence:
            ticket_sequence = self.get_ticket_sequence(account_object)[0]

        payload = {
            "tx_json": {
                "TransactionType": "AccountSet",
                "Account": account_object.account_id,
                "TicketSequence": ticket_sequence,
            },
            "secret": account_object.master_seed
        }

        return self.execute_transaction(payload=payload)

    def parse_response(self, request_data, response, verbose=True):
        request_print_str = None
        try:
            request_print_str = request_data["method"]
            transaction_type = request_data["params"][0]["tx_json"]["TransactionType"]
            request_print_str = "{} / {}".format(request_print_str, transaction_type)

            ticket_sequence = request_data["params"][0]["tx_json"]["TicketSequence"]
            log.debug("**** Using Ticket Sequence: {}".format(ticket_sequence))
            request_print_str = "{} (** using TicketSequence: {} **)".format(request_print_str, ticket_sequence)

            if request_data["params"][0]["tx_json"]["TransactionType"] == "NFTokenCreateOffer":
                nftoken_create_offer = "Buy Offer"
                nftoken_create_offer_flag = request_data["params"][0]["tx_json"]["Flags"]
                if nftoken_create_offer_flag == constants.NFTOKEN_CREATE_OFFER_SELL_TOKEN:  # tfSellToken
                    log.debug("**** Sell Offer: {}".format(nftoken_create_offer_flag))
                    nftoken_create_offer = "Sell Offer"

                log.debug("**** NFT Offer: {}".format(nftoken_create_offer))
                request_print_str = "{} (** {} **)".format(request_print_str, nftoken_create_offer)
        except KeyError as e:
            pass

        if verbose:
            log.info("  Request: {}".format(request_print_str))
        log.debug(request_data)

        if self.websockets:
            response_result = json.loads(response)
            if response_result.get('status') == 'error':
                response_result['result'] = deepcopy(response_result)
            response_result['result']['status'] = response_result['status']
        else:
            if response.content:
                response_result = json.loads(response.content.decode('utf-8'))
            else:
                return {}

        log.debug("  Response")
        if verbose:
            try:
                log.info("  Response status: {}".format(response_result["result"]["engine_result"]))
            except KeyError:
                log.info("  Response status: {}".format(response_result["result"]["status"]))
        log.debug(response_result['result'])
        return response_result

    def execute_command(self, data, verbose=True):
        response = None
        response_result = None
        engine_result_message = None
        json_data = json.loads(data)

        sequence_passed = False
        try:
            if json_data["params"][0]["tx_json"]["Sequence"]:
                sequence_passed = True
        except KeyError as e:
            pass

        log.debug("Server address: {}".format(self.address))

        retry_required = None
        max_timeout = 120  # in sec waiting for server to sync up
        wait_time = 20  # seconds
        start_time = time.time()
        end_time = start_time + max_timeout
        while time.time() <= end_time and retry_required in (None, True):
            try:
                json_data = json.loads(data)
                if self.websockets:
                    converted_data = self.convert_command(json_data)
                    response = asyncio.run(
                        self.send_command(self.address, converted_data))
                else:
                    response = requests.post(self.address, data)
                    if self.standalone_mode:
                        log.debug("Standalone mode; advancing ledger...")
                        cmd_ledger_advance = "{} --conf {} ledger_accept --silent".format(self.rippled_exec,
                                                                                          self.rippled_config)
                        helper.run_external_command(cmd_ledger_advance, skip_logging=True)

            except KeyError as e:
                pass
            except requests.exceptions.RequestException as e:
                log.error("Failed to establish connection to server: {} - {}".format(self.address, e))
                raise

            if not response:
                log.error("No response received from server: {}".format(response))
                raise Exception("No response received from server: {}".format(response))

            response_result = self.parse_response(json_data, response, verbose=verbose)

            retry_required = False
            if "engine_result" in response_result["result"] and \
                    response_result["result"]["engine_result"] in ("telCAN_NOT_QUEUE_FULL", "telCAN_NOT_QUEUE_FEE"):
                retry_required = True
                engine_result_message = response_result["result"]["engine_result_message"]
                log.warning(
                    "**** {} - Retry after {} seconds...".format(engine_result_message, wait_time))
                time.sleep(wait_time)

            elif "error" in response_result["result"] and "error_code" in response_result["result"] and \
                    response_result["result"]["error_code"] in \
                    (constants.ERROR_CODE_noCurrent, constants.ERROR_CODE_noNetwork):
                retry_required = True
                engine_result_message = response_result["result"]["error_message"]
                log.warning(
                    "**** {} - Retry after {} seconds...".format(engine_result_message, wait_time))
                time.sleep(wait_time)

            # Handle only payloads with no "Sequence" passed to support negative tests
            elif "engine_result" in response_result["result"] and \
                    response_result["result"]["engine_result"] == "tefPAST_SEQ" and not sequence_passed:
                retry_required = True
                engine_result_message = response_result["result"]["engine_result_message"]
                log.warning(
                    "**** {} - Retry after {} seconds...".format(engine_result_message, wait_time))
                time.sleep(wait_time)
                account = json_data["params"][0]["tx_json"]["Account"]
                sequence = self.get_account_sequence(account)
                log.debug("**** Current sequence {}...".format(sequence))
                json_data["params"][0]["tx_json"]["Sequence"] = sequence
                data = json.dumps(json_data)

        if retry_required:
            log.error("********************************************************************************")
            log.error("**** {} - Aborting execution! ****".format(engine_result_message))
            log.error("********************************************************************************")
            raise Exception(engine_result_message)

        self.wait_until_escalated_fee_drops(response_result["result"])
        self.update_account_xrp_balance_with_fee(json_data, response_result["result"], verbose=verbose)
        return response_result['result']

    def get_txn_sequence(self, response, verbose=False):
        log.debug("")
        log.debug("Get transaction sequence...")

        seq = None
        try:
            if "TicketSequence" in response["tx_json"]:
                seq = response["tx_json"]["TicketSequence"]
            else:
                seq = response["tx_json"]["Sequence"]
            self.wait_for_ledger_close(seq, verbose=verbose)
        except KeyError as e:
            pass

        return seq

    def set_signer_list(self, account, signer_entries, signer_quorum, verbose=True):
        if verbose:
            log.info("")
            log.info("Set signer list set...")

        payload = {
            "tx_json": {
                "Flags": 0,
                "TransactionType": "SignerListSet",
                "Account": account.account_id,
                "SignerQuorum": signer_quorum,
                "SignerEntries": signer_entries,
            },
            "secret": account.master_seed
        }
        return self.execute_transaction(payload=payload, verbose=verbose)

    def verify_signer_list(self, response, verbose=True):
        if verbose:
            log.info("")
            log.info("Verify signer list...")

        max_retries = 10
        count = 1
        wait_time = 2  # seconds

        if "SignerEntries" in response["tx_json"]:
            account_id = response["tx_json"]["Account"]
            singer_entries = response["tx_json"]["SignerEntries"]

            while count <= max_retries:
                res = self.get_account_objects(account_id, verbose=False)
                for account_object in res["account_objects"]:
                    if account_object["LedgerEntryType"] == "SignerList" and len(
                            account_object["SignerEntries"]) == len(singer_entries):
                        if verbose:
                            log.info("  verified")
                        return True
                log.debug("Wait {} seconds and retry (attempt: {}/{})".format(wait_time, count, max_retries))
                time.sleep(wait_time)
                count += 1
            raise Exception("'SignerEntries' not in ledger in {} seconds".format(wait_time * max_retries))

    def add_default_fee(self, payload):
        if "Fee" not in payload["tx_json"]:
            log.debug(
                "Adding default fee ({} XRP drops) for this transaction".format(constants.DEFAULT_TRANSACTION_FEE))
            payload["tx_json"]["Fee"] = constants.DEFAULT_TRANSACTION_FEE

    def add_network_id(self, payload):
        if "NetworkID" not in payload["tx_json"] and \
                self.network_id and int(self.network_id) > constants.MAX_LIMIT_NETWORK_ID_NOT_REQUIRED:
            log.debug(f"Adding NetworkID ({self.network_id}) for this transaction")
            payload["tx_json"]["NetworkID"] = self.network_id

    def update_account_xrp_balance_with_fee(self, json_data, response, mode=constants.XRP_DEBIT, verbose=True):
        if "tx_json" in response:
            if json_data["method"] in constants.IGNORE_FEE_INCUR_FOR or \
                    ("engine_result_code" in response and response["engine_result_code"]
                     in constants.IGNORE_FEE_INCUR_FOR):
                log.debug("Not updating XRP usage as this transaction does not incur fee")
            else:
                try:
                    account_id = response["tx_json"]["Account"]
                    if account_id:
                        log.debug("Updating account balance for account: {}".format(account_id))
                        txn_fee = int(response["tx_json"]["Fee"])
                        if account_id in Account.xrp_balance[self].keys():
                            Account.xrp_balance[self][account_id] -= txn_fee
                            log.debug("{} {} for account '{}'".format(txn_fee, mode, account_id))
                            log.debug("Account balance from ledger: {}".format(
                                self.get_account_balance(account_id, verbose=False)))
                            log.debug("XRP Usage updated to: {}".format(Account.xrp_balance[self][account_id]))
                except KeyError as e:
                    # Ignore if account/fee not present in response
                    if verbose:
                        log.warning("Failed to update XRP balance for account in response: {}".format(response))
                        log.warning("Ignoring this failure and proceeding...")

    def wait_until_escalated_fee_drops(self, response):
        log.debug("Verify if transaction is held for escalated fee to be dropped...")
        log.debug("Response: {}".format(response))
        fee_escalated = False
        account_id = None
        # Error response when "Fee of 7200 exceeds the requested tx limit of 100"
        if "error" in response and response["error"] == "highFee" and response["error_code"] == 11:
            log.warning("{} - waiting for escalated fee to be dropped".format(response["error_message"]))
            account_id = response["request"]["tx_json"]["Account"]
            fee_escalated = True
        elif "engine_result" in response and response["engine_result"] == "terQUEUED":
            account_id = response["tx_json"]["Account"]
            fee_escalated = True

        if fee_escalated and account_id:
            max_retries = 60
            wait_time = 2  # second
            count = 1
            notified = False
            transactions = None
            while count <= max_retries:
                try:
                    account_info = self.get_account_info(account_id, verbose=False)
                    txn_count = int(account_info["queue_data"]["txn_count"])

                    if txn_count != 0:
                        transactions = account_info["queue_data"]["transactions"]
                        txn_index = account_info["account_data"]["PreviousTxnID"]
                        if not notified:
                            log.info(
                                "  Wait for escalated fee to be dropped for held transaction: {}".format(txn_index))
                            notified = True
                        time.sleep(wait_time)
                        count += 1
                    else:
                        log.debug("  ** Transaction fee dropped after {} seconds".format(count * wait_time))
                        return
                except KeyError as e:
                    # This response does not have transactions queued
                    return

            log.warning(
                "    Transactions still held after {} seconds: {}".format(max_retries * wait_time, transactions))

    def add_regular_key_to_account(self, account_object, regular_key_account=None, ticket_sequence=None, verbose=True):
        if verbose:
            log.info("")
            log.info("Set regular key pair...")

        if regular_key_account is None:
            # Wallet propose first
            regular_key_account = self.create_account(fund=False, verbose=verbose)

        payload = {
            "tx_json": {
                "TransactionType": "SetRegularKey",
                "Account": account_object.account_id,
                "RegularKey": regular_key_account.account_id,
                "Fee": constants.DEFAULT_TRANSACTION_FEE
            },
            "secret": account_object.master_seed
        }

        if ticket_sequence:
            payload["tx_json"]["TicketSequence"] = ticket_sequence

        # Now send a transaction to set regular key for the account
        response = self.execute_transaction(payload=payload, verbose=verbose)

        # If the above is 200 then remove it from the object
        account_object.regular_key(seed=regular_key_account.master_seed, account=regular_key_account.account_id)

        return regular_key_account

    def remove_regular_key_from_account(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info("Remove regular key pair...")
        payload = {
            "tx_json": {
                "TransactionType": "SetRegularKey",
                "Account": account_object.account_id,
                "Fee": constants.DEFAULT_TRANSACTION_FEE
            },
            "secret": account_object.master_seed
        }
        response = self.execute_transaction(payload=payload)

        # If the above is 200 then remove it from the object
        account_object.regular_key(seed=None, account=None)

    def disable_master_key(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info("Disable master key...")
        return self.account_set(account_object, flag=4, verbose=verbose)

    def enable_deposit_auth(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info("Enable Deposit Auth...")
        return self.account_set(account_object, flag=9, verbose=verbose)

    def disable_deposit_auth(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info("Disable Deposit Auth...")
        return self.account_set(account_object, flag=9, clear_flag=True, verbose=verbose)

    def enable_require_auth(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Setting Auth flag for {account_object.account_id}")
        return self.account_set(account_object, flag=2, verbose=verbose)

    def disable_require_auth(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Setting Auth flag for {account_object.account_id}")
        return self.account_set(account_object, flag=2, clear_flag=True, verbose=verbose)

    def create_trustline(self, account_object, amount, limit=int(1e9), verbose=True):
        trustline_limit = dict(amount, value=limit)

        if verbose:
            log.info("")
            log.info((f"Creating Trustline for {account_object.account_id}"
                      f" for {limit} {amount['currency']}")
                     )
            log.info(f"\tissued by: {amount['issuer']}")

        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_object.account_id,
                "LimitAmount": trustline_limit
            },
        }

        return self.execute_transaction(secret=account_object.master_seed, payload=payload, verbose=verbose)

    def freeze_trustline(self, account_object, amount, verbose=True):
        trustline_limit = dict(amount)

        if verbose:
            log.info("")
            log.info(f"Freezing Trustline for {amount['issuer'][:6]}.{amount['currency']}")

        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_object.account_id,
                "LimitAmount": trustline_limit,
                "Flags": constants.FLAGS_SET_FREEZE_tfSetFreeze
            },
        }
        return self.execute_transaction(secret=account_object.master_seed,
                                        payload=payload,
                                        verbose=verbose)

    def unfreeze_trustline(self, account_object, amount, verbose=True):
        trustline_limit = dict(amount)

        if verbose:
            log.info("")
            log.info(f"Unfreezing Trustline for {amount['issuer'][:6]}.{amount['currency']}")

        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_object.account_id,
                "LimitAmount": trustline_limit,
                "Flags": constants.FLAGS_CLEAR_FREEZE_tfClearFreeze
            },
        }
        return self.execute_transaction(secret=account_object.master_seed,
                                        payload=payload,
                                        verbose=verbose)

    def set_global_freeze(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Set Global Freeze on account {account_object.account_id}...")

        flag = constants.FLAGS_GLOBAL_FREEZE_asfGlobalFreeze
        return self.account_set(account_object, flag=flag, verbose=verbose)

    def unset_global_freeze(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Unset Global Freeze on account {account_object.account_id}...")
        flag = constants.FLAGS_GLOBAL_FREEZE_asfGlobalFreeze
        return self.account_set(account_object, flag=flag, clear_flag=True, verbose=verbose)

    def set_default_ripple(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Set DefaultRipple for account {account_object.account_id}...")

        flag = constants.FLAGS_DEFAULT_RIPPLE_asfDefaultRipple
        return self.account_set(account_object, flag=flag, verbose=True)

    def unset_default_ripple(self, account_object, verbose=True):
        if verbose:
            log.info("")
            log.info(f"Unset DefaultRipple for account {account_object.account_id}...")
        flag = constants.FLAGS_DEFAULT_RIPPLE_asfDefaultRipple
        return self.account_set(account_object, flag=flag, clear_flag=True, verbose=verbose)

    def enable_rippling(self, account_object, amount, verbose=True):
        flag = constants.FLAGS_CLEAR_NORIPPLE_tfClearNoRipple
        trustline_limit = dict(amount)

        if verbose:
            log.info("")
            log.info(f"Allowing rippling for {amount['currency']}")
            log.info(f"\tissued by: {amount['issuer']}")

        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_object.account_id,
                "LimitAmount": trustline_limit,
                "Flags": flag
            },
        }

        return self.execute_transaction(secret=account_object.master_seed,
                                        payload=payload, verbose=verbose)

    def disable_rippling(self, account_object, amount, verbose=True):
        flag = constants.FLAGS_SET_NORIPPLE_tfSetNoRipple
        trustline_limit = dict(amount)

        if verbose:
            log.info("")
            log.info(f"Disabling rippling for {amount['issuer']}.{amount['currency'][:6]}")

        payload = {
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account_object.account_id,
                "LimitAmount": trustline_limit,
                "Flags": flag
            },
        }
        return self.execute_transaction(secret=account_object.master_seed,
                                        payload=payload, verbose=verbose)

    def make_payment(self, source, dest, amount, send_max=None, verbose=True):

        dest = dest if isinstance(dest, str) else dest.account_id

        if verbose:
            log.info("")
            log.info("Submitting Payment")
            log.info(f"\tfrom: {source}")
            log.info(f"\tto:   {dest}")
            log.info(f"\tfor:  {helper.format_currency(amount)}")

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": source.account_id,
                "Destination": dest,
                "Amount": amount
            },
        }

        if send_max is not None:
            payload["tx_json"]["SendMax"] = send_max

        return self.execute_transaction(secret=source.master_seed, payload=payload, verbose=verbose)

    def account_set(self, account_object, flag=None, clear_flag=False, verbose=True, **kwargs):
        log.debug("")
        log.debug("Account Set...")

        account_sequence = self.get_account_sequence(account_object)

        payload = {
            "tx_json": {
                "TransactionType": "AccountSet",
                "Account": account_object.account_id,
                "Sequence": account_sequence,
                "Fee": constants.DEFAULT_TRANSACTION_FEE,
            },
            "secret": account_object.master_seed
        }

        if flag:
            if clear_flag:
                log.debug("  ClearFlag: {}".format(flag))
                payload["tx_json"]["ClearFlag"] = flag
            else:
                log.debug("  SetFlag: {}".format(flag))
                payload["tx_json"]["SetFlag"] = flag
        if kwargs:
            key_val = ", ".join("{}: {}".format(key, val) for key, val in kwargs.items())
            log.debug("  setting new key/values: {}".format(key_val))
            payload["tx_json"].update(kwargs)

        return self.execute_transaction(payload=payload, verbose=verbose)

    def deposit_preauthorize(self, account_object, third_party_account, ticket_sequence=None, verbose=True):
        log.info("")
        log.info("Deposit pre-authorize...")

        payload = {
            "tx_json": {
                "TransactionType": "DepositPreauth",
                "Account": account_object.account_id,
                "Authorize": third_party_account.account_id,
                "Fee": constants.DEFAULT_TRANSACTION_FEE
            },
            "secret": account_object.master_seed
        }

        if ticket_sequence:
            payload["tx_json"]["TicketSequence"] = ticket_sequence

        return self.execute_transaction(payload=payload, verbose=verbose)

    def deposit_unauthorize(self, account_object, third_party_account, verbose=True):
        log.info("")
        log.info("Deposit Un-authorize...")

        payload = {
            "tx_json": {
                "TransactionType": "DepositPreauth",
                "Account": account_object.account_id,
                "Unauthorize": third_party_account.account_id,
                "Fee": constants.DEFAULT_TRANSACTION_FEE
            },
            "secret": account_object.master_seed
        }

        return self.execute_transaction(payload=payload, verbose=verbose)

    def deposit_authorized(self, source_account, destination_account, ledger_index="validated", ledger_hash=None,
                           verbose=True):

        payload = {
            "tx_json": {
                "source_account": source_account.account_id,
                "destination_account": destination_account.account_id,
                "ledger_index": ledger_index
            }
        }
        if ledger_hash:
            payload["tx_json"]["ledger_hash"] = ledger_hash

        return self.execute_transaction(payload=payload, method="deposit_authorized", verbose=verbose)

    def get_server_info(self, verbose=True):
        return self.execute_transaction(method="server_info", verbose=verbose)

    def get_account_sequence(self, account_object_or_id, verbose=False):
        log.debug("")
        log.debug("Get Account sequence...")

        try:
            account_id = account_object_or_id.account_id
        except AttributeError as e:
            account_id = account_object_or_id
        account_info = self.get_account_info(account_id, verbose=verbose)
        account_sequence = account_info["account_data"]["Sequence"]
        return account_sequence

    def get_check_ids(self, account_object, verbose=False):
        account_objects = self.get_account_objects(account_object.account_id, verbose=verbose)
        check_ids = []
        for item in account_objects["account_objects"]:
            if "LedgerEntryType" in item and item["LedgerEntryType"] == "Check":
                log.debug("Check ID: {}".format(item["index"]))
                check_ids.append(item['index'])

        log.info("")
        log.info("Check IDs: {}".format(check_ids))
        return check_ids

    def get_did_ledger_index(self, create_response, verbose=False):
        hash_from_previous_txn = create_response["tx_json"]["hash"]
        tx_response = self.tx(hash_from_previous_txn, verbose=False)
        ledger_index = None
        for affected_node in tx_response["meta"]["AffectedNodes"]:
            for node, node_data in affected_node.items():
                if node_data["LedgerEntryType"] == "DID":
                    ledger_index = node_data["LedgerIndex"]
                    log.info(f"  DID Ledger Index: {ledger_index}")

        return ledger_index

    def get_xchain_signature_reward(self, verbose=False):
        log.debug("Get XChain Signature reward...")
        account_objects = self.get_account_objects(self.door.account_id, verbose=verbose)
        signature_reward = None
        for item in account_objects["account_objects"]:
            if "LedgerEntryType" in item and item["LedgerEntryType"] == "Bridge":
                signature_reward = item["SignatureReward"]
                log.debug("Signature Reward: {}".format(signature_reward))
                break

        if verbose:
            log.info("")
            log.info("SignatureReward: {}".format(signature_reward))
        return signature_reward

    def get_xchain_minimum_account_create_amount(self, verbose=False):
        log.debug("Get XChain minimum account create amoumt...")
        account_objects = self.get_account_objects(self.door.account_id, verbose=verbose)
        minimum_account_create_amount = None
        for item in account_objects["account_objects"]:
            if "LedgerEntryType" in item and item["LedgerEntryType"] == "Bridge" and \
                    item["XChainBridge"]["LockingChainIssue"] == constants.SIDECHAIN_BRIDGE_CURRENCY_XRP:
                minimum_account_create_amount = item["MinAccountCreateAmount"]
                log.debug("MinAccountCreateAmount: {}".format(minimum_account_create_amount))
                break

        if verbose:
            log.info("")
            log.info("MinAccountCreateAmount: {}".format(minimum_account_create_amount))
        return minimum_account_create_amount

    def get_xchain_account_create_count(self, verbose=False):
        log.debug("Get XChain account create count...")
        account_objects = self.get_account_objects(self.door.account_id, verbose=verbose)
        xchain_account_create_count = None
        for item in account_objects["account_objects"]:
            if "LedgerEntryType" in item and item["LedgerEntryType"] == "Bridge" and \
                    item["XChainBridge"]["LockingChainIssue"] == constants.SIDECHAIN_BRIDGE_CURRENCY_XRP:
                xchain_account_create_count = item["XChainAccountCreateCount"]
                log.debug("XChainAccountCreateCount: {}".format(xchain_account_create_count))
                break

        log.debug("")
        log.info("XChainAccountCreateCount: {}".format(xchain_account_create_count))
        return xchain_account_create_count

    def get_channel_ids(self, account):
        account_channels = self.get_account_channels(account.account_id)
        channel_ids = []
        for channel in account_channels["channels"]:
            log.debug("Channel ID: {}".format(channel["channel_id"]))
            channel_ids.append(channel["channel_id"])

        log.info("")
        log.info("Channel IDs: {}".format(channel_ids))
        return channel_ids

    def is_account_created(self, account, fund, verbose=True):
        if not fund:
            return True

        if verbose:
            log.info("  wait for account to be added to ledger...")
        max_retries = 15
        count = 1
        wait_time = 2  # seconds
        while count <= max_retries:
            res = self.get_account_objects(account.account_id, verbose=verbose)
            if "account" in res and res["account"] == account.account_id:
                return True

            log.debug("Wait {} seconds and retry for account to be validated (attempt: {}/{})".format(wait_time, count,
                                                                                                      max_retries))
            time.sleep(wait_time)
            count += 1

        log.warning("  Account not added to ledger in {} seconds".format(wait_time * max_retries))
        return False

    def wait_before_executing_transaction(self, wait_time=0, epoch_wait_time=None, verbose=True):
        log.info("")
        log.info("Wait for ledger parent time to advance...")

        if epoch_wait_time:
            wait_time = epoch_wait_time - int(time.time()) + constants.RIPPLE_EPOCH
        else:
            epoch_wait_time = self.get_rippled_epoch_time(wait_time)

        log.debug("Waiting for {} seconds...".format(wait_time))
        ledger_close_time = self.get_ledger_close_time(verbose=False)
        log.info("  Waiting until ledger close time {} exceeds {}...".format(ledger_close_time, epoch_wait_time))

        sleep_time = 2  # seconds
        while ledger_close_time <= epoch_wait_time:
            if verbose:
                log.info("  Wait {} seconds and retry for ledger close time {} to exceed {} [set wait time]...".
                         format(sleep_time, ledger_close_time, epoch_wait_time))
            time.sleep(sleep_time)
            ledger_close_time = self.get_ledger_close_time(verbose=False)

        log.info("  Ledger close time {} exceeds wait time {}".format(ledger_close_time, epoch_wait_time))
        log.info("")

    def wait_for_ledger_close(self, seq, verbose=True):
        if verbose:
            log.info("")
            log.info("Waiting for ledger close...")

        max_timeout = 30  # max sec for ledger close
        start_time = time.time()
        end_time = start_time + max_timeout
        while time.time() <= end_time:
            current_ledger = self.ledger_current(verbose=verbose)
            if int(current_ledger) < int(seq):
                if verbose:
                    log.info(
                        "Waiting for leger to close. Current ledger at {} [target: {}]".format(current_ledger, seq))
                time.sleep(1)
            else:
                if verbose:
                    log.info("Ledger closed. Current ledger at {} [target: {}]".format(current_ledger, seq))
                return True

        return False

    def update_xrp_balance_with_txn_amount(self, account_id, amount, mode):
        log.debug("")
        log.debug("Update account balance...")
        if isinstance(amount, int) or isinstance(amount, str):
            try:
                if mode == constants.XRP_DEBIT:
                    log.debug("Debit {} from account {}".format(amount, account_id))
                    Account.xrp_balance[self][account_id] -= int(amount)
                elif mode == constants.XRP_CREDIT:
                    log.debug("Credit {} from account {}".format(amount, account_id))
                    Account.xrp_balance[self][account_id] += int(amount)
                else:
                    log.warning("Not updating XRP balance for account '{}'".format(account_id))
            except KeyError as e:
                log.debug("** Account balance not initialized for: {} **".format(e))
        else:
            # TODO: Handle balance update for non-xrp
            log.debug("Not updating non-xrp balance for account '{}'".format(account_id))

        log.debug("{} {} for account '{}' [updated balance: {}]".format(amount, mode, account_id,
                                                                        Account.xrp_balance[self][account_id]))

    def update_account_sequence(self, payload):
        if "Account" in payload["tx_json"]:
            account_id = payload["tx_json"]["Account"]

            if "TicketSequence" in payload["tx_json"]:
                Account.last_recorded_account_sequence[self][account_id] = self.get_account_sequence(account_id) - 1
            elif "Sequence" in payload["tx_json"]:
                Account.last_recorded_account_sequence[self][account_id] = payload["tx_json"]["Sequence"]
            else:
                Account.last_recorded_account_sequence[self][account_id] = self.get_account_sequence(account_id)

            log.debug("")
            log.debug("'last recorded account sequence' for {} updated to: {}".format(
                account_id, Account.last_recorded_account_sequence[self][account_id]))

    def get_last_recorded_account_sequence(self, account_id):
        log.debug("")
        log.debug("Get XRP balance...")
        return Account.last_recorded_account_sequence[self][account_id]

    def get_xrp_balance(self, account_id):
        log.debug("")
        log.debug("Get XRP balance...")
        if self.name == constants.CLIO_SERVER_NAME:
            log.debug("Clio server: Account registered in rippled")
            return Account.xrp_balance[self.rippled][account_id]
        return Account.xrp_balance[self][account_id]

    def set_xrp_balance(self, account_id, balance):
        log.debug("")
        log.debug("Set XRP balance...")
        try:
            Account.xrp_balance[self][account_id] = int(balance)
            log.debug("Balance set for: {}/{}/{}".format(self.name, account_id, Account.xrp_balance[self][account_id]))
        except KeyError as e:
            raise Exception("Account balance not initialized for: {}".format(account_id))

    def is_transaction_validated(self, response=None, tx_id=None, engine_result="tesSUCCESS", max_timeout=30,
                                 verbose=True):
        if verbose:
            log.info("Wait for transaction to be validated...")

        perform_txn_validation = False
        if tx_id:
            perform_txn_validation = True
        elif response:
            log.debug("Response to verify: {}".format(response))
            tx_id = response["tx_json"]["hash"]
            if "engine_result" in response:
                if response["engine_result"] == "tesSUCCESS" or response["engine_result"] == "terQUEUED" or \
                        response["engine_result"] == "tecKILLED":  # OfferCreate tecKILLED flag
                    perform_txn_validation = True
            elif response["status"] == "success":
                perform_txn_validation = True
        else:
            log.error("'response' or 'tx_id' should be passed")

        if perform_txn_validation:
            log.debug("Transaction ID: '{}'".format(tx_id))
            start_time = time.time()
            end_time = start_time + max_timeout
            transaction_result = None
            while time.time() <= end_time:
                tx_response = self.tx(tx_id, verbose=False)
                if "validated" in tx_response:
                    log.debug("Txn response \"validated\": {}".format(tx_response["validated"]))
                    if "meta" in tx_response:
                        transaction_result = tx_response["meta"]["TransactionResult"]
                    if tx_response["validated"]:
                        if response and response["engine_result"] == "terQUEUED":
                            log.debug("  As expected, transaction is validated")
                            return True
                        else:
                            if tx_response["meta"]["TransactionResult"] == engine_result:
                                log.debug("  As expected, transaction is validated")
                                return True
                log.debug("  Wait for a second and retry...")
                time.sleep(1)
            log.info("  Transaction not validated: {} ({})".format(tx_id, transaction_result))

        return False

    def advance_ledger_with_transactions(self, num_of_txns):
        log.info("")
        log.info("Creating {} transactions to advance ledger faster...".format(num_of_txns))

        account_1 = self.create_account(fund=True, verbose=False)
        account_2 = self.create_account(fund=True, verbose=False)

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": account_1.account_id,
                "Destination": account_2.account_id,
                "Amount": "10"
            },
            "secret": account_1.master_seed
        }

        for i in range(0, num_of_txns + 1):
            payment_response = self.execute_transaction(payload=payload, wait_for_ledger_close=False, verbose=False)

    def wait_for_ledger_to_advance_for_account_delete(self, account, num_of_seq=256):
        self.advance_ledger_with_transactions(num_of_seq)
        log.info("")
        log.info("Wait for current ledger index to be {} more than account sequence ({})...".format(
            num_of_seq,
            self.get_account_sequence(account)))

        count = 1
        account_1_sequence = ledger_sequence = 0
        while (ledger_sequence - account_1_sequence) <= num_of_seq:
            account_1_sequence = self.get_account_sequence(account)
            ledger_sequence = self.ledger_current(verbose=False)
            if (count % 60) == 1:
                log.info("  Current ledger index {} is {} less for {}. Retrying...".format(ledger_sequence, (
                        account_1_sequence + num_of_seq - ledger_sequence), (account_1_sequence + num_of_seq)))
            time.sleep(1)
            count += 1

    def update_request_to_forward_to_rippled(self, request, method):
        if method != "submit" and method in constants.METHODS_NOT_IMPLEMENTED_IN_CLIO:
            log.info("Adding ledger_index as current to forward the request from Clio to rippled")
            request["params"][0]["ledger_index"] = "current"
        return request

    def xchain_validation(self, payload, txn_hash):
        amount = None
        dest_account_id = None
        reward_from_account_id = None
        xchain_attestion = "XChainClaimAttestations"
        xchain_proof_sig = "XChainClaimProofSig"
        xchain_validated = False
        transaction_type = payload["tx_json"]["TransactionType"]
        log.debug("Transaction hash: {}".format(txn_hash))
        tx_response = self.tx(txn_hash, verbose=False)
        for affected_node in tx_response["meta"]["AffectedNodes"]:
            log.debug("Parsing affected node: {}...".format(affected_node))
            try:
                if affected_node["DeletedNode"]["LedgerEntryType"] in \
                        ("XChainOwnedClaimID", "XChainOwnedCreateAccountClaimID"):
                    if transaction_type == "XChainClaim":
                        dest_account_id = payload["tx_json"]["Destination"]
                        reward_from_account_id = payload["tx_json"]["Account"]
                        amount = payload["tx_json"]["Amount"]
                    elif transaction_type in ("XChainAddClaimAttestation", "XChainAddAccountCreateAttestation"):
                        if affected_node["DeletedNode"]["LedgerEntryType"] == "XChainOwnedCreateAccountClaimID":
                            log.debug("DeletedNode for ledger type: XChainOwnedCreateAccountClaimID")
                            xchain_attestion = "XChainCreateAccountAttestations"
                            xchain_proof_sig = "XChainCreateAccountProofSig"
                        dest_account_id = \
                            affected_node["DeletedNode"]["FinalFields"][xchain_attestion][0][xchain_proof_sig][
                                "Destination"]
                        reward_from_account_id = payload["tx_json"]["Account"]
                        amount = affected_node["DeletedNode"]["FinalFields"][xchain_attestion][0][
                            xchain_proof_sig]["Amount"]

                    if affected_node["DeletedNode"]["LedgerEntryType"] == "XChainOwnedCreateAccountClaimID" and \
                            self.get_account_info(dest_account_id, verbose=False)["account_data"]["Flags"] == \
                            constants.FLAGS_DEPOSIT_AUTH_ENABLED:
                        log.debug("XChainOwnedCreateAccountClaimID on a preauth enabled account. Not updating balance")
                    else:
                        self.update_xrp_balance_with_txn_amount(dest_account_id, amount, mode=constants.XRP_CREDIT)

                    if affected_node["DeletedNode"]["LedgerEntryType"] == "XChainOwnedCreateAccountClaimID":
                        signature_reward = int(
                            affected_node["DeletedNode"]["FinalFields"][xchain_attestion][0][
                                xchain_proof_sig]["SignatureReward"])
                        log.debug("Reward amount already taken out of XChainAccountCreateCommit owner")
                    else:
                        signature_reward = int(self.get_xchain_signature_reward())

                        log.debug("Remove reward amount ({}) from XChainClaimID owner ({})...".
                                  format(signature_reward, reward_from_account_id))
                        self.update_xrp_balance_with_txn_amount(reward_from_account_id,
                                                                signature_reward,
                                                                mode=constants.XRP_DEBIT)

                    xchain_claim_attestations = affected_node["DeletedNode"]["FinalFields"][
                        xchain_attestion]
                    reward_amount = int(signature_reward / len(xchain_claim_attestations))
                    for xchain_claim_attestation in xchain_claim_attestations:
                        reward_account_id = xchain_claim_attestation[xchain_proof_sig]["AttestationRewardAccount"]
                        log.debug("** Rewarding account '{}': {} drops".format(reward_account_id, reward_amount))
                        self.update_xrp_balance_with_txn_amount(reward_account_id, reward_amount,
                                                                mode=constants.XRP_CREDIT)
                        xchain_validated = True

                    log.debug("** Credit reward balance (if any) to owner of XChainClaim...")
                    self.update_xrp_balance_with_txn_amount(reward_from_account_id,
                                                            signature_reward % len(
                                                                xchain_claim_attestations),
                                                            mode=constants.XRP_CREDIT)
                    break
            except KeyError as e:
                log.debug("key '{}' not found".format(e))

        return xchain_validated

    def on_message(self, ws, message, end_time):
        if time.time() < end_time:
            log.info(f'{message[0:100]}...')
            message = json.loads(message)
            self.stream_queue.put(message)
            self.stream_list.append(message)

    def on_error(self, ws, error):
        log.info("Error:", error)

    def on_close(self):
        log.debug("WebSocket connection closed")
        self.stream_list.clear()

    def on_open(self, ws, payload=None):
        log.info("WebSocket connection opened")
        with self.stream_queue.mutex:
            self.stream_queue.queue.clear()
        if payload:
            ws.send(json.dumps(payload))

    def start_websockets_connection(self, payload=None, max_stream_timeout=None):
        log.info("For streaming related tests....")
        start_time = time.time()
        end_time = start_time + float(max_stream_timeout)

        # Create a WebSocket connection
        ws = websocket.WebSocketApp(self.address,
                                    on_open=lambda ws: self.on_open(ws, payload),
                                    on_message=lambda ws, message: self.on_message(ws, message, end_time),
                                    on_error=lambda ws, error: self.on_error(ws, error), on_close=self.on_close())
        return ws

    def start_streaming_thread(self, payload, max_stream_timeout=constants.MAX_STREAM_TIMEOUT):
        ws = self.start_websockets_connection(payload, max_stream_timeout)
        ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
        ws_thread.start()
        time.sleep(5)
        return ws

    def close_streaming_thread(self, ws):
        stream_data = copy.deepcopy(self.stream_list)
        ws.close()
        log.debug(stream_data)
        return stream_data

    def send_request_to_existing_ws(self, ws, payload):
        ws.send(json.dumps(payload))
        time.sleep(2)
