import time
import requests
import json
import configparser
from requests.exceptions import ConnectionError

SERVERS = []
SERVERS_NOT_RESPONDING = []
PAYLOAD = "{\n\"method\": \"server_state\",\n \"params\": [\n{}\n]\n}"
HEADERS = {'Content-Type': 'text/plain'}
OPERATIONAL = "operational"
MAINTENANCE = "under_maintenance"
DEGRADED_PERFORMANCE = "degraded_performance"
PARTIAL_OUTAGE = "partial_outage"
MAJOR_OUTAGE = "major_outage"


class Node:

    def __init__(self, server_ip, component_id, page_id, api_key, rippled_port):
        self.server_ip = server_ip
        self.component_id = component_id
        self.page_id = page_id
        self.api_key = api_key
        self.rippled_port = rippled_port


def parse_config_file():
    config = configparser.ConfigParser()
    config.read('config.ini')
    for node in config.sections():
        SERVERS.append(Node(server_ip=node,
                            component_id=(config.get(node, 'component.id')),
                            page_id=(config.get(node, 'page.id')),
                            api_key=(config.get(node, 'apikey')),
                            rippled_port=(config.get(node, 'rippled.port'))))


def main():
    while True:

        for node in SERVERS_NOT_RESPONDING:
            url = "http://" + node.server_ip + ":51234/"
            try:
                response = requests.request("POST", url, headers=HEADERS, data=PAYLOAD)
                response_result = json.loads(response._content.decode('utf-8'))

                # if state is proposing, syncing or full then dont do anything
                if response_result['result']['state']['server_state'] == 'proposing' or \
                        response_result['result']['state']['server_state'] == 'syncing' or \
                        response_result['result']['state']['server_state'] == 'full':
                    update_status(OPERATIONAL, node)
                    SERVERS_NOT_RESPONDING.remove(node)
                    SERVERS.append(node)

            except ConnectionError as e:
                print("Server is still not reachable")

        for node in SERVERS:
            url = "http://" + node.server_ip + ":51234/"

            try:
                response = requests.request("POST", url, headers=HEADERS, data=PAYLOAD)
                response_result = json.loads(response._content.decode('utf-8'))

                # if state is proposing, syncing or full then dont do anything
                if response_result['result']['state']['server_state'] == 'proposing' or \
                        response_result['result']['state']['server_state'] == 'syncing' or \
                        response_result['result']['state']['server_state'] == 'full':
                    print("ok")

                else:
                    SERVERS_NOT_RESPONDING.append(node)
                    SERVERS.remove(node)
                    update_status(PARTIAL_OUTAGE, node)

            except ConnectionError as e:
                SERVERS_NOT_RESPONDING.append(node)
                SERVERS.remove(node)
                update_status(PARTIAL_OUTAGE, node)
                continue

        time.sleep(5)
        print('\n')


def update_status(status, node):
    url = "https://api.statuspage.io/v1/pages/" + node.page_id + "/components/" + node.component_id
    response = requests.request("PUT", url, headers={'Authorization': node.api_key},
                                data='{"component": {"status": "' + status + '"}}')
    print(response.text.encode('utf8'))


if __name__ == "__main__":
    parse_config_file()
    main()
