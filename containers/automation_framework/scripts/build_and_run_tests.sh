#!/bin/sh
set +e

################################################################################
# This script is to build rippled (including the required prerequisites) on a provided rippled repo,
# and optionally run tests (smoke/nightly)
# Subsequent executions of this script builds rippled only if there are any new commits in rippled repo
# or in automation repo that could be affecting the build steps/prerequisites
# Optionally, the stats collected (rippled sync time) can be published to prometheus
#
# Usage: sh scripts/build_rippled_test.sh
#     --automationRepoPath <PATH_TO_AUTOMATION_REPO>
#     --localRippledRepoPath <PATH_TO_RIPPLED_REPO>
#     [--runCount <no. of iteration to run this test (default: forever)>]
#     [--runInterval <Sleep time between iterations (default: 1 hr)>]
#     [--network <devnet/testnet (default: devnet)]
#     [--runTests <smoke/nightly>]
#     [--publishStats true]
#
# Example: To setup a repetitive run on a dedicated host, execute the following command as sudo/root
# $ nohup sudo sh ~/workspace/automation/scripts/build_rippled_test.sh
#     --automationRepoPath ~/workspace/automation
#     --localRippledRepoPath ~/workspace/rippled
#     --publishStats true
#     --runTests smoke &
#
# Exmaple: To run memory leak test (via valgrind in standalone mode)
# $ nohup sudo sh ~/workspace/automation/scripts/build_rippled_test.sh
#     --automationRepoPath ~/workspace/automation
#     --localRippledRepoPath ~/workspace/rippled
#     --launchViaValgrind true
#     --runTests memleak &

################################################################################

network="devnet"
tests_to_run="MR"
run_tests_flag=""
pytest_marker=""
publish_stats="None"
launch_via_valgrind=""
standalone_mode=""
skip_unit_tests=""
local_rippled_repo_path="${HOME}/rippled"
rippled_automation_repo_path="${PWD}"
run_count=1
run_interval=3600  # 1 hr

usage() {
  echo "Usage: $0 <parameters>"
  echo "  --automationRepoPath <automation repo path>"
  echo "  --localRippledRepoPath <local rippled repo path>"
  echo "  --network <devnet/testnet (default: $network)>"
  echo "  --runCount <no. of iteration to run this test (default: $run_count, forever: -1)>"
  echo "  --runInterval <Sleep time between iterations (default: $run_interval)>"
  echo "  --publishStats true (publish stats to prometheus)"
  exit 1
}

validate_repos() {
  if [ ! -d "${rippled_automation_repo_path}/.git" ]; then
    echo "Unable to locate automation repo. Update --automationRepoPath"
    exit 1
  fi

  if [ ! -d "${local_rippled_repo_path}/.git" ]; then
    echo "Unable to locate local rippled repo. Update --localRippledRepoPath"
    exit 1
  fi
}
check_repos_for_new_commits() {
  check_for_new_commit_cmd="git fetch --dry-run 2>&1"

  CWD=$(pwd)
  cd "${rippled_automation_repo_path}"
  new_commits=$(eval sudo -u $(stat -c '%U' "${rippled_automation_repo_path}") "${check_for_new_commit_cmd}")
  if [ "$?" -eq 0 ]; then
    if [ -n "${new_commits}" ]; then
      echo "New commits found. Updating repo..."
      echo "Deleting work dir: ${work_dir}..."
      rm -rf "${work_dir}"
      sudo -u $(stat -c '%U' "${rippled_automation_repo_path}") git pull
    else
      echo "No new commits since last pull"
    fi
  else
    echo "Error executing git command. Make sure repo ${rippled_automation_repo_path} was cloned with user $(stat -c '%U' ${rippled_automation_repo_path})'s key"
    exit 1
  fi

  cd "${local_rippled_repo_path}"
  new_commits=$(eval sudo -u $(stat -c '%U' "${local_rippled_repo_path}") "${check_for_new_commit_cmd}")
  if [ "$?" -eq 0 ]; then
    if [ -n "${new_commits}" ]; then
      echo "New commits found. Updating repo..."
      rm -f "${rippled_built_marker_file}"
      sudo -u $(stat -c '%U' "${local_rippled_repo_path}") git pull
    else
      echo "No new commits since last pull"
    fi
  else
    echo "Error executing git command. Make sure repo ${local_rippled_repo_path} was cloned with user: $(stat -c '%U' ${local_rippled_repo_path})'s key"
    exit 1
  fi

  git log -1
  cd "${CWD}"
}

build_rippled() {
  if [ -f "${rippled_built_marker_file}" ]; then
    echo "Not rebuilding rippled as there is no change in rippled repo. Just starting rippled..."
    sh "${rippled_automation_repo_path}"/install_rippled.sh --automationRepoPath "${rippled_automation_repo_path}" \
      --localRippledRepoPath "${local_rippled_repo_path}" \
      --mode "build" --network "${network}" \
      --publishStats "${publish_stats}" --skipUnitTests "${skip_unit_tests}" \
      --launchViaValgrind "${launch_via_valgrind}" --startRippled
    if [ "$?" -ne 0 ]; then
      echo "Failed to start rippled"
      return 1
    fi
  else
    echo "Building rippled..."
    if [ -f "${rippled_prereq_installed_marker_file}" ]; then
      echo "Skipping prerequisites as this is not the 1st time build on this host"
      sh "${rippled_automation_repo_path}"/install_rippled.sh --automationRepoPath "${rippled_automation_repo_path}" \
        --localRippledRepoPath "${local_rippled_repo_path}" \
        --mode "build" --network "${network}" \
        --ignoreRippledRepoClone --ignoreRippledBuildPrereq \
        --publishStats "${publish_stats}" --skipUnitTests "${skip_unit_tests}" \
        --launchViaValgrind "${launch_via_valgrind}"
      if [ "$?" -ne 0 ]; then
        echo "Failed to build rippled"
        return 1
      fi
    else
      echo "Building rippled for the 1st time on this host (including prerequisites)"
      sh "${rippled_automation_repo_path}"/install_rippled.sh --automationRepoPath "${rippled_automation_repo_path}" \
        --localRippledRepoPath "${local_rippled_repo_path}" \
        --mode "build" --network "${network}" \
        --ignoreRippledRepoClone \
        --publishStats "${publish_stats}" --skipUnitTests "${skip_unit_tests}" \
        --launchViaValgrind "${launch_via_valgrind}"
      if [ "$?" -eq 0 ]; then
        touch "${rippled_prereq_installed_marker_file}"
      else
        echo "Failed to build rippled"
        return 1
      fi
    fi

    touch "${rippled_built_marker_file}"
  fi
}

run_tests() {
  CWD=$(pwd)
  if [ "${run_tests_flag}" = "true" ]; then
    echo "Launching tests..."
    cd "${rippled_automation_repo_path}"
    sh "${rippled_automation_repo_path}"/run_test.sh --network "${network}" --runType "${tests_to_run}" \
      --standaloneMode "${standalone_mode}" --testMarker "${pytest_marker}" \
      --publishStats "${publish_stats}"
  else
    echo "Not running any test, instead sleep for 5 mins"
    sleep 300
  fi
  cd "${CWD}"
}

stop_rippled() {
  sh "${rippled_automation_repo_path}"/install_rippled.sh --automationRepoPath "${rippled_automation_repo_path}" \
    --localRippledRepoPath "${local_rippled_repo_path}" --mode "build" --stopRippled
}

perform_test() {
  validate_repos
  check_repos_for_new_commits
  build_rippled
  if [ "$?" -eq 0 ] ; then
    run_tests "${run_tests_flag}"
  fi
  stop_rippled
}

script_teardown() {
  stop_rippled
  echo "Exiting in 5 seconds..."
  sleep 5
  exit 1
}


trap script_teardown INT

while [ "$1" != "" ]; do
  case $1 in
  --network)
    shift
    network="$1"
    ;;

  --localRippledRepoPath)
    shift
    local_rippled_repo_path="$1"
    ;;

  --automationRepoPath)
    shift
    rippled_automation_repo_path="$1"
    ;;

  --launchViaValgrind)
    shift
    launch_via_valgrind="${1:-$launch_via_valgrind}"
    standalone_mode="true"
    ;;

  --skipUnitTests)
    shift
    skip_unit_tests="${1:-$skip_unit_tests}"
    ;;

  --runTests)
    shift
    run_tests_flag="true"
    tests_to_run="$1"
    ;;

  --publishStats )
    shift
    publish_stats="$1"
    ;;

  --runCount )
    shift
    run_count="$1"
    ;;

  --runInterval )
    shift
    run_interval="$1"
    ;;

  --testMarker)
    shift
    run_tests_flag="true"
    pytest_marker="${1:-$pytest_marker}"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

work_dir="${rippled_automation_repo_path}/work_dir"
rippled_built_marker_file="${work_dir}/rippled_is_built"
rippled_prereq_installed_marker_file="${work_dir}/rippled_prereqs_installed"
test_run_log_path="${rippled_automation_repo_path}/../logs"


mkdir -p "${test_run_log_path}"
iteration=1
while :
do
  run_log_file="${test_run_log_path}/test_run_$(date +%Y_%m_%d_%H_%M_%S).log"
  echo "** Iteration $iteration [view log file: ${run_log_file}]"
  perform_test > "${run_log_file}"
  if [ $iteration -eq $run_count ] ; then
    break
  else
    iteration=$((iteration+1))
    echo "Sleep for $run_interval seconds..."
    sleep $run_interval
  fi
done
