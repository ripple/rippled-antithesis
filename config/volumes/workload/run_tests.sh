#!/bin/bash

if [ -x /opt/ripple/bin/rippled ] && [ -r /etc/opt/ripple/rippled.cfg ]; then
  # Note, this will be forked
  /opt/ripple/bin/rippled --conf /etc/opt/ripple/rippled.cfg 2> ${ANTITHESIS_OUTPUT_DIR:-.}/rippled.log &
else
  echo "Cannot start rippled" && exit 1
fi

cd auto

echo "Waiting for $@"
DONE=0
while [ $DONE -eq 0 ]; do
  DONE=1
  PEERS_EXPECTED=6
  for i in localhost $@; do
    STATE=$(curl --silent --data '{"method": "server_info"}' http://$i:5005/)
    echo $STATE | jq -r '.result.info.server_state' | grep -E "^proposing$|^full$" >/dev/null || DONE=0
    echo $STATE | jq -r '.result.info.peers' | grep -E "^${PEERS_EXPECTED}$" >/dev/null || DONE=0
    echo $STATE | jq -r '.result.info.validated_ledger' | grep -vE "^null$" >/dev/null || DONE=0
    [ $DONE -eq 0 ] && echo "waiting ..." && sleep 5s && break
  done
done

# The framework is hard-coded to try to run on a real network so replace the actual devnet test fund account with the real genesis account
sed -i 's/rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb/rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh/' ./rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/constants.py
sed -i 's/snRzwEoNTReyuvz6Fb1CDXcaJUQdp/snoPBrXtMeMyMHUVTgbuqAfg1SUTb/' ./rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/constants.py

echo "Workload initialization complete"

while true; do
  echo "Iteration ${it:=1}"
  python ~/more_txns.py localhost 5005
  ((it++))
done
