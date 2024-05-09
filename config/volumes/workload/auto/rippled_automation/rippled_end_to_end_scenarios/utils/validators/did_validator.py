from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

log = log_helper.get_logger()


def validate_updated_did_object(rippled_server, initial_payload, did_update_response):
    if "engine_result_code" in did_update_response and did_update_response["engine_result_code"] == 0:
        log.info("")
        log.info("Verify updated DID object...")
        updated_params = {}
        for param in initial_payload["tx_json"]:
            if param in constants.DID_PARAMS:
                updated_params[param] = initial_payload["tx_json"][param]

        for param in did_update_response["tx_json"]:
            if param in constants.DID_PARAMS:
                updated_params[param] = did_update_response["tx_json"][param]
        log.debug(f"Updated DID params: {updated_params}")

        ledger_index = rippled_server.get_did_ledger_index(did_update_response)
        ledger_entry_response = rippled_server.get_ledger_entry(index=ledger_index,
                                                                verbose=False)
        for param, value in updated_params.items():
            try:
                assert ledger_entry_response["node"][param] == value, \
                    f"{param}:{value} does not match DID object {param}:{ledger_entry_response['node'][param]}"
                log.info(f"  verified param: '{param}' ({value})")
            except KeyError as e:
                pass
