import json
import os
import sys

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer
from rippled_automation.rippled_end_to_end_scenarios.sidechain.witnesses import Witnesses
from rippled_automation.rippled_end_to_end_scenarios.sidechain import sidechain_helper

log = log_helper.get_logger()
REQUIRED_BALANCE_IN_MASTER_ACCOUNT = str(
    int(constants.DEFAULT_ACCOUNT_BALANCE) * constants.MAX_NO_OF_ACCOUNTS_FOR_A_TEST_RUN)


def get_sidechain_config(rippled_standalone_mode, network):
    config = constants.SIDECHAIN_STANDALONE_CONFIG if rippled_standalone_mode \
        else constants.SIDECHAIN_NETWORK_CONFIG[network]
    log.debug("Sidechain config: {}".format(config))
    return config


def is_sidechain_created(chains, xchain_bridge_create):
    sidechain_created = False
    for chain in chains:
        account_objects = chain.get_account_objects(chain.door.account_id, verbose=False)
        try:
            for account_object in account_objects["account_objects"]:
                if account_object["LedgerEntryType"] == "Bridge":
                    if xchain_bridge_create:
                        if account_object['XChainClaimID']:
                            sidechain_created = True

                            if not account_object['XChainClaimID'] == "0":
                                log.error("XChain bridge already exists for the configs used in this run")
                                return sidechain_created
                    else:
                        if account_object['XChainClaimID']:
                            sidechain_created = True
                        else:
                            log.error("XChainClaimID not found")
                            break
        except KeyError as e:
            log.debug("Key not found: {}".format(e))
            break
    return sidechain_created


def setup_reward_account(chains, witnesses_info, account_exists=False):
    if account_exists:
        log.info("  Retrieve reward accounts...")
    else:
        log.info("  Create reward accounts...")
    for chain in chains:
        log.debug("  {}: Creating reward accounts...".format(chain.name))
        chain_name = "LockingChain" if chain.name == constants.MAINCHAIN_NAME else "IssuingChain"

        reward_accounts = {}
        for witness_index, witness_info in witnesses_info.items():
            witness_config = witnesses_info[witness_index]["config"]
            with open(witness_config, "r") as fp:
                witness_data = json.load(fp)
            log.debug("witness config data: {}".format(witness_data))
            reward_account_id = witness_data[chain_name]["RewardAccount"]

            wallet = chain.create_wallet_from_account_id(account_id=reward_account_id)
            if not account_exists:
                log.debug("Create/fund account: {}...".format(reward_account_id))
                reward_accounts[witness_index] = chain.create_account(wallet=wallet, fund=True, verbose=False)
                # TODO: Add validation
            else:
                log.debug("Initialize account balance for: {}...".format(reward_account_id))
                reward_accounts[witness_index] = chain.create_account(wallet=wallet, verbose=False)
                chain.set_xrp_balance(reward_account_id, chain.get_account_balance(reward_account_id, verbose=False))
        chain.reward_accounts = reward_accounts


def get_iou_currency(chains, witnesses_info):
    iou_currency = None
    for chain in chains:
        log.debug("  {}: Fetch IOU currency...".format(chain.name))
        chain_name = constants.WITNESS_CONFIG_MAINCHAIN_NAME if chain.name == constants.MAINCHAIN_NAME else \
            constants.WITNESS_CONFIG_SIDECHAIN_NAME
        for witness_index, witness_info in witnesses_info.items():
            witness_config = witnesses_info[witness_index]["config"]
            with open(witness_config, "r") as fp:
                witness_data = json.load(fp)
            log.debug("witness config data: {}".format(witness_data))
            iou_currency = witness_data["XChainBridge"]["{}Issue".format(chain_name)]["currency"]
            log.debug("{}: IOU currency: {}".format(chain.name, iou_currency))
            break

        chain.iou_currency = iou_currency


def get_txn_submit_mode(chains, witnesses, standalone_mode):
    txn_submit = False
    for chain in chains:
        if standalone_mode:
            log.debug("  {}: Fetch auto-submit mode...".format(chain.name))
            chain_name = constants.WITNESS_CONFIG_MAINCHAIN_NAME if chain.name == constants.MAINCHAIN_NAME else \
                constants.WITNESS_CONFIG_SIDECHAIN_NAME
            witnesses_info = witnesses.bridge_info[constants.SIDECHAIN_BRIDGE_TYPE_XRP]
            for witness_index, witness_info in witnesses_info.items():
                witness_config = witnesses_info[witness_index]["config"]
                with open(witness_config, "r") as fp:
                    witness_data = json.load(fp)
                log.debug("witness config data: {}".format(witness_data))
                if "TxnSubmit" in witness_data[chain_name] and witness_data[chain_name]["TxnSubmit"]["ShouldSubmit"]:
                    txn_submit = True
                log.debug("{}: ShouldSubmit: {}".format(chain.name, txn_submit))
                break
        else:
            txn_submit = True  # network mode

        chain.txn_submit = txn_submit
    witnesses.txn_submit = txn_submit


def get_admin_mode_info(witnesses):
    for bridge_type, witnesses_info in witnesses.bridge_info.items():
        admin_info = {}
        for witness_index, witness_info in witnesses_info.items():
            witness_config = witnesses_info[witness_index]["config"]
            with open(witness_config, "r") as fp:
                witness_data = json.load(fp)
            log.debug("witness config data: {}".format(witness_data))
            admin_info[witness_index] = witness_data["Admin"] if "Admin" in witness_data else None
        log.debug("{} bridge admin info: {}".format(bridge_type, admin_info))
        witnesses.admin_info[bridge_type] = admin_info


def reset_reward_account_balances(chains):
    # Reset reward account balances before every test. This avoids the following test not to fail,
    # because of the previous failure/balance mismatch
    log.debug(
        "Re-calculate reward accounts so that the rest of the tests would start "
        "with correct reward account balance...")
    for chain in chains:
        for index, reward_account in chain.reward_accounts.items():
            reward_account_id = reward_account.account_id
            log.debug("Resetting balance for {}".format(reward_account_id))
            chain.set_xrp_balance(reward_account_id, chain.get_account_balance(reward_account_id, verbose=False))


def fund_issuing_chain_master_account(mainchain, sidechain, network_setup=False):
    log.info("  Create/Fund issuing chain master account [{}]...".format(constants.ISSUING_CHAIN_MASTER_ACCOUNT_ID))
    if mainchain.standalone_mode or network_setup:
        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": constants.MASTER_ACCOUNT_ID,
                "Destination": constants.ISSUING_CHAIN_MASTER_ACCOUNT_ID,
                "Amount": REQUIRED_BALANCE_IN_MASTER_ACCOUNT,
            },
            "secret": constants.MASTER_ACCOUNT_SEED
        }
        response = sidechain.execute_transaction(payload=payload, verbose=False)  # Submit payment on sidechain
        # TODO: Check for account balance validation before and after

    else:
        payload = {
            "tx_json": {
                "Account": constants.MASTER_ACCOUNT_ID,
                "Destination": constants.ISSUING_CHAIN_MASTER_ACCOUNT_ID,
                "TransactionType": "XChainAccountCreateCommit",
                "Amount": REQUIRED_BALANCE_IN_MASTER_ACCOUNT,
                "SignatureReward": mainchain.get_xchain_signature_reward(),
                "XChainBridge": {
                    "LockingChainDoor": mainchain.door.account_id,
                    "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                    "IssuingChainDoor": sidechain.door.account_id,
                    "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP
                }
            },
            "secret": constants.MASTER_ACCOUNT_SEED
        }
        # Submit XChainAccountCreate on mainchain
        response = mainchain.execute_transaction(payload=payload, verbose=False)
        # TODO: Check for account balance validation before and after

    wallet = sidechain.create_wallet_from_account_id(account_id=constants.ISSUING_CHAIN_MASTER_ACCOUNT_ID,
                                                     master_seed=constants.ISSUING_CHAIN_MASTER_ACCOUNT_MASTER_SEED)
    sidechain.issuing_chain_master_account = sidechain.create_account(wallet=wallet, verbose=False)


def create_trustlines_on_door_accounts(chains, bridge_type):
    if bridge_type != constants.SIDECHAIN_BRIDGE_TYPE_XRP:
        for chain in chains:
            log.debug("  {}: Enable rippling for {}...".format(chain.name, bridge_type))
            # Enable rippling to move currency all the way to IOU door
            chain.account_set(chain.issuer, flag=8, verbose=False)  # asfDefaultRipple

            if chain.name == constants.MAINCHAIN_NAME:
                log.debug("  {}: Add Trustline...".format(chain.name))
                payload = {
                    "tx_json": {
                        "TransactionType": "TrustSet",
                        "Account": chain.iou_door.account_id,
                        "LimitAmount": {
                            "currency": chain.iou_currency,
                            "issuer": chain.issuer.account_id,
                            "value": str(int(constants.DEFAULT_TRANSFER_AMOUNT) * 100),
                        },
                    },
                    "secret": chain.iou_door.master_seed
                }
                rsp = chain.execute_transaction(payload=payload, verbose=False)
            else:
                log.debug("Skipping Trustline for issuing chain as issuer is the door account")


def setup_sidechain(sidechain_setup_config, standalone_mode, xchain_bridge_create=False, network_setup=False):
    bridge_types = []
    mainchain = None
    sidechain = None
    witness_servers = {}
    log.debug("**** Sidechain config: {}".format(sidechain_setup_config))
    if os.path.isfile(sidechain_setup_config):
        with open(sidechain_setup_config, "r") as fp:
            sidechain_config_data = json.load(fp)
            log.debug("Sidechain setup config data: {}".format(sidechain_config_data))

        for bridge, bridge_info in sidechain_config_data["bridges"].items():
            bridge_types.append(bridge)

        for chain in sidechain_config_data["chains"]:
            chain_name = chain["name"]
            log.debug("  Initialize '{}' rippled handle...".format(chain_name))
            chain_host = "{}:{}".format(chain["http_ip"], chain["http_port"])

            chain_object = RippledServer(address=chain_host, server_name=chain_name, rippled_exec=chain["rippled"],
                                         rippled_config=chain["config"],
                                         standalone_mode=standalone_mode)
            if chain_name == constants.MAINCHAIN_NAME:
                mainchain = chain_object
            elif chain_name == constants.SIDECHAIN_NAME:
                sidechain = chain_object
        chains = [mainchain, sidechain]

        for bridge_type in bridge_types:
            log.debug("  Initialize '{}' door account...".format(bridge_type))
            for chain in chains:
                door_account_info = sidechain_config_data["bridges"][bridge_type]["door_accounts"][
                    "{}_door".format(chain.name)]
                log.debug("door_account_info: {}".format(door_account_info))
                if standalone_mode or network_setup:
                    door_account = chain.create_account(seed=door_account_info["seed"], verbose=False)
                else:
                    wallet = chain.create_wallet_from_account_id(account_id=door_account_info["id"])
                    door_account = chain.create_account(wallet=wallet, verbose=False)
                if bridge_type == constants.SIDECHAIN_BRIDGE_TYPE_XRP:
                    chain.door = door_account
                else:
                    chain.iou_door = door_account

        bridge_info = {}
        for bridge_type in bridge_types:
            log.debug("  Fetching '{}' bridge info...".format(bridge_type))
            bridge_info[bridge_type] = {}
            witness_servers[bridge_type] = {}
            for index, witness in enumerate(sidechain_config_data["bridges"][bridge_type]["witnesses"]):
                log.debug("Parsing witness {}: {}".format(index, witness))
                witness_address = "{}:{}".format(witness["ip"], witness["rpc_port"])
                witness_info = {
                    "name": witness["name"],
                    "witnessd": witness["witnessd"],
                    "config": witness["config"],
                    "host": witness_address,
                    # Get handle of each witness; not Witnesses()
                    "server": RippledServer(address=witness_address, server_type=constants.SERVER_TYPE_WITNESS)
                }
                bridge_info[bridge_type][index] = witness_info
                witness_servers[bridge_type][index] = witness_info["server"]
            log.debug("{} Bridge info: {}".format(bridge_type, bridge_info[bridge_type]))
        xrp_bridge = bridge_info[constants.SIDECHAIN_BRIDGE_TYPE_XRP]
        if constants.SIDECHAIN_BRIDGE_TYPE_IOU in bridge_info:
            get_iou_currency(chains, bridge_info[constants.SIDECHAIN_BRIDGE_TYPE_IOU])

        if xchain_bridge_create:
            log.info("Setting up xChain bridge...")
            sidechain_created = is_sidechain_created(chains, xchain_bridge_create)
            assert not sidechain_created, "XChain bridge already exists for the configs used in this run"

            log.info("  Create door accounts...")
            mainchain.fund_account(account_id=mainchain.door.account_id, verbose=False)

            for chain in chains:
                log.debug("  {}: Creating IOU door account...".format(chain.name))
                chain.fund_account(account_id=chain.iou_door.account_id, verbose=False)

            log.debug("  Assign issuer accounts...")
            mainchain.issuer = mainchain.create_account(seed=constants.LOCKING_CHAIN_IOU_ISSUER_SEED, fund=True,
                                                        verbose=False)
            sidechain.issuer = sidechain.iou_door

            setup_reward_account(chains, xrp_bridge)

            signer_quorum = int(constants.SIDECHAIN_WITNESS_QUORUM * (len(xrp_bridge)))
            for bridge_type in bridge_types:
                create_trustlines_on_door_accounts(chains, bridge_type)
                log.info("  Create '{}' signer list...".format(bridge_type))
                signer_entries = sidechain_helper.create_signer_entries(rippled_server=mainchain,
                                                                        bridge=bridge_info[bridge_type],
                                                                        verbose=False)
                log.info("  Create '{}' bridge...".format(bridge_type))
                for chain in chains:
                    if bridge_type == constants.SIDECHAIN_BRIDGE_TYPE_XRP:
                        door_account = chain.door
                        bridge = {
                            "LockingChainDoor": mainchain.door.account_id,
                            "LockingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                            "IssuingChainDoor": sidechain.door.account_id,
                            "IssuingChainIssue": constants.SIDECHAIN_BRIDGE_CURRENCY_XRP,
                        }
                    else:
                        door_account = chain.iou_door
                        src_chain_issue = {
                            "currency": chain.iou_currency,
                            "issuer": mainchain.issuer.account_id,
                        }
                        dst_chain_issue = {
                            "currency": chain.iou_currency,
                            "issuer": sidechain.issuer.account_id,
                        }
                        bridge = {
                            "LockingChainDoor": mainchain.iou_door.account_id,
                            "LockingChainIssue": src_chain_issue,
                            "IssuingChainDoor": sidechain.iou_door.account_id,
                            "IssuingChainIssue": dst_chain_issue,
                        }

                    log.debug("  {}: Adding signer list...".format(chain.name))
                    response = chain.set_signer_list(account=door_account, signer_entries=signer_entries,
                                                     signer_quorum=signer_quorum, verbose=False)
                    assert chain.verify_signer_list(response, verbose=False)
                    # TODO: Disable master key on issuing chain

                    log.debug("  {}: Creating bridge '{}'...".format(chain.name, bridge_type))
                    payload = {
                        "tx_json": {
                            "Account": door_account.account_id,
                            "TransactionType": "XChainCreateBridge",
                            "XChainBridge": bridge,
                            "SignatureReward": constants.SIGNATURE_REWARDS[chain.name]
                        },
                        "secret": door_account.master_seed
                    }
                    if bridge_type == constants.SIDECHAIN_BRIDGE_TYPE_XRP:
                        payload["tx_json"]["MinAccountCreateAmount"] = constants.DEFAULT_ACCOUNT_BALANCE
                    chain.execute_transaction(payload=payload, verbose=False)
        else:
            log.info("Fetching XChain bridge info...")
            setup_reward_account(chains, xrp_bridge, account_exists=True)

            if standalone_mode:
                mainchain.issuer = mainchain.create_account(seed=constants.LOCKING_CHAIN_IOU_ISSUER_SEED, verbose=False)
                sidechain.issuer = sidechain.iou_door

        sidechain_created = is_sidechain_created(chains, xchain_bridge_create)
        assert sidechain_created, "XChain bridge doesn't exist"

        mode = "Standalone" if mainchain.standalone_mode else "Network"
        log.info("")
        for chain in chains:
            log.info("**** {}: {} ({})".format(chain.name, chain.address,
                                               chain.get_rippled_version(verbose=False)))
            if constants.SIDECHAIN_BRIDGE_TYPE_IOU in bridge_info:
                log.info("     XRP door: {}, IOU door: {}, reward: {}".format(chain.door.account_id,
                                                                              chain.iou_door.account_id,
                                                                              chain.get_xchain_signature_reward()))
                log.debug("**** {} issuer: {}".format(chain.name, chain.issuer.account_id))

            else:
                log.info("     XRP door: {}, reward: {}".format(chain.door.account_id,
                                                                chain.get_xchain_signature_reward()))
            log.debug("**** {} reward accounts: {}".format(chain.name, ", ".join(
                "{}".format(account.account_id) for index, account in chain.reward_accounts.items())))

        if mainchain.standalone_mode:
            log.info("**** Witness servers [Quorum: {}%]: {}".format(constants.SIDECHAIN_WITNESS_QUORUM * 100,
                                                                     ", ".join("{}".format(val["host"])
                                                                               for key, val in xrp_bridge.items())))

        witnesses = Witnesses(bridge_info=bridge_info, servers=witness_servers)
        get_txn_submit_mode(chains, witnesses, standalone_mode)
        get_admin_mode_info(witnesses)
        log.info("**** AddAttestation (auto-submit): {}".format(witnesses.txn_submit))
        log.info("**** Mode: {}".format(mode))
        return mainchain, sidechain, witnesses
    else:
        log.error("Sidechain config '{}' not found".format(sidechain_setup_config))
        raise Exception("Sidechain config '{}' not found".format(sidechain_setup_config))
