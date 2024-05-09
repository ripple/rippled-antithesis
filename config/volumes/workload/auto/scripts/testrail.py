import argparse
import json
import os
import requests
import sys
import time
from datetime import datetime

import rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.constants as constants

DEFAULT_REPORT = os.path.join(os.path.dirname(__file__), '../.report.json')
headers = {'Content-Type': 'application/json'}
auth = ('rsg@ripple.com', 'jo0VNF1o4j8OgJ4m75gs-OC1b5wUSwDiZWU5VRYYA')
s = requests.Session()
s.headers.update(headers)

TESTRAIL_URL = "https://testrippled.testrail.io/index.php?"
API_V = "/api/v2"
BASE_URL = f"{TESTRAIL_URL}{API_V}"

default_job_id = "LocalRun"

project_ids = {
    constants.TESTRAIL_DEFAULT_PROJECT: 1,  # rippled
    constants.TESTRAIL_CLIO_PROJECT: 6
}

status = {
    "passed": 1,
    "rerun": 1,
    "skipped": 2,
    "failed": 5,
    "error": 5,
}


def execute_query(action="GET", **kwargs):
    response = None
    tries_left = 25
    wait_time = 5  # seconds
    while tries_left:
        try:
            if action == "GET":
                response = s.get(kwargs["uri"], auth=auth)
            else:
                response = s.post(kwargs["query"], json=kwargs["json_body"], auth=auth)
        except requests.RequestException as e:
            print("Error: Couldn't reach Testrail! " + repr(e))

        if not response or not response.ok:
            print(f"Response status: {response}")
            tries_left -= 1

            if tries_left:
                print(f"Retry in {wait_time} second(s)")
                time.sleep(wait_time)
        else:
            return response

    raise Exception("Error communicating with testrail")


def post_query(query, json_body):
    return execute_query(action="POST", query=query, json_body=json_body)


def get_query(uri):
    return execute_query(action="GET", uri=uri)


def create_new_run(job_id, run_type, network, rippled_version):
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    test_cycle_name = f"{job_id} - {dt_string} - {run_type} - {network} - {rippled_version}"

    print(f"Creating test cycle for Job ID: {job_id}")
    print(f"Test cycle name: {test_cycle_name}")

    feature = get_testrun_info(key=constants.KEY_NAME_FEATURE)
    project_id = project_ids[feature] if project_ids.get(feature) else project_ids[constants.TESTRAIL_DEFAULT_PROJECT]

    query = f"{BASE_URL}/add_run/{project_id}"
    body = {"name": test_cycle_name}

    response = post_query(query=query, json_body=body)
    return response.json()['id']


def get_tests_in_run(run_id):
    # BUG: This still overwrites results with the same title
    # It can't just return a list if test names aren't unique.
    # Perhaps we could identify them by case_id or something?
    raw_response = get_query(f"{BASE_URL}/get_tests/{run_id}")
    response = raw_response.json()
    next_link = response.get('_links').get('next')
    tests = response['tests']
    all_tests = {test['title']: test['case_id'] for test in tests}

    while next_link:
        response = get_query(f"{TESTRAIL_URL}{next_link}").json()
        next_link = response.get('_links').get('next')
        tests = response['tests']
        for test in tests:
            title = test['title']
            id_ = test['case_id']
            all_tests.update({title: id_})
    return all_tests


def get_test_from_report(json_report):
    with open(json_report, "r") as myfile:
        data = myfile.readlines()

    report_results = json.loads(data[0])['tests']
    test_results = {}
    for test in report_results:
        test_name = test['nodeid'].split("::", 1)[1]
        outcome = test['outcome']

        if outcome == 'failed':
            message = test['call']['crash']['message']
            outcome = [outcome, message]

        test_results[test_name] = outcome

    return test_results


def update_results(run_id, actual_results, tests_in_run):
    results = []
    result_messages = []
    for test_name, test_result in actual_results.items():
        test_result_str = test_result if isinstance(test_result, str) else test_result[0]
        result_message = f"{test_name} -> {test_result_str}"

        if test_result_str != 'passed':
            result_messages.append(result_message)

        try:
            result = {"case_id": tests_in_run[test_name], "status_id": status[test_result_str]}
            if isinstance(test_result, list) and test_result_str == 'failed':
                result['comment'] = test_result[1]
            results.append(result)

        except KeyError:
            print(f"ERROR: Test '{test_name}' not found in testrail")
            sys.exit(1)

    query = f"{BASE_URL}/add_results_for_cases/{run_id}"
    response = post_query(query=query, json_body={"results": results})

    for msg in result_messages:
        print(msg)

    print(f"Status: {response.status_code}")
    return response.ok


def get_testrun_info(key):
    value = None
    if os.path.exists(constants.TESTRUN_INFO_FILE):
        with open(constants.TESTRUN_INFO_FILE, "r") as fp:
            data = json.load(fp)

        if key == constants.KEY_NAME_RIPPLED_VERSION and not data[key]:
            key = constants.KEY_NAME_CLIO_RIPPLED_VERSION

        try:
            value = data[key]
        except KeyError as e:
            print(repr(e))
    return value


def main(job_id, run_type, network, rippled_version, json_report):
    if any(arg is None for arg in (job_id, run_type, network, rippled_version)):
        raise Exception("Required parameter is None")

    run_id = create_new_run(job_id, run_type, network, rippled_version)
    tests_in_run = get_tests_in_run(run_id)
    actual_results = get_test_from_report(json_report)
    update_succeeded = update_results(run_id, actual_results, tests_in_run)

    if not update_succeeded:
        print("Error updating results")
        sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobID', help=f"Job ID creating this test set (default: {default_job_id})",
                        default=default_job_id)
    parser.add_argument('--network', help="testnet/devnet/mainnet", default=None, required=True)
    parser.add_argument('--runType', help="nightly/smoke", default=None, required=True)
    parser.add_argument('--jsonReport', help="pytest json report", default=DEFAULT_REPORT, required=True)
    parser.add_argument('--rippledVersion',
                        help="Rippled version", default=get_testrun_info(key=constants.KEY_NAME_RIPPLED_VERSION))
    arguments = parser.parse_args()
    print(arguments)
    return arguments


if __name__ == "__main__":
    args = parse_arguments()
    main(args.jobID, args.runType, args.network, args.rippledVersion, args.jsonReport)
