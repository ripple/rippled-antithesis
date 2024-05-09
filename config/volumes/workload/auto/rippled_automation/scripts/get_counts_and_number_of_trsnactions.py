#!/usr/bin/env python
import time
import os
import sys
import time, threading
import requests
HEADERS = {'Content-Type': 'application/json'}
URL = "http://localhost:51234/"
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
WAIT_SECONDS = 4


def foo():
    payload = "{\n \"method\":\"get_counts\",\n \"params\": [\n{\n}\n]\n}"
    response = requests.request("POST", URL, headers=HEADERS, data=payload)
    print(response.text.encode('utf8'))

    payload = "{\n\"method\": \"ledger\",\n\"params\": [\n{\n\"ledger_index\": \"validated\",\n\"validated\": true,\n" \
              "\"transactions\": true\n}\n]\n}"
    response = requests.request("POST", URL, headers=HEADERS, data=payload)
    print(response.text.encode('utf8'))

    threading.Timer(WAIT_SECONDS, foo).start()


foo()
