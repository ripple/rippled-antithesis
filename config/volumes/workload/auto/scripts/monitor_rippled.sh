#!/bin/sh

################################################################################
# This script is to monitor local & public rippled, and report any crash. The
# script monitors rippled uptime, sequence number, system stats like
# CPU, memory, storage, and logs it every 30 seconds.
# In case of public rippled crash, local rippled is stopped by the script,
# so all tests get interrupted and the crash is noted.
#
# Usage: sh scripts/monitor_rippled.sh
#     [--rpcEndpoint <rpc endpoint>]
#     [--mode <build/install> (default mode: install)]
#     [--localRippledRepoPath <PATH_TO_RIPPLED_REPO>]
#     [--automationRepoPath <PATH_TO_AUTOMATION_REPO>]
#     [--logDirPath <if called from install_rippled.sh, pass this param to preserve logs in the same directory>]
#
# Example: To monitor rippled installed on a host,
# $ sh ~/workspace/automation/scripts/monitor_rippled.sh &
#
################################################################################

TMP_DIR="/tmp"
log_dir="$TMP_DIR"
install_mode="install" # default mode: install
build="build"          # build mode name
rippled_automation_repo_path="${PWD}"
local_rippled_repo_path="${HOME}/rippled"
job_id=""
job_name="<job_name undefined>"
slack_notify="false"

usage() {
  echo "Usage: $0 [Optional parameters]"
  echo "  --rpcEndpoint <rpc endpoint>"
  echo "  --mode build (build rippled; default mode: install)"
  echo "  --localRippledRepoPath <local rippled repo path for building rippled>"
  echo "  --logDirPath <if called from install_rippled.sh, pass this param to preserve logs in the same directory>"
  echo "  --automationRepoPath <automation repo path>"
  echo "  --jobID <CI job ID>"

  exit 1
}

stop_rippled() {
  stop_msg="${1:-Error}"

  echo "******************************************************" | tee -a "${rippled_sequence_log}"
  echo "**** ${stop_msg} ****" | tee -a "${rippled_sequence_log}"
  echo "Check ${rippled_sequence_log} for more info"
  echo "******************************************************" | tee -a "${rippled_sequence_log}"

  if [ "${slack_notify}" = "true" ]; then
    slack_message="**** ${stop_msg} ****"
    if [ -n "${job_id}" ]; then
      ci_job_url="https://gitlab.ops.ripple.com/xrpledger/automation/-/jobs/${job_id}"
      slack_message=":fire: \`${job_name}\` - ${ci_job_url} - ${slack_message}"
    fi
      echo "** Send slack notification: ${slack_message}"
      python3 -m scripts.slack_notification --message "${slack_message}"
  fi

  sh "${rippled_automation_repo_path}"/install_rippled.sh --automationRepoPath "${rippled_automation_repo_path}" \
    --localRippledRepoPath "${local_rippled_repo_path}" --mode "${install_mode}" --stopRippled

  exit 1
}

while [ "$1" != "" ]; do
  case $1 in
  --rpcEndpoint)
    shift
    rpc_endpoint="$1"
    ;;

  --localRippledRepoPath)
    shift
    local_rippled_repo_path="${1:-$local_rippled_repo_path}"
    ;;

  --automationRepoPath)
    shift
    rippled_automation_repo_path="$1"
    ;;

  --mode)
    shift
    install_mode="${1:-$install_mode}"
    ;;

  --logDirPath)
    shift
    log_dir="${1:-$log_dir}"
    ;;

  --jobID)
    shift
    job_id="${1:-$job_id}"
    ;;

  --jobName)
    shift
    job_name="${1:-$job_name}"
    ;;

  --slackNotify)
    shift
    slack_notify="${1:-$slack_notify}"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

rippled_exec="/opt/ripple/bin/rippled"
rippled_config_path="/opt/ripple/etc"

if [ -f "${rippled_exec}" -a -n "${rpc_endpoint}" ]; then
  rippled_seq_file="${TMP_DIR}/rippled_seq"
  local_rippled_seq_file="${TMP_DIR}/local_rippled_seq"
  public_rippled_seq_file="${TMP_DIR}/public_rippled_seq"
  rippled_sequence_log="${log_dir}/rippled_monitoring.log"
  "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg server_info >"${rippled_seq_file}" 2>&1
  seq_after_sync=$(grep '\"seq\" : ' "${rippled_seq_file}" | cut -d ':' -f2 | cut -d ' ' -f2)
  uptime_after_sync=$(grep '\"uptime\" : ' "${rippled_seq_file}" | cut -d ':' -f2 | cut -d ' ' -f2 | cut -d ',' -f1)
  sleep 2

  if [ -n "${seq_after_sync}" ]; then
    cpu_info_file="/proc/cpuinfo"
    if [ -f "${cpu_info_file}" ]; then
      cat "${cpu_info_file}" >"${log_dir}/sys_info.log"
    fi
    echo "Sequence after rippled is synced: $seq_after_sync"
    echo "Uptime after rippled is synced: $uptime_after_sync"

    while :; do
      "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg server_info >"${local_rippled_seq_file}" 2>&1
      local_rippled_seq=$(grep '\"seq\" : ' "${local_rippled_seq_file}" | cut -d ':' -f2 | cut -d ' ' -f2)
      uptime_now=$(grep '\"uptime\" : ' "${local_rippled_seq_file}" | cut -d ':' -f2 | cut -d ' ' -f2 | cut -d ',' -f1)

      rpc_server=$(echo "${rpc_endpoint}" | cut -d':' -f1)
      rpc_port=$(echo "${rpc_endpoint}" | cut -d':' -f2)

      rpc_ip=$(nslookup "${rpc_server}" | grep Address | tail -1 | cut -d ':' -f2)
      echo "RPC server ${rpc_server} translates to IP: ${rpc_ip}" >>"${rippled_sequence_log}"
      if [ -z "${rpc_ip}" ]; then
        stop_rippled "Unable to translate ${rpc_endpoint} to an IP"
      fi
      "${rippled_exec}" --rpc_ip "${rpc_ip}:${rpc_port}" server_info >"${public_rippled_seq_file}" 2>&1
      public_rippled_seq=$(grep '\"seq\" : ' "${public_rippled_seq_file}" | cut -d ':' -f2 | cut -d ' ' -f2)

      connection_error=$(grep "error" "${public_rippled_seq_file}")
      if [ -n "$connection_error" ]; then
        echo "**** Error connecting to ${rpc_endpoint}"
        public_rippled_seq="error"
      fi

      time_stamp="$(date +%Y_%m_%d_%H_%M_%S)"
      echo "--------------------------------------------------------------------------------" >>"${rippled_sequence_log}"
      echo "$time_stamp    Sequence: ${local_rippled_seq} (local) vs ${public_rippled_seq} (rpc_ip)" >>"${rippled_sequence_log}"
      echo "rippled uptime: ${uptime_now}" >>"${rippled_sequence_log}"
      df -h >>"${rippled_sequence_log}"
      mpstat >>"${rippled_sequence_log}"
      free -m >>"${rippled_sequence_log}"

      if [ -n "${uptime_now}" ]; then
        if [ "${uptime_now}" -lt "${uptime_after_sync}" ]; then
          stop_rippled "Uptime dipped to ${uptime_now} - Local rippled has probably restarted"
        fi
      else
        stop_rippled "No Uptime data - Local rippled has stopped/crashed"
      fi

      if [ -n "${local_rippled_seq}" ]; then
        if [ "${local_rippled_seq}" -lt "${seq_after_sync}" ]; then
          stop_rippled "Local rippled has probably crashed"
        fi
      else
        stop_rippled "Error fetching local rippled sequence number"
      fi

      if [ -n "${public_rippled_seq}" ]; then
        if [ "${public_rippled_seq}" = "error" ]; then
          echo "**** Error connecting to ${rpc_endpoint}"
        else
          if [ "${public_rippled_seq}" -lt "${seq_after_sync}" ]; then
            stop_rippled "Public rippled has probably crashed"
          fi
        fi
      else
        stop_rippled "Error fetching public rippled sequence number"
      fi

      sleep 30
    done
  else
    stop_rippled "Error fetching sequence number"
  fi
else
  usage
  exit 1
fi
