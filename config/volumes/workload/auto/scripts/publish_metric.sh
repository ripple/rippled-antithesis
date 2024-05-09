#!/bin/sh

################################################################################
# This script is to publish metric to prometheus. The script automatically
# determines if it has to do a push to gateway server or endpoint, based on
# the job ID passed
#
# Usage: sh scripts/publish_metric.sh
#     --metric <key:value>
#     --labels <optional: release:1.8,version=beta>
#     [--jobID <if passed, uses pushGatewayServer, else endpoint>]
#
# Example: To publish metric,
# $ sh scripts/publish_metric.sh --metric key:5 --labels "release:1.8,version=beta"
#
################################################################################

metric=""
labels=""
job_id="LocalRun"
prometheus_gateway_server="http://172.16.0.69:9091"  # public: 34.222.118.252

usage() {
  echo "Usage: $0 <parameters>"
  echo "  --metric <key:value>"
  echo "  --labels <optional: release:1.8,version=beta>"
  echo "  --jobID <if passed, uses pushGatewayServer, else endpoint>"
  exit 1
}

exit_on_error() {
  exit_code=$1
  if [ $exit_code -ne 0 ]; then
    echo "Exit code: $exit_code"
    exit $exit_code
  fi
}

while [ "$1" != "" ]; do
  case $1 in
  --metric)
    shift
    metric="${1:-$metric}"
    ;;

  --labels)
    shift
    labels="${1:-labels}"
    ;;

  --jobID)
    shift
    job_id="${1:-$job_id}"
    ;;

  --help | *)
    usage
    ;;
  esac
  shift
done

if [ -n "$metric" ]; then
  if [ ! "$job_id" = "LocalRun" ]; then
    echo "  Using pushgateway server to push metrics"

    python3 scripts/prometheus_client/custom_metric_exporter.py --pushGatewayServer "${prometheus_gateway_server}" --sendMetric "${metric}" --labels "${labels}"
    exit_on_error $?
  else
    echo "  Using endpoint to push metrics"

    trap "python3 scripts/prometheus_client/custom_metric_exporter.py --stop" EXIT
    python3 scripts/prometheus_client/custom_metric_exporter.py --listen &
    sleep 1
    python3 scripts/prometheus_client/custom_metric_exporter.py --sendMetric "${metric}" --labels "${labels}"
    exit_on_error $?
    sleep 20
  fi
else
  usage
fi
