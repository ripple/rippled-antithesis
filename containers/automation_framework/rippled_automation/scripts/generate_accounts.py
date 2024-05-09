import requests
import json
import time
url = "http://localhost:51234/"
account_json = {}
list_of_accounts = []


def generate_accounts(number_of_accounts = 10):
    for i in range(number_of_accounts):
        payload = "{\n    \"method\": \"wallet_propose\",\n    \"params\": [\n        {}\n    ]\n}"
        time.sleep(1)
        account_info = requests.request("POST", url, data=payload)
        payload = "{\n   \"method\":\"submit\",\n" \
                  "   \"params\":[\n{\n\"tx_json\":{\n\"Flags\": \"2147483648\"," \
                  "\n\"Account\":\"rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb\",\n\"Fee\":\"10\",\n\"Amount\":\"100000000000\"," \
                "\n\"Destination\":\"<text>\",\n\"TransactionType\":\"Payment\"\n}," \
                "\n\"secret\":\"snRzwEoNTReyuvz6Fb1CDXcaJUQdp\"\n}\n]\n}"
        print(account_info.json()['result']['account_id'])
        payload = payload.replace("<text>", account_info.json()['result']['account_id'])
        response = requests.request("POST", url, data=payload)
        print (str(response))
        if response.status_code == 200:
            # if funding was successful then add this to the json array
            print(i)
            list_of_accounts.append(account_info.json().get('result'))
        else:
            print("Issues with funding these are the accounts created so far")
            outfile = open('accounts' + str(time.time()) + ' .json', 'w')
            outobj = {
                'num_accounts': number_of_accounts,
                'drops_amount': 100000000000,
                'fee': 10,
                'accounts': list_of_accounts
            }
            # here make the accounts.json file and exit
    print("Opening file now")
    outfile = open('accounts' + str(time.time()) + ' .json', 'w')
    outobj = {
        'num_accounts': number_of_accounts,
        'drops_amount': 100000000000,
        'fee': 10,
        'accounts': list_of_accounts
    }
    json.dump(outobj, outfile)
    print("closing file now")


if __name__ == "__main__":
    generate_accounts(1000)
