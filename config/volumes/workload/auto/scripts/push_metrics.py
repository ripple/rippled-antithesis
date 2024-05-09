################################################################################
# This script parses the response from 'rippled server_info counters' for rpc,
# job_queues, etc and publishes the metrics to prometheus.
# This script is run on the client handles, and p2p servers to gather stats for
# monitoring.
#
# Usage:
# 1. Copy the script to ~/scripts
# 2. Start the script:
#   $ nohup python3 -u ~/scripts/push_metrics.py &
################################################################################

import atexit
import json
import os
import requests
import time
import socket
import subprocess
import sys

# Parameters
push_gateway = 'http://34.222.118.252:9091'
job_name = 'automation_exporter'
instance_name = socket.gethostname()
iteration_interval = 10  # seconds
script_path = os.path.dirname(os.path.realpath(__file__))
rippled = '/opt/ripple/bin/rippled --conf /etc/opt/ripple/rippled.cfg --silent'

# Computed constants
url = '{}/metrics/job/{}/instance/{}'.format(push_gateway, job_name, instance_name)

# endpoint_targets define sections of 2 kinds
# 1. objects that have a dictionary of endpoints; so there is no final endpoint defined in this list
# Example: result -> info -> counters -> rpc, these paths lead to a dictionary from task type to object of
# counters (e.g. `started`, `finished`, `duration_us`)
# 2. objects that have a final endpoint; so 'end_points' is defined in the list.
# An empty 'end_points' list parses all the end_points in that path
# Example: result -> info -> validated_leger -> age
endpoint_targets = [
    {
        'rippled_command': 'server_info counters',
        'targets': [
            {
                'path': ['result', 'info', 'counters', 'rpc'],
                'metric_type': 'counter'
            },
            {
                'path': ['result', 'info', 'counters', 'job_queue'],
                'metric_type': 'counter'
            },
            {
                'path': ['result', 'info', 'validated_ledger'],
                'end_points': ['age'],
                'metric_type': 'gauge'
            },
        ]
    },
    {
        'rippled_command': 'get_counts',
        'targets': [
            {
                'path': ['result'],
                'end_points': [],
                'metric_type': 'gauge'
            },
        ]
    }
]


@atexit.register
def cancel_push():
    print('Cancel pushing metrics to prometheus...')
    time.sleep(15)
    requests.delete(url=url)


def parse_endpoints():
    data = ''
    for endpoint_target in endpoint_targets:
        cmd = '{} {}'.format(rippled, endpoint_target['rippled_command'])
        response = run_command(cmd)
        if response:
            for target in endpoint_target['targets']:
                metric_type = target['metric_type']
                section = response
                section_found = True
                for step in target['path']:
                    try:
                        section = section[step]
                    except KeyError as cause:
                        print('Cannot parse JSON: {}'.format(cause), file=sys.stderr)
                        section_found = False
                        break

                if section_found:
                    metric_prefix = endpoint_target['rippled_command'].split(' ')[-1] \
                        if len(target['path']) == 1 else target['path'][-1]

                    if 'end_points' in target:
                        for end_point in target['end_points'] if target['end_points'] else section.keys():
                            key = '{}_{}'.format(metric_prefix, end_point)
                            try:
                                value = section[end_point]
                                try:
                                    if not isinstance(value, list):
                                        if isinstance(value, str):
                                            value = int(value)

                                        data += '# TYPE {} {}\n'.format(key.replace('::', '_'), metric_type)
                                        data += '{}{{object="{}"}} {}\n'.format(key.replace('::', '_'), metric_prefix,
                                                                                value)
                                except ValueError as cause:
                                    print('Cannot publish value: {}'.format(value), file=sys.stderr)
                            except KeyError as cause:
                                print('Cannot parse JSON: {}'.format(cause), file=sys.stderr)
                    else:
                        data += ''.join(
                            '# TYPE {}_{} {}\n'.format(metric_prefix, key, metric_type)
                            for key in next(iter(section.values())).keys()
                        )

                        for task, counters in section.items():
                            for key, value in counters.items():
                                data += '{}_{}{{task="{}"}} {}\n'.format(metric_prefix, key, task, value)

    return data


def run_command(cmd):
    if not isinstance(cmd, list):
        cmd = cmd.split(' ')
    try:
        completed_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = completed_process.communicate()

        try:
            json_data = json.loads(out.decode())

            output_file=os.path.join(script_path, "{}.json".format(cmd[-1]))
            print("Output file: {}".format(output_file))
            with open(output_file, 'w') as fp:
                json.dump(json_data, fp)

        except Exception as cause:
            print('Cannot parse JSON: {}'.format(cause), file=sys.stderr)
            cancel_push()
            return None

        if not json_data or 'error' in json_data:
            print('Error connecting to rippled', file=sys.stderr)
            cancel_push()
            return None

    except Exception as e:
        print("Error: {}".format(e))
        cancel_push()
        return None

    return json_data


def push_metrics():
    data = parse_endpoints()

    requests.post(url=url, data=data)
    print('Pushed metrics to {}:\n{}'.format(push_gateway, data))
    log_file = os.path.join(script_path, "output.log")
    print("Log file: {}".format(log_file))
    with open(log_file, 'w') as fp:
        fp.write(data)


if __name__ == '__main__':
    while True:
        print('\n**********************************************************************')
        push_metrics()
        print('\nWait {} seconds before the next iteration...'.format(iteration_interval))
        time.sleep(iteration_interval)
