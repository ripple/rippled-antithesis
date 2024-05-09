#!/bin/sh

auto_submit_mode="true"
network="devnet"
standalone_mode="false"

usage() {
  echo "Usage: $0 [Optional parameters]"
  echo "  --sidechainAutoSubmit true (auto-submit sidechain AddAttestation txns, default: ${auto_submit_mode})"
  echo "  --standaloneMode true (to run locking chain/issuing chain in standalone mode. default: network mode)"

  exit 1
}

while [ "$1" != "" ]; do
  case $1 in
  --network)
    shift
    network="${1:-$network}"
    ;;

  --sidechainAutoSubmit)
    shift
    auto_submit_mode="${1:-$auto_submit_mode}"
    ;;

  --standaloneMode)
    shift
    standalone_mode="${1:-$standalone_mode}"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

rippled_exec=/opt/ripple/bin/rippled
witness_exec=/opt/xbridge-witness/xbridge_witnessd
sidechain_config_dir=configs/sidechain

if [ "${standalone_mode}" = "true" ]; then
  sidechain_config_dir="configs/rippled/sidechain/standalone"
  mode="standalone"
else
  sidechain_config_dir="configs/rippled/sidechain/$network"
  mode="network"
fi
witness_configs_dir="${sidechain_config_dir}/witness"

echo ""
echo "** Mode: ${mode}"
echo "** Config directory: ${sidechain_config_dir}"
echo "** Stopping rippled & witness servers..."
pkill -9 rippled ; pkill -9 witness

echo "** Deleting rippled db..."
rm -rf /var/lib/rippled/issuing_chain/db/*
rm -rf /var/lib/rippled/locking_chain/db/*

echo "** Deleting witness db & logs..."
for witness_config_file in "${witness_configs_dir}"/*json
do
  witness_db_dir=$(grep DBDir "${witness_config_file}" | cut -d: -f2 | cut -d, -f1 | cut -d\" -f2 )
  if [ -d "${witness_db_dir}" -a "${witness_db_dir}" != "." ] ; then
    rm -rf "${witness_db_dir}"/*
  fi
  witness_log_file=$(grep LogFile "${witness_config_file}" | cut -d: -f2 | cut -d, -f1 | cut -d\" -f2 )
  witness_log_dir=$(dirname "${witness_log_file}")
  if [ -d "${witness_log_dir}" -a "${witness_log_dir}" != "." ] ; then
    rm -rf "${witness_log_dir}"/*
  fi
done

echo "** Starting mainchain & sidechain rippled..."
if [ "${standalone_mode}" = "true" ] ; then
  "${rippled_exec}" --conf "${sidechain_config_dir}/locking_chain/rippled.cfg" --start -a --silent 2>&1 &
  "${rippled_exec}" --conf "${sidechain_config_dir}/issuing_chain/rippled.cfg" --start -a --silent 2>&1 &
  sleep 2  # Wait for rippled to be up before starting witness

  echo "** Setting auto-submit mode: ${auto_submit_mode}"
  if [ "$auto_submit_mode" = "true" ] ; then
    sed -i.tmp 's/\"ShouldSubmit\"\:\ false/\"ShouldSubmit\"\:\ true/g' "${witness_configs_dir}"/witness*.json
  else
    sed -i.tmp 's/\"ShouldSubmit\"\:\ true/\"ShouldSubmit\"\:\ false/g' "${witness_configs_dir}"/witness*.json
  fi

  for witness_config_file in "${witness_configs_dir}"/*json
  do
    echo "** Starting witness ${witness_config_file}..."
    witness_db_dir=$(grep DBDir "${witness_config_file}" | cut -d: -f2 | cut -d, -f1 | cut -d\" -f2 )
    mkdir -p "${witness_db_dir}"
    "${witness_exec}" --conf "${witness_config_file}" --silent --verbose &
    pid=$! ;  sleep 1  # wait a second to get the process ID before the next instance starts
    process_running=$(ps | grep $pid | grep -v grep)
    if [ -z "${process_running}" ] ; then
      echo "** Error running witness server"
      tail -5 "${witness_log_file}"
      exit 1
    fi
  done
else
  "${rippled_exec}" --conf "${sidechain_config_dir}/locking_chain/rippled.cfg" --silent 2>&1 &
  "${rippled_exec}" --conf "${sidechain_config_dir}/issuing_chain/rippled.cfg" --silent 2>&1 &
  sleep 2  # Wait for rippled to be up before starting witness
fi

pgrep -fl "${rippled_exec}" | grep -v grep
pgrep -fl "${witness_exec}" | grep -v grep

echo "\n** Make sure rippled db on both chains are synced before submitting any transaction"
