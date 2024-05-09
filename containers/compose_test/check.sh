#!/usr/bin/env bash

address=$(docker network inspect rippled-net | jq -r .[0].IPAM.Config[0].Gateway)
address=$(echo "${address%${address##*.}}")
curl ${address}{2,3,4,5,6}:5005 \
    --silent \
    --data '{"method": "server_info"}' | jq -r '.result.info | {hostid, build_version, complete_ledgers, server_state, uptime}'