#!/usr/bin/env sh
set +e

################################################################################
# Script to be run post testrun to capture core dump, if any
################################################################################

cat /proc/sys/kernel/core_pattern
echo "sleep 2 mins before checking for core..."
sleep 120

core_filename="core.*"
rippled_exec="/opt/ripple/bin/rippled"
witness_exec="/opt/xbridge-witness/xbridge_witnessd"
core_archive_dir=logs/corefiles

core_files=$(find . -type f -maxdepth 1 -name "${core_filename}")
if [ -n "${core_files}" ] ; then
  mkdir -p "${core_archive_dir}"
  for core_file in $(echo "${core_files}")
  do
    ls -ld "${core_file}"
    echo "Copy core dump ${core_file} to ${core_archive_dir} ..."
    cp "${core_file}" "${core_archive_dir}"

  done
  echo "Copy rippled binary [${rippled_exec}]..."
  cp "${rippled_exec}" "${core_archive_dir}"

  if [ -f "${witness_exec}" ]; then
    echo "Copy witness binary [${witness_exec}]..."
    cp "${witness_exec}" "${core_archive_dir}"
  fi
fi
