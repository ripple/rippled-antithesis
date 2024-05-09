#!/bin/sh

################################################################################
# This test is to run repeated iterations of memory leak testsuite.
#
# Usage: sh rippled_automation/rippled_end_to_end_scenarios/build_and_run_tests/memory_leak_test.sh
#     [--network <devnet/testnet (default: devnet)]
#
# Example:
# $ screen sudo sh rippled_automation/rippled_end_to_end_scenarios/build_and_run_tests/memory_leak_test.sh
#
################################################################################

script_path="$(pwd)"/$(dirname "${0}")
network="devnet"
rippled_automation_repo_path="${script_path}/../../../"
local_rippled_repo_path="/space/workspace/rippled"
run_interval=10800  # 3 hrs

usage() {
  echo "Usage: $0 [Optional parameters]"
  echo "  --network <devnet/testnet/mainnet (default: $network)>"
  echo "  --localRippledRepoPath <local rippled repo path for building rippled>"
  exit 1
}

while [ "$1" != "" ]; do
  case $1 in
  --network)
    shift
    network="${1:-$network}"
    ;;

  --localRippledRepoPath)
    shift
    local_rippled_repo_path="${1:-$local_rippled_repo_path}"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

echo "automation repo: ${rippled_automation_repo_path}"
echo "rippled repo: ${local_rippled_repo_path}"

if [ ! -d "${local_rippled_repo_path}" ] ; then
  echo "Default rippled path not found: ${local_rippled_repo_path}"
  usage
fi

while :
do
  echo "Clean up logs older than 1 day..."
  find "${rippled_automation_repo_path}"/logs/product_logs -type d -ctime +1 -exec rm -rf {} \;
  find "${rippled_automation_repo_path}"/logs/test_logs -type d -ctime +1 -exec rm -rf {} \;
  find /space/workspace/logs -type f -mtime +1 -exec rm -rf {} \;

  sh "${rippled_automation_repo_path}"/scripts/build_and_run_tests.sh \
  --automationRepoPath "${rippled_automation_repo_path}" \
  --localRippledRepoPath "${local_rippled_repo_path}" \
  --skipUnitTests true --publishStats true --network "${network}" \
  --launchViaValgrind true --runTests memleak --runCount 1

  echo "Sleep for $run_interval seconds..."
  sleep $run_interval
done
