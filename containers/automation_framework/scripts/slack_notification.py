import argparse
import json
import requests

# ripplex-automation
# WEBHOOK = "https://hooks.slack.com/services/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"
# ripplex-automation-validation
WEBHOOK = "https://hooks.slack.com/services/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"


def send_slack_message(message):
    payload = {"text": message}
    return requests.post(WEBHOOK, json.dumps(payload))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--message', required=True, help="Notification message")
    return parser.parse_args()


def main(message):
    send_slack_message(message)


if __name__ == '__main__':
    args = parse_arguments()
    main(args.message)
