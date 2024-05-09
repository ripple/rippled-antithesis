#!/usr/bin/env python
import os
import sys
import time

import pytest

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import helper

log = log_helper.get_logger()


@pytest.mark.collect_stats
def test_get_counts(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    prometheus_handle = fx_rippled["prometheus_handle"]

    # TODO: Remove the items in the list after Issue https://github.com/ripple/rippled/issues/3953 is fixed
    keys_permitted_with_zero_value = [
        "historical_perminute",
        "node_reads_duration_us",
        "write_load",
        "read_queue",
        "read_threads_running",
        "SLE_hit_rate",
    ]

    payload = {
        "tx_json": {
            "min_count": 100
        }
    }
    get_counts_response = rippled_server.execute_transaction(payload=payload, method="get_counts")
    assert get_counts_response["status"] == "success", "Failed to get counts"

    log.info("")
    for key, value in get_counts_response.items():
        log.info("{} : {}".format(key, value))

        if prometheus_handle:
            metric = "{}:{}".format(key.replace('::', '_'), value)
            prometheus_handle.send_metric(metric=metric)

    for key, value in get_counts_response.items():
        if key not in keys_permitted_with_zero_value and helper.is_number(value):
            if isinstance(value, str):
                assert int(value) != 0, "value '{}' reported for '{}'".format(value, key)
            else:
                assert value != 0, "value '{}' reported for '{}'".format(value, key)
