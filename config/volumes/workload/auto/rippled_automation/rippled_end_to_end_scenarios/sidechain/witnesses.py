import json
import os
import queue
import requests
import sys
import threading
import time

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import helper
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer
log = log_helper.get_logger()


class Witnesses(RippledServer):
    def __init__(self, bridge_info=None, servers=None):
        super().__init__(server_type=constants.SERVER_TYPE_WITNESS)
        self.admin_info = {}
        self.bridge_info = bridge_info
        self.servers = servers
        self.servers_stopped = []

    def set_admin_info(self, payload, bridge_type, witness_index):
        witness_name = self.bridge_info[bridge_type][witness_index]["name"]
        if self.admin_info[bridge_type][witness_index] is None:
            log.info("* {} (*Admin RPC disabled*)".format(witness_name))
        else:
            log.info("* {} (*Admin RPC enabled*)".format(witness_name))
            if "Username" not in payload["tx_json"]:
                log.debug("Setting Admin Username to payload: {}".format(
                    self.admin_info[bridge_type][witness_index]["Username"]))
                payload["tx_json"]["Username"] = self.admin_info[bridge_type][witness_index]["Username"]
            if "Password" not in payload["tx_json"]:
                log.debug("Setting Admin Password to payload: {}".format(
                    self.admin_info[bridge_type][witness_index]["Password"]))
                payload["tx_json"]["Password"] = self.admin_info[bridge_type][witness_index]["Password"]
        log.debug("Payload after reading admin info from witness: {}".format(payload))

    def get_xchain_attestation_claim(self, payload, bridge_type, witness_index=0, method="witness"):
        xchain_attestation_claim = {}
        log.info("")
        log.info("Get witness from...")
        if self.txn_submit:
            log.info("  ** auto-submit **")
            return constants.SIDECHAIN_IGNORE_VALIDATION

        reward_accounts = None
        if "reward_account" in payload["tx_json"]:
            reward_accounts = payload["tx_json"]["reward_account"]
        if method == "witness_account_create":
            try:
                reward_accounts = payload["tx_json"]["reward_account"]
            except KeyError as e:
                log.error("reward_account missing in payload")
                raise Exception("reward_account missing in payload")
            claim_key = "createAccount"
        else:
            claim_key = "claim"

        witness_name = self.bridge_info[bridge_type][witness_index]["name"]
        server = self.bridge_info[bridge_type][witness_index]["server"]
        if witness_name in self.servers_stopped:
            log.info("* {}: not running (skipped)".format(witness_name))
            return constants.SIDECHAIN_IGNORE_VALIDATION
        else:
            self.set_admin_info(payload, bridge_type, witness_index)
            reward_account_id = None
            if reward_accounts:
                reward_account_id = reward_accounts[witness_index].account_id
                payload["tx_json"]["reward_account"] = reward_account_id
            log.debug("Reward account for witness '{}': {}".format(witness_name, reward_account_id))
            log.debug("Payload for witness '{}': {}".format(witness_name, payload))

            witness_response = server.execute_transaction(payload=payload, method=method, verbose=False)
            log.debug("witness response [{}]: {}".format(witness_index, witness_response))
            xchain_attestation_claim = witness_response.get(claim_key, xchain_attestation_claim)

        log.debug("{} [{}]: {}".format(claim_key, witness_index, xchain_attestation_claim))
        return xchain_attestation_claim

    def get_quorum(self, bridge_type):
        signer_quorum = int(constants.SIDECHAIN_WITNESS_QUORUM * (len(self.bridge_info[bridge_type])))
        log.debug("Quorum for {} bridge: {}".format(bridge_type, signer_quorum))
        return signer_quorum

    def get_witness_attribute(self, witness_config, key_path):
        key_path = key_path if isinstance(key_path, list) else [key_path]
        with open(witness_config, "r") as fp:
            witness_data = json.load(fp)
        log.debug("witness config data: {}".format(witness_data))
        value = None
        for key in key_path:
            try:
                value = witness_data[key] if value is None else value[key]
            except KeyError as e:
                log.error("Key not found: {}".format(key))
                raise

        log.debug("Value for witness attibute '{}': {}".format(key, value))
        return value

    def get_witness_info(self, witness_name):
        for bridge_type, witnesses_info in self.bridge_info.items():
            for witness_index, witness_info in witnesses_info.items():
                if witness_name == witness_info["name"]:
                    log.debug(f'Witness server found: {bridge_type}/{witness_info["name"]} [{witness_index}]')
                    return bridge_type, witness_index
        return None, None

    def update_signing_seed(self, witness_index, bridge_type, signing_seed_account, signing_account=None):
        log.info("")
        log.info("Update witness signing seed...")
        witness_server_info = self.bridge_info[bridge_type][witness_index]
        witness_config = witness_server_info["config"]
        with open(witness_config, "r") as fp:
            witness_data = json.load(fp)

        witness_data["SigningKeySeed"] = signing_seed_account.master_seed
        witness_data["SigningAccount"] = signing_seed_account.account_id
        witness_data["SigningKeyType"] = signing_seed_account.key_type
        if signing_account:
            log.debug("Updating 'SigningAccount' to {}".format(signing_account.account_id))
            witness_data["SigningAccount"] = signing_account.account_id

        log.debug("Updated witness config data: {}".format(witness_data))
        with open(witness_config, "w") as fp:
            json.dump(witness_data, fp, indent=2)

    def update_currency(self, witness_index, bridge_type, currency):
        log.info("")
        log.info("Updating 'currency' to {}".format(currency))
        witness_server_info = self.bridge_info[bridge_type][witness_index]
        witness_config = witness_server_info["config"]
        with open(witness_config, "r") as fp:
            witness_data = json.load(fp)

        witness_data["XChainBridge"]["LockingChainIssue"]["currency"] = currency
        witness_data["XChainBridge"]["IssuingChainIssue"]["currency"] = currency

        log.debug("Updated witness config data: {}".format(witness_data))
        with open(witness_config, "w") as fp:
            json.dump(witness_data, fp, indent=2)

    def delete_witness_db(self, witness_index, bridge_type):
        witness_server_info = self.bridge_info[bridge_type][witness_index]
        witness_name = witness_server_info["name"]
        witness_config = witness_server_info["config"]
        db_path = self.get_witness_attribute(witness_config, "DBDir")

        import shutil
        log.info("")
        log.info("Deleting witness '{}' db...".format(witness_name))
        try:
            shutil.rmtree(db_path)
            os.mkdir(db_path)
        except OSError as e:
            log.error("Error deleting {}: {}".format(db_path, e.strerror))

    def witness_server_stop(self, witness_index, bridge_type):
        witness_server_info = self.bridge_info[bridge_type][witness_index]
        witness_name = witness_server_info["name"]
        witness_exec = witness_server_info["witnessd"]
        witness_config = witness_server_info["config"]
        witness_server = self.servers[bridge_type][witness_index]

        log.info("")
        log.info("Stopping witness server: {} [{}]...".format(witness_name, witness_index))
        payload = {
            "tx_json": {
            }
        }
        self.set_admin_info(payload, bridge_type, witness_index)
        if witness_name in self.servers_stopped:
            log.info("  Witness server '{}' is already stopped".format(witness_name))
            stop_status = True
            log.debug("Stopped witness servers: {}".format(self.servers_stopped))
        else:
            witness_server.execute_transaction(payload=payload, method="stop")
            stop_status = helper.wait_for_server_stop(witness_exec, witness_config, cmd=witness_config)
            if stop_status:
                self.servers_stopped.append(witness_name)
                self.bridge_info[bridge_type][witness_index]["server"] = None
                self.servers[bridge_type][witness_index] = None

            log.debug("Stopped witness servers: {}".format(self.servers_stopped))
            status, output = helper.run_external_command("pgrep -lf {}".format(witness_exec), skip_logging=True)
            log.debug("Witnesses in running state:\n{}".format(output))

        return stop_status

    def witness_server_start(self, witness_index, bridge_type, mainchain, sidechain):
        witness_server_info = self.bridge_info[bridge_type][witness_index]
        witness_name = witness_server_info["name"]
        witness_exec = witness_server_info["witnessd"]
        witness_config = witness_server_info["config"]
        witness_address = witness_server_info["host"]

        log.info("")
        log.info("Starting witness server: {} [{}]...".format(witness_name, witness_index))

        cmd_to_start = "{} --conf {} --verbose".format(witness_exec, witness_config)
        helper.run_external_command(cmd_to_start, wait=False)
        time.sleep(1)  # wait for server to be up
        witness_server = RippledServer(address=witness_address, server_type=constants.SERVER_TYPE_WITNESS)

        # Get witness server status
        payload = {
            "tx_json": {
            }
        }
        self.set_admin_info(payload, bridge_type, witness_index)
        start_status = False
        max_timeout = 60  # max sec to set 'initializing' to 'False'
        start_time = time.time()
        end_time = start_time + max_timeout
        while time.time() <= end_time:
            for chain in [mainchain, sidechain]:
                log.debug(f"Advance '{chain}' ledger to trigger witness server to get initialized...")
                cmd_ledger_advance = "{} --conf {} ledger_accept --silent".format(chain.rippled_exec,
                                                                                  chain.rippled_config)
                helper.run_external_command(cmd_ledger_advance, skip_logging=True)

            response = witness_server.execute_transaction(payload=payload, method="server_info", verbose=False)
            log.debug(f"'{witness_name}' server_info: {response}")

            if response["info"]["issuing"]["initiating"] == "False" and \
                    response["info"]["locking"]["initiating"] == "False" and \
                    response["status"] == "success":
                log.info(f"  issuing initiating: {response['info']['issuing']['initiating']}")
                log.info(f"  locking initiating: {response['info']['locking']['initiating']}")
                start_status = True
                break
            time.sleep(1)

        if start_status:
            log.info("  started successfully")
            if witness_name in self.servers_stopped:
                self.servers_stopped.remove(witness_name)
            self.bridge_info[bridge_type][witness_index]["server"] = witness_server
            self.servers[bridge_type][witness_index] = witness_server
        else:
            log.error("** Failed to start")

        log.debug("Stopped witness servers: {}".format(self.servers_stopped))
        status, output = helper.run_external_command("pgrep -lf witness")
        log.debug("Witnesses in running state:\n{}".format(output))

        return start_status


