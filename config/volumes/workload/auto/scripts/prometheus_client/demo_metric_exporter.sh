#!/bin/sh
  
# Stop custom exporter from listen mode at exit
trap "python3 custom_metric_exporter.py --stop" EXIT

# Start custom exporter in listen mode
python3 custom_metric_exporter.py --listen &
sleep 1

while :
do
    rand=$(( ( RANDOM % 10 )  + 1 ))
    metric="random_number:${rand}"
    echo "metric -> ${metric}"
    python3 custom_metric_exporter.py --sendMetric "${metric}" --labels "version:1.8,rel:beta"
    sleep 5
done

