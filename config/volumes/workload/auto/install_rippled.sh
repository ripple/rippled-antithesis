#!/usr/bin/env sh
set +e

################################################################################
# Script to install/build rippled
# To install rippled:
# Usage: sh install_rippled.sh
#     [--network <devnet/testnet (default: devnet)]
#     [--feature <rippled/amm/clio/sidechain> (default: rippled)>]
#
# To build rippled:
# Usage: sh install_rippled.sh
#     --mode build
#     [--network <devnet/testnet (default: devnet)]
#     [--feature <rippled/amm/clio/sidechain> (default: rippled)>]
#     [--rippledRemoteBranch <rippled remote git branch for building rippled (default: ripple:develop>]
#     [--ignoreRippledRepoClone] (ignore rippled repo clone for building rippled)
#     [--ignoreRippledBuildPrereq] (ignore rippled build prereq for building rippled)
#     [--skipUnitTests true] (skip unit tests after build)
#     [--launchViaValgrind true] (launch rippled via valgrind, to use for tests like memleak)
#
# Generic options on installed/built rippled
#     [--startRippled] (start rippled on an installed/build rippled)
#     [--stopRippled] (stop rippled on an installed/build rippled)
#     [--publishStats true] (push stats to prometheus)
#
# Example command to launch rippled via valgrind (in standalone mode)
# sh install_rippled.sh --mode build [--localRippledRepoPath <local rippled repo path>] --launchViaValgrind true
################################################################################

network="devnet"
default_rippled_sync_timeout=1200 # 20 mins
default_clio_sync_timeout=600 # 10 mins
mainnet_rippled_sync_timeout=7200 # 120 mins
feature_amm="amm"
rippled_amm_devnet_rpc_endpoint="amm.devnet.rippletest.net:51234"
rippled_default_altnet_rpc_endpoint="s.altnet.rippletest.net:51234"
rippled_default_devnet_rpc_endpoint="s.devnet.rippletest.net:51234"
clio_default_devnet_rpc_endpoint="clio.devnet.rippletest.net:51233"
rippled_default_mainnet_rpc_endpoint="s1.ripple.com:51234"
feature_sidechain="sidechain"
rippled_locking_chain_devnet_rpc_endpoint="${rippled_default_devnet_rpc_endpoint}"
rippled_issuing_chain_devnet_rpc_endpoint="sidechain-net2.devnet.rippletest.net:51234"
product_clio="clio"
product="rippled"
rippled_log_filepath="/var/log/rippled/debug.log"
clio_log_filepath="/var/log/clio/clio.log"
rippled_db_path="/var/lib/rippled/db"

time_stamp="$(date +%Y_%m_%d_%H_%M_%S)"
publish_stats="None"
job_id="LocalRun"
job_name="<job_name undefined>"
stop_rippled_flag=""
start_rippled_flag=""
install_mode="install" # default mode: install
build="build"          # build mode name
ignore_repo_clone=""
ignore_build_prereq=""
skip_unit_tests=""
feature="default"
launch_via_valgrind=""
standalone_mode=""
sidechain_auto_submit="true"
rippled_automation_repo_path="${PWD}"
rippled_remote_branch="XRPLF:develop"
clio_remote_branch="XRPLF:develop"
witness_remote_branch="ripple:develop"
local_rippled_repo_path="${HOME}/rippled"
local_clio_repo_path="${HOME}/clio"
local_witness_repo_path="${HOME}/witness"
monitor_rippled_pid="/tmp/monitor_rippled.pid"
db_type="unknown"
slack_notify="false"
latest_version="latest"
rippled_version="${latest_version}"
clio_pid=""
local_host="localhost"
rippled_port=51234
clio_port=51233

usage() {
  echo "Usage: $0 [Optional parameters]"
  echo "  --network <devnet/testnet (default: $network)>"
  echo "  --product <rippled/clio (default: $product)>"
  echo "  --feature <rippled/amm/clio/sidechain> (default: $feature)>"
  echo "  --mode build (build rippled; default mode: install)"
  echo "  --rippledVersion <rippled version (e.g. 2.0.0~rc5-1)> (default: ${latest_version})"
  echo "  --rippledRemoteBranch <rippled remote git branch for building rippled (default: ${rippled_remote_branch}>"
  echo "  --clioRemoteBranch <clio remote git branch for building clio (default: ${clio_remote_branch}>"
  echo "  --localRippledRepoPath <local rippled repo path for building rippled >"
  echo "  --localClioRepoPath <local clio repo path for building clio >"
  echo "  --automationRepoPath <automation repo path>"
  echo "  --ignoreRepoClone (ignore repo clone for building rippled/clio)"
  echo "  --ignoreBuildPrereq (ignore build prereq for building rippled/clio)"
  echo "  --startRippled (start rippled on an installed/build rippled)"
  echo "  --stopRippled (stop rippled on an installed/build rippled)"
  echo "  --skipUnitTests true (skip unit tests after build)"
  echo "  --launchViaValgrind true (launch rippled via valgrind, to use for tests like memleak)"
  echo "  --publishStats true (publish stats to prometheus)"
  echo "  --sidechainAutoSubmit true (auto-submit sidechain AddAttestation txns, default: $sidechain_auto_submit)"
  echo "  --witnessRemoteBranch <witness remote git branch for witness server (default: ${witness_remote_branch}>"

  exit 1
}

exit_on_error() {
  exit_code=$1
  exit_message="$2"
  if [ $exit_code -ne 0 ]; then
    echo "${exit_message} (${exit_code})"

    if [ "${slack_notify}" = "true" ]; then
      slack_message="${exit_message}"
      if [ "${job_id}" != "LocalRun" ]; then
        ci_job_url="https://gitlab.ops.ripple.com/xrpledger/automation/-/jobs/${job_id}"
        slack_message=":fire: \`${job_name}\` - ${ci_job_url} - ${slack_message}"
      fi
      echo "** Send slack notification: ${slack_message}"
      python3 -m scripts.slack_notification --message "${slack_message}"
    fi

    exit $exit_code
  fi
}

prepare_workspace() {
  if [ ! -d "${rippled_automation_repo_path}/.git" ]; then
    echo "Unable to locate automation repo. Update --automationRepoPath"
    exit_on_error 1 "Unable to locate automation repo"
  fi

  echo "Log directory: ${log_dir}"
  mkdir -p "${log_dir}"

  echo "set core pattern and ulimit"
  bash -c 'echo core.%e > /proc/sys/kernel/core_pattern'
  ulimit -c unlimited

  if [ "${standalone_mode}" = "true" ]; then
    feature_config_dir="configs/${product}/${feature}/standalone"
  else
    feature_config_dir="configs/${product}/${feature}/${network}"
  fi
  echo "${feature} config files directory: ${feature_config_dir}"

  rippled_sync_timeout="${default_rippled_sync_timeout}"
  if [ "${network}" = "mainnet" ] ; then
    echo "Setting rippled sync timeout to $((mainnet_rippled_sync_timeout / 60)) mins"
    rippled_sync_timeout="${mainnet_rippled_sync_timeout}"
  fi

  if [ -f "${rippled_db_path}/ledger.db" ] ; then
    echo "rippled install/build will use the existing db [${rippled_db_path}]"
    db_type="existing"
  else
    echo "rippled install/build will use new db, as path ${rippled_db_path} doesn't exist"
    db_type="new"
  fi

  if [ "${install_mode}" = "${build}" ]; then
    echo "Initializing parameters for mode: building/using pre-built rippled/clio"
    rippled_exec="/opt/ripple/bin/rippled"
    rippled_config_path="/opt/ripple/etc"
    clio_exec="/opt/ripple/bin/clio_server"
    clio_config_path="/opt/clio/etc"
    mkdir -p "${rippled_config_path}" "${clio_config_path}" "${work_dir}"

    rippled_repo_name=$(echo "${rippled_remote_branch}" | cut -d ':' -f1)
    clio_repo_name=$(echo "${clio_remote_branch}" | cut -d ':' -f1)
    rippled_checkout_branch=$(echo "${rippled_remote_branch}" | cut -d ':' -f2)
    rippled_repo_url="https://github.com/${rippled_repo_name}/rippled.git"
    clio_repo_url="https://github.com/${clio_repo_name}/clio.git"
    clio_checkout_branch=$(echo "${clio_remote_branch}" | cut -d ':' -f2)

    witness_repo_name=$(echo "${witness_remote_branch}" | cut -d ':' -f1)
    witness_checkout_branch=$(echo "${witness_remote_branch}" | cut -d ':' -f2)
    witness_repo_url="https://github.com/${witness_repo_name}/xbridge_witness.git"
    witness_exec="/opt/xbridge-witness/xbridge_witnessd"
  else
    echo "Initializing parameters for mode: installing/using pre-installed rippled/clio"
    rippled_exec="/opt/ripple/bin/rippled"
    rippled_config_path="/opt/ripple/etc"
    clio_exec="/opt/ripple/bin/clio_server"
    clio_config_path="/opt/clio/etc"
  fi

  ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime && apt-get update && apt-get install --yes tzdata
  . "${build_lib}"
}

install_misc_packages() {
  if [ ! "${ignore_build_prereq}" = "true" ]; then
    echo "Installing misc packages..."
    log_file="${log_dir}/misc_packages.log"
    case ${ID} in
    ubuntu | debian)
      echo "Acquire::Retries 3;" > /etc/apt/apt.conf.d/80-retries
      apt -y update >>"${log_file}" 2>&1 &&
      apt -y install sysstat dnsutils jq >>"${log_file}" 2>&1
      exit_on_error $? "misc packages installation failed"
      if [ "${UBUNTU_CODENAME}" = "bionic" ]; then
        apt-get -y install python3.8 python3-pip >>"${log_file}" 2>&1
        update-alternatives --install /usr/local/bin/python3 python3 /usr/bin/python3.8 3
      else # focal or jammy
        apt-get install -y python-is-python3 pip >>"${log_file}" 2>&1
      fi
      ;;

    centos | fedora | rhel | scientific)
      yum -y update >>"${log_file}" 2>&1 &&
      yum -y install git procps sysstat findutils bind-utils >>"${log_file}" 2>&1
      ;;
    *)
      echo "unrecognized distro!"
      exit_on_error 1 "unrecognized distro!"
      ;;
    esac

    case ${ID} in
    centos)
      yum install -y centos-release-scl  >>"${log_file}" 2>&1 &&
      yum -y update  >>"${log_file}" 2>&1 &&
      yum install -y rh-python38  >>"${log_file}" 2>&1 &&
      echo "source scl_source enable rh-python38" >> /etc/bashrc
      source scl_source enable rh-python38  >>"${log_file}" 2>&1
    ;;
    fedora)
      yum install -y python pip >>"${log_file}" 2>&1
    ;;
    esac

    # Install prometheus-client
    echo "Install prometheus-client..."
    python3 -m pip install prometheus-client requests distro >>"${log_file}" 2>&1
    exit_on_error $? "prometheus-client install failed"
  fi
}

install_rippled() {
  echo "Installing rippled (${rippled_version})..."
  log_file="${log_dir}/rippled_install.log"
  case ${ID} in
  ubuntu | debian)
    pkgtype="dpkg"
    ;;
  fedora | centos | rhel | scientific)
    pkgtype="rpm"
    ;;
  *)
    echo "unrecognized distro!"
    exit_on_error 1 "unrecognized distro!"
    ;;
  esac

  if [ "${pkgtype}" = "dpkg" ]; then
    apt -y update >>"${log_file}" 2>&1 &&
      apt -y install apt-transport-https ca-certificates wget gnupg apt-utils >>"${log_file}" 2>&1
    exit_on_error $? "Error installing packages"
    wget -q -O - "https://repos.ripple.com/repos/api/gpg/key/public" | apt-key add -
    echo "deb https://repos.ripple.com/repos/rippled-deb focal nightly" | tee -a /etc/apt/sources.list.d/ripple.list
    apt -y update >>"${log_file}" 2>&1
    if [ "${rippled_version}" = "${latest_version}" ]; then
      apt -y install rippled >>"${log_file}" 2>&1
    else
      apt -y install rippled="${rippled_version}" --allow-downgrades >>"${log_file}" 2>&1
    fi
    exit_on_error $? "Error installing rippled packages"
  elif [ "${pkgtype}" = "rpm" ]; then
    cat <<REPOFILE | tee /etc/yum.repos.d/ripple.repo
[ripple-nightly]
name=XRP Ledger Packages
baseurl=https://repos.ripple.com/repos/rippled-rpm/nightly/
enabled=1
gpgcheck=0
gpgkey=https://repos.ripple.com/repos/rippled-rpm/nightly/repodata/repomd.xml.key
repo_gpgcheck=1
REPOFILE
    yum -y update >>"${log_file}" 2>&1 &&
      yum -y install rippled >>"${log_file}" 2>&1
    exit_on_error $? "Error installing packages"
  fi
  sleep 5
}

clone_repo() {
  CWD=$(pwd)

  l_product="$1"
  if [ ! "${ignore_build_prereq}" = "true" ]; then
    echo "Installing required packages before building ${l_product}..."

    log_file="${log_dir}/prereq_packages.log"
    apt -y update >>"${log_file}" 2>&1 &&
      DEBIAN_FRONTEND=noninteractive apt -y install git pkg-config protobuf-compiler libprotobuf-dev libssl-dev wget build-essential >>"${log_file}" 2>&1
  fi

  if [ ! "${ignore_repo_clone}" = "true" ]; then

    product_repo_url="$(eval "echo \$${l_product}_repo_url")"
    product_checkout_branch="$(eval "echo \$${l_product}_checkout_branch")"
    product_repo_path="$(eval "echo \$local_${l_product}_repo_path")"

    echo "Cloning ${l_product} repo ${product_repo_url} (branch: ${product_checkout_branch}) ..."
    log_file="${log_dir}/clone_${l_product}.log"

    git clone "${product_repo_url}" "${product_repo_path}"
    cd "${product_repo_path}"
    git checkout "${product_checkout_branch}"
    exit_on_error $? "Unable to checkout: ${product_checkout_branch}"
    git log -1
  fi
  cd "${CWD}"
}

config_and_start_rippled() {
  echo "Configure and start rippled..."
  cd "${rippled_automation_repo_path}"

  chain="$2"
  if [ -n "${chain}" ] ; then
    echo "Chain: ${chain}"
    rippled_config_path="${feature_config_dir}/${chain}"
    rippled_log_filepath="/var/log/rippled/${chain}/debug.log"  # /var/log/rippled/locking_chain/debug.log
    rippled_log_archive="${log_dir}/${chain}_rippled.log"
  else
    echo "Deleting old config files and validator.txt files..."
    rm -rf "${rippled_config_path}"/validators.txt
    rm -rf "${rippled_config_path}"/rippled.cfg

    rippled_log_archive="${log_dir}/rippled.log"

    echo "Copying new config files and validator.txt files for ${product}/${feature}/${network} ..."
    cp ${feature_config_dir}/validators.txt "${rippled_config_path}"/validators.txt
    cp ${feature_config_dir}/rippled.cfg "${rippled_config_path}"/rippled.cfg
    exit_on_error $? "Gitlab failure: error copying config files"
  fi

  # archive config files
  echo "Archive config files..."
  cp -r "${rippled_config_path}" "${log_dir}"

  echo "Files present when rippled is installed"
  ls -lrt "${rippled_config_path}"

  mkdir -p $(dirname "${rippled_log_filepath}")
  touch "${rippled_log_filepath}"
  tail_pid=$(pgrep -fl tail | grep "${rippled_log_filepath}" | awk '{print $1}')
  kill -9 "$tail_pid" >/dev/null 2>&1 # not to conflict repetitive runs of rippled

  echo "Starting rippled as a service in the background"
  if [ "${launch_via_valgrind}" = "true" ]; then
    echo "Launching rippled via valgrind in standalone mode..."
    apt-get install valgrind -y >"${log_dir}/install_valgrind.log" 2>&1
    valgrind_log_file="${log_dir}/valgrind-out.txt"
    echo "Valgrind log file: ${valgrind_log_file}"
    echo "${valgrind_log_file}" >"/tmp/valgrind_log_filepath.txt" # Save valgrind logfile path for run_tests.sh to parse
    valgrind --tool=memcheck --leak-check=yes --leak-check=summary --show-leak-kinds=all --show-reachable=yes \
      --log-file="${valgrind_log_file}" \
      "${rippled_exec}" -a --start --conf="${rippled_config_path}/rippled.cfg" --silent 2>&1 &
  else
    if [ "${standalone_mode}" = "true" ]; then
      "${rippled_exec}" -a --start --conf="${rippled_config_path}/rippled.cfg" --silent 2>&1 &
    else
      "${rippled_exec}" --conf "${rippled_config_path}/rippled.cfg" --silent 2>&1 &
    fi
  fi
  tail -f "${rippled_log_filepath}" > "${rippled_log_archive}" &

  sleep 5
  ls -latr core* 2> /dev/null
}

config_and_start_clio() {
  echo "Configure and start clio..."

  echo "Deleting old clio config files..."
  rm -rf "${clio_config_path}"/config.json

  clio_log_archive="${log_dir}/clio.log"

  echo "Copying new config files for ${product}/${network} ..."
  cp ${feature_config_dir}/config.json "${clio_config_path}"/config.json
  exit_on_error $? "Gitlab failure: error copying config files"

  # archive config files
  echo "Archive config files..."
  cp -r "${clio_config_path}" "${log_dir}"

  echo "Files present when clio is installed"
  ls -lrt "${clio_config_path}"

  echo "Starting clio as a service in the background"

  "${clio_exec}" "${clio_config_path}/config.json" 2>&1 &
  clio_pid=$!
  sleep 5

  tail -f "${clio_log_filepath}" > "${clio_log_archive}" &

  ls -latr core* 2> /dev/null
}


wait_for_rippled_sync() {
  echo "Validating db sync for rippled [${rippled_config_path}]..."
  rippled_version=$("${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg --version | cut -d' ' -f3 | cut -c-15)

  l_product="$1"
  chain="$2"
  if [ -n "${chain}" ] ; then
    echo "Chain: ${chain}"
    rpc_endpoint="$(eval "echo \$${l_product}_${chain}_${network}_rpc_endpoint")"
    server_name="${chain}"
  else
    rpc_endpoint="$(eval "echo \$${l_product}_${feature}_${network}_rpc_endpoint")"
    server_name="${feature}"
  fi

  local_rippled_server_info="${log_dir}/${server_name}_server_info.log"
  public_rippled_server_info="${log_dir}/${server_name}_${network}_server_info.log"

  count=1
  max_tries=2
  rippled_synced="false"
  while [ $count -le $max_tries -a "${rippled_synced}" = "false" ] ; do
    echo "Wait for rippled db to sync up (attempt: ${count}/${max_tries})..."

    seconds_elapsed=0
    wait_time=20
    local_rippled_seq="local seq"
    public_rippled_seq="public seq"
    install_complete="true"
    while [ $seconds_elapsed -lt $rippled_sync_timeout ]; do
      "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg server_info >"${local_rippled_server_info}" 2>&1
      local_rippled_seq=$(grep '\"seq\" : ' "${local_rippled_server_info}" | cut -d ':' -f2)

      rpc_server=$(echo "${rpc_endpoint}" | cut -d':' -f1)
      rpc_port=$(echo "${rpc_endpoint}" | cut -d':' -f2)

      rpc_ip=$(nslookup "${rpc_server}" | grep Address | tail -1 | cut -d ':' -f2)
      if [ -z "${rpc_ip}" ]; then
        echo "Unable to translate ${rpc_endpoint} to an IP: ${rpc_ip}"
        install_complete="false"
        break
      else
        "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg --rpc_ip "${rpc_ip}:${rpc_port}" server_info > "${public_rippled_server_info}" 2>&1
        connection_error=$(grep "error" "${public_rippled_server_info}")
        if [ -n "$connection_error" ]; then
          echo "**** Error connecting to ${rpc_endpoint}"
          public_rippled_seq="error"
        else
          public_rippled_seq=$(grep '\"seq\" : ' "${public_rippled_server_info}" | cut -d ':' -f2)
        fi

        if [ -z "${public_rippled_seq}" ]; then
          echo "Unable to query 'server_info' on public server ${rpc_ip}. Probably, rippled install was not successful"
          install_complete="false"
          break
        fi
      fi

      echo "  [Time elapsed: $seconds_elapsed seconds] Sequence: ${local_rippled_seq} (local) vs ${public_rippled_seq} (${network} -${rpc_ip})"
      if [ "${standalone_mode}" = "true" ]; then
        if [ -n "${local_rippled_seq}" ]; then
          echo "rippled db is initialized and running in standalone mode..."
          rippled_synced="true"
          break
        fi
      fi

      server_state=$(grep '\"server_state\" : ' "${local_rippled_server_info}" | cut -d ':' -f2)
      server_state_full=$(echo "${server_state}" | grep full)
      server_state_proposing=$(echo "${server_state}" | grep proposing)

      if [ "${local_rippled_seq}" = "${public_rippled_seq}" ] && { [ -n "${server_state_full}" ] || [ -n "${server_state_proposing}" ]; }; then
        max_timeout=$((seconds_elapsed + 300))  # 300 more seconds to transition to non-empty
        while [ $seconds_elapsed -lt $max_timeout ] && [ "${rippled_synced}" = "false" ]; do
          "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg server_info >"${local_rippled_server_info}" 2>&1
          server_state=$(grep '\"server_state\" : ' "${local_rippled_server_info}" | cut -d ':' -f2)
          complete_ledgers=$(grep '\"complete_ledgers\" : ' "${local_rippled_server_info}" | cut -d ':' -f2)
          echo "**** $(date) server_state:${server_state} complete_ledgers:${complete_ledgers}"

          empty_ledgers=$(echo "${complete_ledgers}" | grep empty)
          if [ -n "${empty_ledgers}" ]; then
            seconds_elapsed=$((seconds_elapsed + wait_time))
            sleep ${wait_time}
          else
            rippled_synced="true"
          fi
        done

        if [ "${rippled_synced}" = "true" ]; then
          break
        else
          exit_on_error 1 "**** server_state is ${server_state} but complete_ledgers is ${empty_ledgers}"
        fi
      fi


      sleep $wait_time
      seconds_elapsed=$((seconds_elapsed + wait_time))
    done

    if [ "$publish_stats" = "true" ] && [ "${install_complete}" = "true" ]; then
      if [ "${standalone_mode}" = "true" ]; then
        echo "  Skipping pushing stats for standalone mode"
      else
        # Push to prometheus only if it's the 1st attempt
        if [ $count -eq "1" ] ; then
          echo "  Publishing stats to prometheus..."
          sh "${rippled_automation_repo_path}"/scripts/publish_metric.sh --metric rippled_sync_time:${seconds_elapsed} \
            --jobID "$job_id" --labels "version:${rippled_version},db_type:${db_type},synced:${rippled_synced}"
        fi
      fi
    fi

    echo "${log_dir}, IS_DB_SYNCED: ${rippled_synced}, ELAPSED_TIME: $seconds_elapsed, RIPPLED_VERSION: ${rippled_version}, DB_TYPE: ${db_type}" | tee -a "${rippled_automation_repo_path}/metrics.log"
    if [ "${rippled_synced}" = "true" ]; then
      echo "**** rippled synced in $seconds_elapsed seconds"
    else
      echo "**** rippled not synced within $rippled_sync_timeout seconds"
      if [ $count -eq $max_tries ] ;  then
        echo "Max attempts [$max_tries] reached. Exiting."
        exit_on_error 1 "**** rippled not synced within $rippled_sync_timeout seconds"
      else
        echo ""
        echo "Restarting rippled (stop & start) and retrying..."
        stop_rippled true false  # do not exit script after stopping rippled
        sleep 5  # wait for 5 seconds before restarting rippled
        config_and_start_rippled "${chain}"
      fi
    fi

    count=$((count + 1))
  done

  "${rippled_exec}" --conf "${rippled_config_path}/rippled.cfg" server_info > "${log_dir}/${server_name}_server_info.log" 2>&1
  "${rippled_exec}" --conf "${rippled_config_path}/rippled.cfg" peers > "${log_dir}/${server_name}_peers.log" 2>&1

  if [ ! "${standalone_mode}" = "true" -a -z "${chain}" ]; then
    echo "Launching monitor rippled in background..."
    # Monitor local & public rippled, and stop local rippled incase of a crash
    sh "${rippled_automation_repo_path}"/scripts/monitor_rippled.sh --localRippledRepoPath "${local_rippled_repo_path}" \
      --automationRepoPath "${rippled_automation_repo_path}" \
      --rpcEndpoint "${rpc_endpoint}" --logDirPath "${log_dir}" \
      --mode "${install_mode}" --jobID "$job_id" --jobName "$job_name" --slackNotify "${slack_notify}" &
    echo $! > "${monitor_rippled_pid}"
  else
    echo "Skipping monitor rippled for standalone mode/sidechain"
  fi
}

wait_for_clio_sync() {
  echo "Validating db sync for clio [${clio_config_path}]..."

  rippled_version=$("${rippled_exec}" --conf "${rippled_config_path}/rippled.cfg" --version | cut -d' ' -f3 | cut -c-15)
  clio_version=$("${clio_exec}" "${clio_config_path}/config.json" --version)

  local_rippled_server_info="${log_dir}/rippled_server_info.log"
  local_clio_server_info="${log_dir}/clio_server_info.log"

  count=1
  max_tries=2
  clio_synced="false"
  while [ $count -le $max_tries -a "${clio_synced}" = "false" ] ; do
    echo "Wait for clio db to sync up (attempt: ${count}/${max_tries})..."

    seconds_elapsed=0
    wait_time=20
    rippled_seq="rippled seq"
    clio_seq="clio seq"
    install_complete="true"
    while [ $seconds_elapsed -lt $default_clio_sync_timeout ]; do
      curl -d '{"method": "server_info"}' ${local_host}:${rippled_port} >"${local_rippled_server_info}" 2>/dev/null
      curl -d '{"method": "server_info"}' ${local_host}:${clio_port} >"${local_clio_server_info}" 2>/dev/null

      rippled_seq=$(cat "${local_rippled_server_info}" | jq .result.info.validated_ledger.seq)

      clio_error=$(grep "error" "${local_clio_server_info}" | cut -d ':' -f2)
      clio_info=$(grep "info" "${local_clio_server_info}" | cut -d ':' -f2)

      if [ -z "${clio_error}" ] && [ -n "${clio_info}" ]; then
        clio_seq=$(cat "${local_clio_server_info}" | jq .result.info.validated_ledger.seq)
        clio_cache=$(cat "${local_clio_server_info}" | jq .result.info.cache.is_full)

        #TODO: Update clio sync logic once Clio returns server_info while syncing with rippled
        if [ "${rippled_seq}" = "${clio_seq}" ] && [ "${clio_cache}" = "true" ] ; then
          clio_synced="true"
          break
        else
          echo "  [Time elapsed: $seconds_elapsed seconds] Sequence: ${rippled_seq} (rippled) vs ${clio_seq} (clio) (${network})"
          sleep $wait_time
        fi
      elif [ -n "${clio_error}" ]; then
        echo "  [Time elapsed: $seconds_elapsed seconds]: Waiting for clio to sync"
        sleep $wait_time
      else
        exit_on_error 1 "**** clio is not running"
      fi
      seconds_elapsed=$((seconds_elapsed + wait_time))
    done

    if [ "${clio_synced}" = "true" ]; then
      echo "${log_dir}, IS_DB_SYNCED: ${clio_synced}, ELAPSED_TIME: $seconds_elapsed, RIPPLED_VERSION: ${rippled_version}, CLIO_VERSION: ${clio_version}, DB_TYPE: ${db_type}" | tee -a "${rippled_automation_repo_path}/metrics.log"
      echo "**** clio synced in $seconds_elapsed seconds"
    else
      echo "**** clio not synced within $default_clio_sync_timeout seconds"
      if [ $count -eq $max_tries ] ;  then
        echo "Max attempts [$max_tries] reached. Exiting."
        exit_on_error 1 "**** clio not synced within $default_clio_sync_timeout seconds"
      else
        echo ""
        echo "Restarting clio (stop & start) and retrying..."
        stop_clio
        sleep 5  # wait for 5 seconds before restarting clio
        config_and_start_clio
      fi
    fi

    count=$((count + 1))
  done
}


build_rippled() {
  echo "Build rippled..."
  case ${ID} in
  ubuntu)
    prereq_for_building_on_ubuntu "${ignore_build_prereq}"
    build_rippled_on_ubuntu
    ;;

  *)
    echo "unrecognized distro!"
    exit_on_error 1 "unrecognized distro!"
    ;;
  esac
}

build_clio() {
  echo "Build Clio..."
  case ${ID} in
  ubuntu)
    build_clio_on_ubuntu
    ;;

  *)
    echo "unrecognized distro!"
    exit_on_error 1 "unrecognized distro!"
    ;;
  esac
}

run_unit_tests() {
  if [ "${skip_unit_tests}" = "true" ]; then
    echo "Skipping unit tests"
  else
    echo "Preparing for running unit tests..."

    # workaround for unit test error on Ubuntu 20
    # Error: [('SSL routines', 'SSL_CTX_use_certificate', 'ca md too weak')]
    # https://askubuntu.com/questions/1231799/certificate-error-after-upgrade-to-20-04
    set_lower_ssl_security_level=""
    ssl_conf="/etc/ssl/openssl.cnf"
    ssl_conf_bkp="${ssl_conf}.bkp"
    if [ -f "/etc/issue" ]; then
      os_version=$(grep "Ubuntu 20" /etc/issue)
      if [ -n "$os_version" ]; then
        echo "  Updating ssl conf..."
        set_lower_ssl_security_level=true
        cp "${ssl_conf}" "${ssl_conf_bkp}"

        echo "openssl_conf = default_conf" >"${ssl_conf}"
        cat "${ssl_conf_bkp}" >>"${ssl_conf}"
        cat <<EOF >>"${ssl_conf}"
[ default_conf ]
ssl_conf = ssl_sect

[ssl_sect]
system_default = ssl_default_sect

[ssl_default_sect]
MinProtocol = TLSv1.2
CipherString = DEFAULT:@SECLEVEL=0
EOF
      fi
    fi
    echo "  Saving a copy of ${ssl_conf} into logs dir"
    cp "${ssl_conf}" "${log_dir}"
    # End of workaround

    echo "  Running unittests..."
    log_file="${log_dir}/unit_tests.log"
    "${rippled_exec}" --unittest >"${log_file}" 2>&1

    if [ "${set_lower_ssl_security_level}" = "true" ]; then
      echo "  Restoring ssl conf file"
      cp "${ssl_conf_bkp}" "${ssl_conf}"
    fi

    failed_test_count=$(grep "tests total, 0 failures" "${log_file}")
    if [ -n "${failed_test_count}" ] ; then
      echo "Unittest: Passed"
    else
      echo "Unittest: Failed"
      exit_on_error 1 "Unittest: Failed"
    fi
  fi
}

run_clio_unit_tests() {
  if [ "${skip_unit_tests}" = "true" ]; then
    echo "Skipping clio unit tests"
  else
    echo "Running clio unittests..."
    log_file="${log_dir}/clio_unit_tests.log"
    "${clio_build_path}/clio_tests" >"${log_file}" 2>&1

    failed_test_count=$(grep "FAILED" "${log_file}")
    if [ -n "${failed_test_count}" ] ; then
      exit_on_error 1 "Clio Unittests: Failed"
    else
      echo "Clio Unittests: Passed"
    fi
  fi
}

stop_rippled() {
  stop_rippled_flag="$1"
  exit_after_stopping="${2:-true}"  # default: stop rippled and exit

  if [ "${stop_rippled_flag}" = "true" ]; then
    stop_exit_status=1

    echo "Stopping rippled..."
    "${rippled_exec}" --conf "${rippled_config_path}"/rippled.cfg stop > "${log_dir}/rippled_stop.log" 2>&1
    rippled_stop_status=$(grep "success" "${log_dir}/rippled_stop.log")
    if [ -n "${rippled_stop_status}" ]; then
      wait_time=5
      seconds_elapsed=0
      max_timeout=300 # 5 mins
      while [ $seconds_elapsed -lt $max_timeout ]; do
        pgrep rippled >/dev/null 2>&1
        if [ $? -eq 0 ]; then
          echo "  Waiting for rippled to stop completely [${seconds_elapsed}/${max_timeout} seconds elapsed]..."
          sleep $wait_time
          seconds_elapsed=$((seconds_elapsed + wait_time))
        else
          echo "rippled stopped!"
          stop_exit_status=0
          break
        fi
      done

      if [ "${stop_exit_status}" -ne 0 ] ; then
        echo "  ** Failed to stop rippled"
      fi
    fi

    # kill advance ledger script running in background
    advance_ledger_pid=$(ps -ef | grep $(basename "${advance_ledger_script}") | grep -v grep | awk '{print $2}')
    kill -9 "$advance_ledger_pid" >/dev/null 2>&1 # not to conflict repetitive runs of rippled

    # kill tail command redirecting rippled log for archiving
    tail_pid=$(ps -ef | grep tail | grep -v grep | grep "${rippled_log_filepath}" | awk '{print $2}')
    kill -9 "$tail_pid" >/dev/null 2>&1 # not to conflict repetitive runs of rippled

    # kill previously running monitor_rippled, if any
    if [ -f "${monitor_rippled_pid}" ] ; then
      kill -9 $(cat "${monitor_rippled_pid}") > /dev/null 2>&1  # not to conflict repetitive runs of rippled
    fi

    if [ "${exit_after_stopping}" = "true" ] ; then
      exit $stop_exit_status
    fi
  fi
}

stop_clio() {
  echo "Stopping clio..."

  kill -9 $clio_pid  > "${log_dir}/stop_clio.log" 2>&1
  exit_on_error $? "Failed to kill clio pid"

  # kill tail command redirecting clio log for archiving
  clio_tail_pid=$(ps -ef | grep tail | grep -v grep | grep "${clio_log_filepath}" | awk '{print $2}')
  kill -9 "$clio_tail_pid" >/dev/null 2>&1 # not to conflict repetitive runs of clio

  #TODO: update stop_clio logic after stop feature is enabled by dev
}

get_rippled() {
  if [ "${start_rippled_flag}" = "true" ]; then
    echo "Skipping installing/building rippled, and directly starting rippled..."
  else
    install_misc_packages "${ignore_build_prereq}"
    if [ "${install_mode}" = "${build}" ]; then
      case ${ID} in
      ubuntu) # supported list of OSes for building rippled
        clone_repo "rippled"
        build_rippled
        run_unit_tests
        ;;

      *)
        echo "unrecognized distro!"
        exit_on_error 1 "unrecognized distro!"
        ;;
      esac
    else
      install_rippled
    fi
  fi
}

get_clio() {
  install_misc_packages "${ignore_build_prereq}"
  if [ "${install_mode}" = "${build}" ]; then
    case ${ID} in
    ubuntu) # supported list of OSes for building clio
      clone_repo "clio"
      build_clio
      run_clio_unit_tests
      ;;

    *)
      echo "unrecognized distro!"
      exit_on_error 1 "unrecognized distro!"
      ;;
    esac
  else
    exit_on_error 1 "Clio not supported in ${install_mode} mode"
  fi
}

get_witness_server() {
  echo "Get witness servers..."

  if [ "${install_mode}" = "${build}" ]; then
    case ${ID} in
    ubuntu) # supported list of OSes for building rippled
      clone_witness_repo
      install_conan
      build_witness_on_ubuntu
      ;;

    *)
      echo "unrecognized distro!"
      exit_on_error 1 "unrecognized distro!"
      ;;
    esac
  else
    echo "Currently, install mode is not supported for witness server"
    exit_on_error 1 "install mode is not supported for witness server"
  fi
}

start_witness_servers() {
  witness_configs_dir="${feature_config_dir}/witness"
  echo "Auto-submit mode: ${sidechain_auto_submit}"
  if [ "${sidechain_auto_submit}" = "true" ] ; then
    sed -i.tmp 's/\"ShouldSubmit\"\:\ false/\"ShouldSubmit\"\:\ true/g' "${witness_configs_dir}"/witness*.json
  else
    sed -i.tmp 's/\"ShouldSubmit\"\:\ true/\"ShouldSubmit\"\:\ false/g' "${witness_configs_dir}"/witness*.json
  fi


  echo "Archive config files..."
  cp -r "${witness_configs_dir}" "${log_dir}"

  for witness_config_file in "${witness_configs_dir}"/witness*.json
  do
    echo "Starting witness ${witness_config_file}..."
    witness_db_dir=$(grep DBDir "${witness_config_file}" | cut -d: -f2 | cut -d, -f1 | cut -d\" -f2 )
    witness_log_file=$(grep LogFile "${witness_config_file}" | cut -d: -f2 | cut -d, -f1 | cut -d\" -f2 )
    witness_log_filename=$(basename "${witness_log_file}")
    witness_log_archive="${log_dir}/${witness_log_filename}"
    mkdir -p $(dirname "${witness_log_file}")
    mkdir -p "${witness_db_dir}"
    "${witness_exec}" --conf "${witness_config_file}" --silent --verbose 2>&1 &
    pid=$! ;  sleep 1  # wait a second to get the process ID before the next instance starts
    process_running=$(ps | grep $pid | grep -v grep)
    if [ -z "${process_running}" ] ; then
      echo "** Error running witness server"
      tail -5 "${witness_log_file}"
      exit_on_error 1 "** Error running witness server"
    fi

    tail_pid=$(pgrep -fl tail | grep "${rippled_log_filepath}" | awk '{print $1}')
    kill -9 "$tail_pid" >/dev/null 2>&1 # not to conflict repetitive runs of witness
    tail -f "${witness_log_file}" > "${witness_log_archive}" &

  done
  sleep 5
}

. /etc/os-release

while [ "$1" != "" ]; do
  case $1 in
  --feature)
    shift
    feature="${1:-$feature}"
    ;;

  --product)
    shift
    product="${1:-$product}"
    ;;

  --network)
    shift
    network="${1:-$network}"
    ;;

  --jobID)
    shift
    job_id="${1:-$job_id}"
    ;;

  --jobName)
    shift
    job_name="${1:-$job_name}"
    ;;

  --publishStats)
    shift
    publish_stats="${1:-$publish_stats}"
    ;;

  --rippledRemoteBranch)
    shift
    rippled_remote_branch="${1:-$rippled_remote_branch}"
    ;;

  --clioRemoteBranch)
    shift
    clio_remote_branch="${1:-$clio_remote_branch}"
    ;;

  --localRippledRepoPath)
    shift
    local_rippled_repo_path="${1:-$local_rippled_repo_path}"
    ;;

  --localClioRepoPath)
    shift
    local_clio_repo_path="${1:-$local_clio_repo_path}"
    ;;

  --automationRepoPath)
    shift
    rippled_automation_repo_path="$1"
    ;;

  --mode)
    shift
    install_mode="${1:-$install_mode}"
    ;;

  --rippledVersion)
    shift
    rippled_version="${1:-$latest_version}"
    ;;

  --launchViaValgrind)
    shift
    launch_via_valgrind="${1:-$launch_via_valgrind}"
    if [ "${launch_via_valgrind}" = "true" ] ; then
      standalone_mode="true"
    fi
    ;;

  --stopRippled)
    stop_rippled_flag="true"
    ;;

  --startRippled)
    start_rippled_flag="true"
    ;;

  --ignoreRepoClone)
    ignore_repo_clone="true"
    ;;

  --ignoreClioRepoClone)
    ignore_clio_repo_clone="true"
    ;;

  --ignoreBuildPrereq)
    ignore_build_prereq="true"
    ;;

  --skipUnitTests)
    shift
    skip_unit_tests="${1:-$skip_unit_tests}"
    ;;

  --sidechainAutoSubmit)
    shift
    sidechain_auto_submit="${1:-$sidechain_auto_submit}"
    ;;

  --standaloneMode)
    shift
    standalone_mode="${1:-$standalone_mode}"
    ;;

  --witnessRemoteBranch)
    shift
    witness_remote_branch="${1:-$witness_remote_branch}"
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

build_lib="${rippled_automation_repo_path}/scripts/lib/build_lib.sh"
log_dir="${rippled_automation_repo_path}/logs/product_logs/logs_${time_stamp}"
rippled_build_path="${local_rippled_repo_path}/my_build"
clio_build_path="${local_clio_repo_path}/my_build"
witness_build_path="${local_witness_repo_path}/my_build"
work_dir="${rippled_automation_repo_path}/work_dir"
advance_ledger_script="${rippled_automation_repo_path}/scripts/advance_ledger.sh"

echo "Network: ${network}"

if [ "${feature}" = "${feature_sidechain}" ]; then
  prepare_workspace
  get_rippled
  config_and_start_rippled "rippled" "locking_chain"
  wait_for_rippled_sync "rippled" "locking_chain"
  config_and_start_rippled "rippled" "issuing_chain"
  wait_for_rippled_sync "rippled" "issuing_chain"

  if [ "${standalone_mode}" = "true" ]; then
    get_witness_server
    start_witness_servers
  else
    echo "Network mode: Skipping setting up witness servers"
  fi
else
  prepare_workspace
  stop_rippled "${stop_rippled_flag}"
  get_rippled
  config_and_start_rippled
  wait_for_rippled_sync "rippled"

  if [ "${product}" = "${product_clio}" ]; then
      setup_db_for_clio
      get_clio
      config_and_start_clio
      wait_for_clio_sync
  fi
fi
