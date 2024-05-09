#!/bin/sh

################################################################################
# This test is to run repeated iterations of build rippled on new db followed by
# `collect_stats` tests, and build rippled on existing db, followed by
# `collect_stats` tests.
# Metric `rippled_sync_time` along with labels `rippled_db_type` (new/exisiting)
# and `rippled_version` are pushed to prometheus
#
# Usage: sh rippled_automation/rippled_end_to_end_scenarios/build_and_run_tests/build_test.sh
#     [--network <devnet/testnet/mainnet (default: devnet)]
#
# Example:
# $ screen sudo sh rippled_automation/rippled_end_to_end_scenarios/build_and_run_tests/build_test.sh [--network mainnet]
#
################################################################################

script_path="$(pwd)"/$(dirname "${0}")
network="devnet"
rippled_automation_repo_path="${script_path}/../../../"
local_rippled_repo_path="/space/workspace/rippled"
rippled_db_path="/var/lib/rippled/db"
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

rippled_db_path_defined=$(grep "${rippled_db_path}" "${rippled_automation_repo_path}/configs/rippled/${network}/rippled.cfg")
if [ -z "${rippled_db_path_defined}" ]; then
  echo "**** Update 'rippled_db_path' to match with the definition in ${rippled_automation_repo_path}/configs/rippled/${network}/rippled.cfg"
  exit 1
fi

while :
do
  echo "Clean up logs older than 1 day..."
  find "${rippled_automation_repo_path}"/logs/product_logs -type d -ctime +1 -exec rm -rf {} \;
  find "${rippled_automation_repo_path}"/logs/test_logs -type d -ctime +1 -exec rm -rf {} \;
  find /space/workspace/logs -type f -mtime +1 -exec rm -rf {} \;

  echo "**** Build rippled with a new db ****"
  if [ -f "${rippled_db_path}/ledger.db" ] ; then
    echo "Deleting exiting rippled db: ${rippled_db_path} ..."
    rm -rf "${rippled_db_path:?}"/*
  fi

  sh "${rippled_automation_repo_path}"/scripts/build_and_run_tests.sh \
  --automationRepoPath "${rippled_automation_repo_path}" \
  --localRippledRepoPath "${local_rippled_repo_path}" \
  --skipUnitTests true --publishStats true --network "${network}" \
  --testMarker collect_stats --runCount 1

  echo "Sleep for $run_interval seconds..."
  sleep $run_interval

  echo "**** Build rippled with exiting db ****"
  sh "${rippled_automation_repo_path}"/scripts/build_and_run_tests.sh \
  --automationRepoPath "${rippled_automation_repo_path}" \
  --localRippledRepoPath "${local_rippled_repo_path}" \
  --skipUnitTests true --publishStats true --network "${network}" \
  --testMarker collect_stats --runCount 1

  echo "Sleep for $run_interval seconds..."
  sleep $run_interval
done
