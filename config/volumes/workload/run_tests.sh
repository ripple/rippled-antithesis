#!/bin/bash

cd auto

for i in {10..1}; do echo "waiting ... $i" && sleep 10s ; done

# The framework is hard-coded to try to run on a real network so replace the actual devnet test fund account with the real genesis account
sed -i 's/rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb/rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh/' ./rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/constants.py
sed -i 's/snRzwEoNTReyuvz6Fb1CDXcaJUQdp/snoPBrXtMeMyMHUVTgbuqAfg1SUTb/' ./rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/constants.py

pytest --hostname rippled --port 5005 rippled_automation/rippled_end_to_end_scenarios/end_to_end_tests/payment_test.py::test_xrp_simple_payment
# pytest --hostname rippled --port 5005 -m smoke
