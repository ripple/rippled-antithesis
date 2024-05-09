#!/usr/bin/env sh
set +e

################################################################################
# Script to run automated tests
#
# Usage: sh run_tests.sh
#     [--network <devnet/testnet (default: devnet)]
#     [--hostname <validator IP to run tests against (default: localhost)>]
#     [--port <listening port of validator to run tests against (default: 51234)>]
#     [--runType <nightly/smoke>] (default on CI runs: all tests except longrun (MR),
#                                  default on local runs: smoke)
#     [--jobID <generated from CI pipeline. Not required for local/manual run>]
#     [--publishTestResults true] (to publish test results to testrail)
#     [--standaloneMode true] (to run tests in standalone mode)
#
# To run memory leak test:
# 1. prerequisite: Run rippled via valgrind
# sh install_rippled.sh --mode build --localRippledRepoPath <local rippled repo path> --startRippled --launchViaValgrind true
# 2. Run test:
# sh run_test.sh --runType memleak --standaloneMode true
################################################################################

exit_status=1
network="devnet"
run_type="MR"
run_count=1
job_id="LocalRun"
job_name="<Set job_name in scheduler>"
tag_string="<Set job_owner in scheduler>"
publish_test_results="None"
run_type_override="None"
host_name="localhost"
port=51234
clio_host="clio.devnet.rippletest.net"
clio_port=51233
standalone_mode=""
memory_leak_summary_file=$(dirname "$(pwd)")/memory_leak_summary_file.txt
memory_leak_buffer=100
max_time_to_run_memleak_tests=7200  # default max time to run memory leak tests: 2 hrs
publish_stats="None"
pytest_marker=""
use_websockets="false"
websockets_port=6006
log_level="INFO"
constants_file="rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/constants.py"
constants_bkp_file="${constants_file}.bkp"
rippled_exec="/opt/ripple/bin/rippled"
rippled_config="/opt/ripple/etc/rippled.cfg"
rippled_repo_path="$HOME/rippled"
xchain_bridge_create="None"
standalone_mode="None"
slack_notify="false"
testrun_pids=""
test_results_dir="logs/test_results"
json_report_file="testrun_report.json"
multiple_test_suites_in_parallel="false"
AUTOMATION_TMP_DIR="/tmp/automation_work_dir"  # NOTE: referenced in constants.py
TEST_RUN_PID_TEST_SUITE_KEY="test_suite"  # NOTE: referenced in constants.py
TEST_RUN_PID_TEST_RESULT_DIR_KEY="results_dir"  # NOTE: referenced in constants.py
TEST_RUN_RESULTS_SUMMARY_FILE="${AUTOMATION_TMP_DIR}/test_run_results.txt"


trap 'script_teardown 1' INT

exit_on_error() {
  exit_code=$1
  exit_message="$2"

  if [ $exit_code -ne 0 ]; then
    echo "${exit_message} (${exit_code})"

    if [ "${slack_notify}" = "true" ]; then
      slack_message="${exit_message}"
      if [ "${job_id}" != "LocalRun" ]; then
        ci_job_url="https://gitlab.ops.ripple.com/xrpledger/automation/-/jobs/${job_id}"
        if [ -n "${job_owner}" ]; then
          tag_string="<@${job_owner}>"
        fi
        slack_message=":fire: \`${job_name}\` - ${ci_job_url} ${tag_string} - ${slack_message}"
      fi
      echo "** Send slack notification: ${slack_message}"
      python3 -m scripts.slack_notification --message "${slack_message}"
    fi

    script_teardown "$exit_code"
  fi
}

usage() {
  echo "Usage: $0 [Optional parameters]"
  echo "  --hostname <validator IP to run tests against (default: $host_name)>"
  echo "  --port <listening port of validator to run tests against (default: $port)>"
  echo "  --clioHost <validator IP to run tests against (default: $clio_host)>"
  echo "  --clioPort <listening port of validator to run tests against (default: $clio_port)>"
  echo "  --network <devnet/testnet (default: $network)>"
  echo "  --runType <nightly/smoke (default: $run_type)>"
  echo "  --testMarker <pytest marker to run custom set of tests>"
  echo "  --testFilter <test filter to run custom set of tests based on test name>"
  echo "  --jobID <generated from CI pipeline. Not required for local/manual run>"
  echo "  --publishTestResults true (to publish test results to testrail)"
  echo "  --publishStats true (to publish stats to prometheus)"
  echo "  --standaloneMode true (to run rippled tests in standalone mode)"
  echo "  --rippled <rippled exec path for standalone mode> (default: $rippled_exec)"
  echo "  --rippledConfig <rippled config path for standalone mode> (default: $rippled_config)"
  echo "  --rippledRepoPath <OPTIONAL: rippled repo path for rippled source testing> (default: $rippled_repo_path)"
  echo "  --xchainBridgeCreate true (Create new xchain bridge. default: ${xchain_bridge_create})"
  echo "  --runCount <no. of iteration to run this test (default: $run_count, forever: -1)>"
  echo "  --useWebsockets true (Run tests on websockets interface (default: $use_websockets))"
  echo "  --websocketsPort <listening port of validator to run tests against (default: $websockets_port)>"
  echo "  --logLevel <Set log level (default: $log_level)>"
  exit 1
}

update_constants_for_standalone_mode() {
  echo "Update constants for standalone mode..."
  cp "${constants_file}" "${constants_bkp_file}"

  sed -i.tmp 's/^TEST_GENESIS_ACCOUNT_ID.*/TEST_GENESIS_ACCOUNT_ID = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"/g' "${constants_file}"
  sed -i.tmp 's/^TEST_GENESIS_ACCOUNT_SEED.*/TEST_GENESIS_ACCOUNT_SEED = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"/g' "${constants_file}"
  sed -i.tmp 's/^DEFAULT_ACCOUNT_BALANCE.*/DEFAULT_ACCOUNT_BALANCE = \"2000000000\"/g' "${constants_file}"
  sed -i.tmp 's/^RUNTIME_FUNDING_ACCOUNT_MAX_BALANCE.*/RUNTIME_FUNDING_ACCOUNT_MAX_BALANCE = \"10000000000000\"/g' "${constants_file}"
  sed -i.tmp 's/^DEFAULT_DELETE_ACCOUNT_FEE.*/DEFAULT_DELETE_ACCOUNT_FEE = \"100000000\"/g' "${constants_file}"

  echo "Following constants are changed:"
  diff "${constants_file}" "${constants_bkp_file}"
}

revert_constants() {
  echo "Revert constants file..."
  cp "${constants_bkp_file}" "${constants_file}"
}

parse_valgrind_log() {
  leak_summary=""
  max_time_to_fetch_leak_summary=60
  if [ -f "/tmp/valgrind_log_filepath.txt" ] ; then
    valgrind_log_file=$(cat "/tmp/valgrind_log_filepath.txt")  # same name as defined in install_rippled.sh
    echo "Valgrind log file: ${valgrind_log_file}"

    if [ -f "${valgrind_log_file}" ] ; then
      echo "Fetch rippled PID..."
      # kill rippled to release from valgrind
      rippled_pid=$(grep "Command:" "${valgrind_log_file}" | cut -d "=" -f3)
      if [ -n "${rippled_pid}" ] ;  then
        echo "Kill rippled (PID: $rippled_pid)"
        kill -TERM "${rippled_pid}"
      fi

      echo "Parsing valgrind log..."
      seconds_elapsed=0
      echo "Wait for valgrind to summarize report within $max_time_to_fetch_leak_summary seconds..."
      while [ $seconds_elapsed -le $max_time_to_fetch_leak_summary ]; do
        leak_summary=$(grep "definitely lost" "${valgrind_log_file}" | cut -d ":" -f2 | cut -d " " -f2 | tr -d ',')
        if [ -n "${leak_summary}" ] ; then
          echo ""
          echo "**** Leak Summary (definitely lost): $leak_summary bytes ****"

          if [ "${publish_stats}" = "true" ] ; then
            echo "  Publishing stats to prometheus..."
            sh scripts/publish_metric.sh --metric memory_leak:${leak_summary} --jobID "$job_id"
          fi

          break
        fi

        sleep 10
        seconds_elapsed=$((seconds_elapsed + 1))
      done
    else
      echo "Valgrind log file not found"
      exit_status=1
    fi
  else
    echo "Valgrind/rippled not started successfully"
    exit_status=1
  fi

  if [ -n "${leak_summary}" ] ; then
    previous_leak=""
    if [ -f "${memory_leak_summary_file}" ] ; then
      previous_leak=$(tail -1 "${memory_leak_summary_file}" | cut -d ',' -f2)
    fi
    echo "$(date '+%m/%d/%Y %T'),${leak_summary}" >> "${memory_leak_summary_file}"

    if [ -z "${previous_leak}" ] ; then
      echo "** 1st time run - Memory leaked **"
      exit_status=1
    else
      leak_diff=$(($leak_summary - $previous_leak))

      if [ "$leak_diff" -gt "$memory_leak_buffer" ] ; then
        echo "** Memory leak spiked **"
        # TODO: Send notification
        exit_status=1
      else
        echo "** Memory leak less than or equal to the leak in previous run ($previous_leak) **"
        exit_status=0
      fi
      echo ""
    fi
  else
    echo "** Error fetching leak summary in $max_time_to_fetch_leak_summary seconds"
    exit_status=1
  fi

}

parse_test_run_status() {
  testrun_pids="$1"

  echo ""
  echo "Test Run Status..."
  for pid in $(echo ${testrun_pids})
  do
    wait "${pid}"
    pid_status=$?
    if [ "${pid_status}" -eq 0 ]; then
      testsuite_status="Pass"
    else
      testsuite_status="Fail"
    fi
    testrun_statuses="${testrun_statuses} ${testsuite_status}"

    test_suite=$(grep "${TEST_RUN_PID_TEST_SUITE_KEY}" "${AUTOMATION_TMP_DIR}/${pid}" | cut -d'=' -f2)
    pid_test_results_dir=$(grep "${TEST_RUN_PID_TEST_RESULT_DIR_KEY}" "${AUTOMATION_TMP_DIR}/${pid}" | cut -d'=' -f2)

    {
      echo "${test_suite} (PID: $pid): ${testsuite_status}"
      echo "${pid_test_results_dir}"
      echo " "
    }  >> "${TEST_RUN_RESULTS_SUMMARY_FILE}"
  done
  echo " "
  echo "************************************************************************************************"
  echo "                                 **** Result Summary ****"
  echo "************************************************************************************************"
  cat "${TEST_RUN_RESULTS_SUMMARY_FILE}"
  echo "************************************************************************************************"

  if [ -n "${testrun_pids}" ] && [ -z "$(echo "${testrun_statuses}" | grep Fail)" ]; then
    exit_status=0
  fi
}
script_teardown() {
  exit_status=${1:-1}
  if [ "${standalone_mode}" = "true" ] ; then
    revert_constants
  fi
  exit ${exit_status}
}

while [ "$1" != "" ]; do
  case $1 in
    --hostname )
      shift
      host_name="${1:-$host_name}"
      ;;

    --port )
      shift
      port="${1:-$port}"
      ;;

    --clioHost )
      shift
      clio_host="${1:-$clio_host}"
      ;;

    --clioPort )
      shift
      clio_port="${1:-$clio_port}"
      ;;

    --network )
      shift
      network="${1:-$network}"
      ;;

    --runType )
      shift
      run_type="${1:-$run_type}"
      run_type_override="true"
      ;;

    --jobID )
      shift
      job_id="${1:-$job_id}"
      ;;

    --jobName)
      shift
      job_name="${1:-$job_name}"
      ;;

    --publishTestResults )
      shift
      publish_test_results="${1:-$publish_test_results}"
      ;;

    --standaloneMode)
      shift
      standalone_mode="${1:-$standalone_mode}"
      ;;

    --rippled)
      shift
      rippled_exec="${1:-$rippled_exec}"
      ;;

    --rippledConfig)
      shift
      rippled_config="${1:-$rippled_config}"
      ;;

    --rippledRepoPath )
      shift
      rippled_repo_path="${1:-rippled_repo_path}"
      ;;

    --xchainBridgeCreate)
      shift
      xchain_bridge_create="${1:-$xchain_bridge_create}"
      ;;

    --maxDurationToRunMemleakTests)
      shift
      max_time_to_run_memleak_tests="${1:-$max_time_to_run_memleak_tests}"
      ;;

    --testMarker)
      shift
      pytest_marker="${1:-$pytest_marker}"
      ;;

    --testFilter)
      shift
      test_filter="${1}"
      ;;

    --publishStats)
      shift
      publish_stats="${1:-$publish_stats}"
      ;;

    --runCount )
      shift
      run_count="$1"
      ;;

    --useWebsockets)
      shift
      use_websockets="${1:-$use_websockets}"
      ;;

    --websocketsPort)
      shift
      websockets_port="${1:-$websockets_port}"
      ;;

    --logLevel )
      shift
      log_level="${1:-$log_level}"
      ;;

    --slackNotify)
      shift
      slack_notify="${1:-$slack_notify}"
      ;;

    --jobOwner)
      shift
      job_owner="$1"
      ;;

    --help | * )
      usage
  esac
  shift
done

rm -rf "${AUTOMATION_TMP_DIR}" "${test_results_dir}"
mkdir -p "${AUTOMATION_TMP_DIR}" "${test_results_dir}"

if [ "${standalone_mode}" = "true" ] ; then
  update_constants_for_standalone_mode
fi

if [ ! "${run_type_override}" = "true" ] ; then
  run_type="smoke" # default run type for local run
fi

if [ "$use_websockets" = "true" ] ; then
  echo "Testing websockets..."
  port=$websockets_port
fi

echo "Beginning tests for network: $network [type: $run_type]"
echo "Job ID: $job_id"

python3 -m pip -q install pytest requests pytest-rerunfailures websockets websocket-client
python3 -m pip -q install pytest-json-report --no-dependencies

iteration=1
if [ $run_count -eq -1 ] ; then
  total_iterations="forever"
else
  total_iterations=$run_count
fi
while :
do
  echo ""
  echo "**** Iteration ${iteration}/${total_iterations} ****"
  if [ -n "$pytest_marker" ] ; then
    echo "Custom test run for pytest marker: $pytest_marker"
    pytest --hostname $host_name --port $port \
      --useWebsockets "${use_websockets}" \
      --standaloneMode "${standalone_mode}" \
      --logLevel "${log_level}" \
      --junitxml="${test_results_dir}/test_results.xml" \
      rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
      -m "${pytest_marker}"
    exit_status=$?

  elif [ "$run_type" = "memleak" ]; then
    echo "Memory leak test run"
    seconds_elapsed=0
    start_time=$(date -u +%s)
    count=1
    while [ $seconds_elapsed -lt $max_time_to_run_memleak_tests ]; do
      echo "** Iteration: $count"
      pytest --hostname $host_name --port $port \
        --useWebsockets "${use_websockets}" \
        --standaloneMode "${standalone_mode}" \
        --logLevel "${log_level}" \
        --junitxml="${test_results_dir}/test_results.xml" \
        --reruns 0 \
        rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
        -m "not daemon_mode_only"
      exit_status=$?
      # TODO: skipping exit_on_error for now, as some tests in checks fail running in standalone mode. They need a fix
      # exit_on_error $exit_status "Memory leak test failed"

      now_in_seconds=$(date -u +%s)
      seconds_elapsed=$(($now_in_seconds - $start_time))
      count=$((count+1))
    done

    parse_valgrind_log

  else
    if [ "$run_type" = "smoke" ] ; then
      if [ -n "$test_filter" ] ; then
        echo "Custom test run on filter: $test_filter"
        pytest --hostname "${host_name}" --port "${port}" \
          --rippled "${rippled_exec}" \
          --rippledConfig "${rippled_config}" \
          --rippledRepoPath "${rippled_repo_path}" \
          --useWebsockets "${use_websockets}" \
          --standaloneMode "${standalone_mode}" \
          --logLevel "${log_level}" \
          --junitxml="${test_results_dir}/test_results.xml" \
          --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
          --publishStats "${publish_stats}" \
          rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
          -k "${test_filter}"
        exit_status=$?

      else
        echo "Smoke test run"
        pytest --hostname "${host_name}" --port "${port}" \
          --rippled "${rippled_exec}" \
          --rippledConfig "${rippled_config}" \
          --rippledRepoPath "${rippled_repo_path}" \
          --useWebsockets "${use_websockets}" \
          --standaloneMode "${standalone_mode}" \
          --logLevel "${log_level}" \
          --junitxml="${test_results_dir}/test_results.xml" \
          --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
          --publishStats "${publish_stats}" \
          rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
          -m "smoke"
        exit_status=$?
      fi

    elif [ "$run_type" = "sidechain" ] ; then
      echo "Sidechain test run"
      pytest --hostname "${host_name}" --port "${port}" \
        --sidechainTests true \
        --xchainBridgeCreate "${xchain_bridge_create}" \
        --standaloneMode "${standalone_mode}" \
        --useWebsockets "${use_websockets}" \
        --logLevel "${log_level}" \
        --junitxml="${test_results_dir}/test_results.xml" \
        --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
        --publishStats "${publish_stats}" \
        rippled_automation/rippled_end_to_end_scenarios/sidechain/ \
        -k "${test_filter}"
      exit_status=$?

    elif [ "$run_type" = "nightly" ]; then
      echo "Nightly test run"
      test_suites_dir="rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests"
      no_of_test_suites=$(find "${test_suites_dir}"/*test.py | wc -l)
      if [ "${no_of_test_suites}" -gt 1 ]; then
        multiple_test_suites_in_parallel="true"
      fi

      # shellcheck disable=SC2045
      for test_suite in $(find "${test_suites_dir}" -name "*test.py" ); do
        echo "Running Testsuite: $test_suite ..."
        test_suite_name=$(basename $test_suite .py)
        pytest --hostname "${host_name}" --port "${port}" \
          --rippled "${rippled_exec}" \
          --rippledConfig "${rippled_config}" \
          --standaloneMode "${standalone_mode}" \
          --useWebsockets "${use_websockets}" \
          --junitxml="${test_results_dir}/${test_suite_name}_results.xml" \
          --logLevel "${log_level}" \
          --json-report --json-report-file="${test_results_dir}/${test_suite_name}_result.json" \
          --publishStats "${publish_stats}" \
          --multipleTestSuiteInParallel "${multiple_test_suites_in_parallel}" \
          "${test_suite}" &
        pid=$!
        echo "${TEST_RUN_PID_TEST_SUITE_KEY}=${test_suite}" > "${AUTOMATION_TMP_DIR}/${pid}"
        testrun_pids="${testrun_pids} ${pid}"
      done
      parse_test_run_status "${testrun_pids}"

    elif [ "$run_type" = "stream" ]; then
      if [ -n "$test_filter" ] ; then
          echo "Custom test run on filter: $test_filter"
          pytest --hostname "${host_name}" --port "${port}" \
            --clioTests true \
            --clioHost "${clio_host}" \
            --clioPort "${clio_port}" \
            --rippled "${rippled_exec}" \
            --rippledConfig "${rippled_config}" \
            --standaloneMode "${standalone_mode}" \
            --useWebsockets true \
            --junitxml="${test_results_dir}/test_results.xml" \
            --logLevel "${log_level}" \
            --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
            --publishStats "${publish_stats}" \
            rippled_automation/rippled_end_to_end_scenarios/stream_tests/ \
            -k "${test_filter}"
          exit_status=$?

      else
        echo "stream test run"
        pytest --hostname "${host_name}" --port "${port}" \
            --clioTests true \
            --clioHost "${clio_host}" \
            --clioPort "${clio_port}" \
            --rippled "${rippled_exec}" \
            --rippledConfig "${rippled_config}" \
            --standaloneMode "${standalone_mode}" \
            --useWebsockets true \
            --junitxml="${test_results_dir}/test_results.xml" \
            --logLevel "${log_level}" \
            --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
            --publishStats "${publish_stats}" \
            rippled_automation/rippled_end_to_end_scenarios/stream_tests/
          exit_status=$?
      fi

    elif [ "$run_type" = "longrun" ]; then
      echo "Longrun test run"
      pytest --hostname "${host_name}" --port "${port}" \
        --rippled "${rippled_exec}" \
        --rippledConfig "${rippled_config}" \
        --standaloneMode "${standalone_mode}" \
        --useWebsockets "${use_websockets}" \
        --junitxml="${test_results_dir}/test_results.xml" \
        --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
        --logLevel "${log_level}" \
        --publishStats "${publish_stats}" \
        rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
        -m "longrun"
      exit_status=$?

    elif [ "$run_type" = "clio" ]; then
      if [ -n "$test_filter" ] ; then
          echo "Custom test run on filter: $test_filter"
          pytest --hostname "${host_name}" --port "${port}" \
            --clioTests true \
            --clioHost "${clio_host}" \
            --clioPort "${clio_port}" \
            --rippled "${rippled_exec}" \
            --rippledConfig "${rippled_config}" \
            --standaloneMode "${standalone_mode}" \
            --useWebsockets "${use_websockets}" \
            --junitxml="${test_results_dir}/test_results.xml" \
            --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
            --logLevel "${log_level}" \
            --publishStats "${publish_stats}" \
            rippled_automation/rippled_end_to_end_scenarios/clio_tests/ \
            -k "${test_filter}"
          exit_status=$?

      else
        echo "clio test run"
        pytest --hostname "${host_name}" --port "${port}" \
          --clioTests true \
          --clioHost "${clio_host}" \
          --clioPort "${clio_port}" \
          --rippled "${rippled_exec}" \
          --rippledConfig "${rippled_config}" \
          --standaloneMode "${standalone_mode}" \
          --useWebsockets "${use_websockets}" \
          --junitxml="${test_results_dir}/test_results.xml" \
          --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
          --logLevel "${log_level}" \
          --publishStats "${publish_stats}" \
          rippled_automation/rippled_end_to_end_scenarios/clio_tests/
        exit_status=$?
      fi

    elif [ "$run_type" = "amm" ]; then
      echo "AMM test run"
      pytest --hostname "${host_name}" --port "${port}" \
        --rippled "${rippled_exec}" \
        --rippledConfig "${rippled_config}" \
        --standaloneMode "${standalone_mode}" \
        --useWebsockets "${use_websockets}" \
        --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
        --junitxml="${test_results_dir}/test_results.xml" \
        --logLevel "${log_level}" \
        --publishStats "${publish_stats}" \
        rippled_automation/rippled_end_to_end_scenarios/amm_tests
      exit_status=$?

    else
      echo "MR test run"
      test_suites_dir="rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests"
      no_of_test_suites=$(find "${test_suites_dir}"/*test.py | wc -l)
      if [ "${no_of_test_suites}" -gt 1 ]; then
        multiple_test_suites_in_parallel="true"
      fi

      # shellcheck disable=SC2045
      for test_suite in $(find "${test_suites_dir}" -name "*test.py" ); do
        echo "Running Testsuite: $test_suite ..."
        test_suite_name=$(basename $test_suite .py)
        pytest --hostname "${host_name}" --port "${port}" \
          --rippled "${rippled_exec}" \
          --rippledConfig "${rippled_config}" \
          --standaloneMode "${standalone_mode}" \
          --useWebsockets "${use_websockets}" \
          --junitxml="${test_results_dir}/${test_suite_name}_results.xml" \
          --logLevel "${log_level}" \
          --json-report --json-report-file="${test_results_dir}/${test_suite_name}_result.json" \
          --publishStats "${publish_stats}" \
          --multipleTestSuiteInParallel "${multiple_test_suites_in_parallel}" \
          -m "not longrun" \
          "${test_suite}" &
        pid=$!
        echo "${TEST_RUN_PID_TEST_SUITE_KEY}=${test_suite}" > "${AUTOMATION_TMP_DIR}/${pid}"
        testrun_pids="${testrun_pids} ${pid}"
      done
      parse_test_run_status "${testrun_pids}"

#      TODO: Uncomment this after this temporary clio issue blocking MR runs is fixed
#      echo "** Running clio tests..."
#      pytest --hostname "${host_name}" --port "${port}" \
#        --rippled "${rippled_exec}" \
#        --rippledConfig "${rippled_config}" \
#        --clioTests true \
#        --clioHost "${clio_host}" \
#        --clioPort "${clio_port}" \
#        --standaloneMode "${standalone_mode}" \
#        --useWebsockets "${use_websockets}" \
#        --junitxml="clio-test_results.xml" \
#        --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
#        --logLevel "${log_level}" \
#        --publishStats "${publish_stats}" \
#        rippled_automation/rippled_end_to_end_scenarios/clio_tests/ \
#        -m "smoke"
#      clio_exit_status=$?
#      exit_status=$(( exit_status|clio_exit_status ))

#      TODO: Uncomment this after this temporary clio issue blocking MR runs is fixed
#      echo "** Running rippled tests on clio host..."
#      pytest --hostname "${clio_host}" --port "${clio_port}" \
#       --useWebsockets "${use_websockets}" \
#       --junitxml="${test_results_dir}/test_results.xml" \
#       --json-report --json-report-file="${test_results_dir}/${json_report_file}" \
#       --logLevel "${log_level}" \
#       --publishStats "${publish_stats}" \
#       rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/ \
#       -m "smoke"
#      clio_exit_status=$?
#      exit_status=$(( exit_status|clio_exit_status ))
    fi
  fi

  if [ "$publish_test_results" = "true" ] ; then
    echo "Updating testrail..."
    # shellcheck disable=SC2045
    for json_report in $(ls "${test_results_dir}"/*.json)
    do
      python3 -m scripts.testrail --network "${network}" \
        --runType "${run_type}" \
        --jobID "${job_id}" \
        --jsonReport "${json_report}"
      exit_on_error $? "Failed to update testrail"
    done
  else
    echo "Skipping testrail update"
  fi

  if [ $iteration -eq $run_count ] ; then
    break
  else
    iteration=$((iteration+1))
  fi
done

if [ "${standalone_mode}" = "true" ] ; then
  revert_constants
fi

echo "Over all test run status: $exit_status"
exit_on_error "$exit_status" "Tests failed"
