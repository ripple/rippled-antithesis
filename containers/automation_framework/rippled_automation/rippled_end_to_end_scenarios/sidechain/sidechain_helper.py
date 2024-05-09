import json
from rippled_automation.rippled_end_to_end_scenarios.utils import helper, log_helper
from ..end_to_end_tests import constants
import pytest

log = log_helper.get_logger()


def create_signer_entries(rippled_server, bridge, signer_weight=1, verbose=True):
    if verbose:
        log.info("")
        log.info("Create signer entries...")
    signer_entries = []
    for witness_index, witness_info in bridge.items():
        witness_config = bridge[witness_index]["config"]
        with open(witness_config, "r") as fp:
            witness_data = json.load(fp)
        log.debug("witness config data: {}".format(witness_data))
        signer_account = rippled_server.create_account(seed=witness_data["SigningKeySeed"],
                                                       key_type=witness_data["SigningKeyType"],
                                                       verbose=False)
        log.debug("Signer account: {}".format(signer_account.account_id))
        signer_entry = {
            "SignerEntry": {
                "Account": signer_account.account_id,
                "SignerWeight": signer_weight
            }
        }
        signer_entries.append(signer_entry)
    log.debug("signerEntries: {}".format(signer_entries))
    return signer_entries


def assign_chains(fx_rippled, src_chain_name):
    mainchain = fx_rippled["rippled_server"]
    sidechain = fx_rippled["sidechain"]

    if src_chain_name == constants.SKIP_TEST_FOR_SOURCE_CHAIN:
        pytest.skip("Skipping test for source chain as {}".format(src_chain_name))

    if src_chain_name == constants.MAINCHAIN_NAME:
        src_chain = mainchain
        dest_chain = sidechain
    else:
        src_chain = sidechain
        dest_chain = mainchain

    log.info("Scenario: {} -> {}".format(src_chain.name, dest_chain.name))
    return src_chain, dest_chain


def reached_quorum(witnesses, bridge_type, witness_index):
    signer_quorum = witnesses.get_quorum(bridge_type)
    return True if (witness_index + 1) == signer_quorum else False
