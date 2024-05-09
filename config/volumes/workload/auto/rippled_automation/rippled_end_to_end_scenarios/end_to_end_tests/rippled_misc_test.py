#!/usr/bin/env python
import os
import shutil
import sys
import time
import pytest
from shutil import copyfile

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper

log = log_helper.get_logger()

"""
This test is do a safety check on the LedgerEntryType & TxType
rippled source files:
- src/ripple/protocol/LedgerFormats.h
- src/ripple/protocol/TxFormats.h

Spec: https://github.com/ripple/rippled/commit/af5f28cbf8861996b1bb5c35cf16bd28401916dc
"""


def get_key(data, val):
    if isinstance(data, dict):
        data_list = [data]
    else:
        data_list = data
    matched_keys = []
    for item in data_list:
        for k, v in item.items():
            if val == v:
                log.debug("Value '{}' matched for key '{}'".format(v, k))
                matched_keys.append(k)

    log.debug("Matched keys: {}".format(matched_keys))
    return matched_keys


def get_last_assigned_value(data_list, key):
    last_updated_val = None
    for item in data_list:
        for k, v in item.items():
            if k == key:
                log.debug("Key '{}' matched".format(k))
                last_updated_val = v

    log.debug("Last updated value: {}".format(last_updated_val))
    return last_updated_val


def validator(fx_rippled, src_file, type_prefix):
    reference_file = os.path.join("data", "reference_{}".format(os.path.basename(src_file)))
    updated_reference_file = os.path.join(fx_rippled["log_dir"], os.path.basename(reference_file))

    if not os.path.isfile(src_file):
        pytest.skip("rippled source file '{}' not found".format(src_file))
    else:
        if os.path.isfile(reference_file):
            shutil.copyfile(reference_file, updated_reference_file)
        else:
            assert False, "{} not found".format(reference_file)

        # Verify key, value from src file (example: LedgerFormats.h)
        current_dict = {}
        with open(src_file, "r") as fp:
            log.info("")
            for line in fp:
                line_to_verify = line.strip()
                if line_to_verify.startswith(type_prefix):
                    key = line_to_verify.split(' ')[0]
                    val = line_to_verify.split(' ')[-1]
                    val = val.split(',')[0]
                    log.info("{}={}".format(key, val))
                    assert key not in current_dict.keys(), "Duplicate Type '{}' found".format(key)
                    assert val not in current_dict.values(), \
                        "Value for Type '{}' duplicates an existing key '{}={}'".format(
                            key, get_key(current_dict, val)[0], val)

                    current_dict[key] = val

        # Load key, value from reference file and parse
        reference_list = []
        reference_file_updated = False
        with open(updated_reference_file, "r+") as fp:
            for line in fp:
                line_to_verify = line.strip()
                key, val = line_to_verify.split('=')
                reference_list.append({key: val})

            for key, val in current_dict.items():
                log.debug("")
                log.debug("Does value '{}' have a matching key in reference file?".format(val))
                reference_key = get_key(reference_list, val)
                if not reference_key:
                    log.info("** Updating reference file: '{}={}'...".format(key, val))
                    fp.write("{}={}".format(key, val))
                    fp.write("\n")
                    reference_file_updated = True
                else:
                    assert reference_key[0] == key, "Type '{}' duplicates an existing value '{}={}'".format(
                        key, reference_key[0], val)
                    last_assigned_value = get_last_assigned_value(reference_list, key)
                    assert last_assigned_value == val, "Value '{}' was assigned to '{}' in the past".format(val, key)

        if reference_file_updated:
            log.info("")
            log.info("**** Updated reference file to review: {}".format(updated_reference_file))
            log.info("**** Replace '{}', and check-in.".format(reference_file))
            assert False, "** Test Passed: Marking as failed to review & check-in updated reference file. " \
                          "Check details in test output."


def test_ledger_entry_type(fx_rippled):
    rippled_repo = fx_rippled["rippled_repo_path"]

    src_file = os.path.join(rippled_repo, "src/ripple/protocol/LedgerFormats.h")
    type_prefix = "lt"

    validator(fx_rippled, src_file, type_prefix)


def test_tx_type(fx_rippled):
    rippled_repo = fx_rippled["rippled_repo_path"]

    src_file = os.path.join(rippled_repo, "src/ripple/protocol/TxFormats.h")
    type_prefix = "tt"

    validator(fx_rippled, src_file, type_prefix)
