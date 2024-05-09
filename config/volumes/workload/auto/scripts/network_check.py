################################################################################
# This script is used to validate a rippled network by:
# 1. Verifying "server_state"
# 2. Perform a 1 drop payment transaction
#
# Usage:
#   python3 scripts/network_check.py [optional parameter]
#       [--rippledServer <rippled host:port (default: localhost:51234)>
################################################################################

import argparse
import json
import logging
import requests
import time

GENESIS_ACCOUNT_ID = "rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb"
GENESIS_ACCOUNT_SEED = "snRzwEoNTReyuvz6Fb1CDXcaJUQdp"
DEFAULT_RIPPLED_SERVER = "localhost:51234"
INITIAL_BALANCE = "20000000"
TRANSFER_AMOUNT = "1"
logging.basicConfig(level=logging.INFO,
                    format='\r%(asctime)s (%(filename)20s:%(lineno)-4s) %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class RippledServer(object):
    def __init__(self, rippled_server=DEFAULT_RIPPLED_SERVER):
        self.rippled_server = "http://{}".format(rippled_server)

    def run(self):
        server_info = self.execute_transaction(payload={}, method="server_info")
        assert server_info["info"]["server_state"] == ("full" or "proposing"), "Server state not full/proposing"
        logging.info("Server state: {}".format(server_info["info"]["server_state"]))

        alice = self.create_account()

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": GENESIS_ACCOUNT_ID,
                "Destination": alice["account_id"],
                "Amount": TRANSFER_AMOUNT,
            },
            "secret": GENESIS_ACCOUNT_SEED
        }
        response = self.execute_transaction(payload=payload, method="submit")
        assert int(self.get_account_balance(alice["account_id"])) == \
               int(INITIAL_BALANCE) + int(TRANSFER_AMOUNT), "Account balance mismatch"
        logging.info("Account balance matches!")

    def create_account(self, amount=INITIAL_BALANCE):
        payload = {
            "tx_json": {
            }
        }
        wallet = self.execute_transaction(payload=payload, method="wallet_propose")

        payload = {
            "tx_json": {
                "TransactionType": "Payment",
                "Account": GENESIS_ACCOUNT_ID,
                "Destination": wallet["account_id"],
                "Amount": amount,
            },
            "secret": GENESIS_ACCOUNT_SEED
        }
        self.execute_transaction(payload=payload, method="submit")

        max_retries = 15
        count = 1
        wait_time = 2  # seconds
        while count <= max_retries:
            account_objects = self.get_account_objects(wallet["account_id"])
            if "account" in account_objects and account_objects["account"] == wallet["account_id"]:
                return wallet

            logging.debug(
                "Wait {} seconds and retry for account to be validated (attempt: {}/{})".format(wait_time, count,
                                                                                                max_retries))
            time.sleep(wait_time)
            count += 1

        raise Exception("  Account not added to ledger in {} seconds".format(wait_time * max_retries))

    def get_account_objects(self, account_id):
        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": "validated"
            },
        }
        return self.execute_transaction(payload=payload, method="account_objects")

    def execute_transaction(self, payload, method):
        tx_json = None
        if "tx_json" in payload:
            tx_json = payload["tx_json"]
        if "secret" in payload:
            secret = payload["secret"]
            request = {"method": method, "params": [dict(tx_json=tx_json, secret=secret)]}
        else:
            request = {"method": method, "params": [tx_json]}

        try:
            logging.debug("Request: {}".format(json.dumps(request)))
            response = requests.post(self.rippled_server, json.dumps(request))
            response_result = json.loads(response.content.decode('utf-8'))['result']
            logging.debug("Response: {}".format(response_result))

            if "engine_result" in response_result and (
                    response_result["engine_result"] == "tesSUCCESS" or
                    response_result["engine_result"] == "terQUEUED"):
                if self.is_transaction_validated(response_result):
                    logging.info("  Transaction validated")

        except requests.exceptions.RequestException as e:
            raise Exception("Failed to establish connection to rippled")

        return response_result

    def tx(self, tx_id):
        payload = {
            "tx_json": {
                "transaction": tx_id,
                "binary": False
            }
        }
        return self.execute_transaction(payload=payload, method="tx")

    def get_account_balance(self, account_id):
        payload = {
            "tx_json": {
                "account": account_id,
                "ledger_index": "current",
                "strict": True,
                "queue": True
            },
        }
        account_info = self.execute_transaction(payload=payload, method="account_info")
        try:
            return account_info['account_data']['Balance']
        except KeyError as e:
            return 0

    def is_transaction_validated(self, response, engine_result="tesSUCCESS"):
        tx_id = response["tx_json"]["hash"]
        logging.debug("Transaction ID: '{}'".format(tx_id))
        logging.debug("Response to verify: {}".format(response))

        max_timeout = 30  # max sec for validating tnx
        start_time = time.time()
        end_time = start_time + max_timeout
        while time.time() <= end_time:
            tx_response = self.tx(tx_id)
            logging.debug("Txn response \"validated\": {}".format(tx_response["validated"]))
            if tx_response["validated"]:
                if response["engine_result"] == "terQUEUED":
                    logging.debug("  As expected, transaction is validated")
                    return True
                else:
                    if tx_response["meta"]["TransactionResult"] == engine_result:
                        logging.debug("  As expected, transaction is validated")
                        return True
            logging.debug("  Wait for a second and retry...")
            time.sleep(1)
        raise Exception("  Transaction not validated: {}".format(tx_id))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rippledServer', default=DEFAULT_RIPPLED_SERVER,
                        help="rippled server (default: {})".format(DEFAULT_RIPPLED_SERVER))
    return parser.parse_args()


def main(rippled_server):
    rippled = RippledServer(rippled_server)
    server_info = rippled.execute_transaction(payload={}, method="server_info")
    assert server_info["info"]["server_state"] == ("full" or "proposing"), "Server state not full/proposing"
    logging.info("Server state: {}".format(server_info["info"]["server_state"]))

    logging.info("Create account...")
    alice = rippled.create_account()

    logging.info("Payment transaction...")
    payload = {
        "tx_json": {
            "TransactionType": "Payment",
            "Account": GENESIS_ACCOUNT_ID,
            "Destination": alice["account_id"],
            "Amount": TRANSFER_AMOUNT,
        },
        "secret": GENESIS_ACCOUNT_SEED
    }
    response = rippled.execute_transaction(payload=payload, method="submit")
    assert int(rippled.get_account_balance(alice["account_id"])) == \
           int(INITIAL_BALANCE) + int(TRANSFER_AMOUNT), "Account balance mismatch"
    logging.info("Account balance matches!")


if __name__ == '__main__':
    cmd_args = parse_arguments()
    main(cmd_args.rippledServer)
