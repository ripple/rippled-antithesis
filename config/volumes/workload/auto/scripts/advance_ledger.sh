#!/bin/sh

rippled_exec="$1"
rippled_cfg_file="$2"

if [ -f "${rippled_cfg_file}" ] ; then
  while :
  do
    "${rippled_exec}" ledger_accept --conf="${rippled_cfg_file}" > /dev/null 2>&1
    sleep 1
  done
else
  echo "Error: rippled.cfg path not provided"
  exit 1
fi

