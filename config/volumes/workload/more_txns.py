from random import SystemRandom
from types import SimpleNamespace
import asyncio
import logging as log
import requests
import sys


MAX_NUMBER_OF_ACCOUNTS = 50
MAX_TOKEN = 1000
CLEAR_NORIPPLE = 262144
DEFAULT_PAYMENT = 1000_000000 # 1000 XRP per account by default

log_level = log.INFO
FORMAT = "[%(asctime)s %(filename)s->%(funcName)s() %(lineno)s] %(levelname)s: %(message)s"
log.getLogger("urllib3").setLevel(log.WARNING)

log.basicConfig(format=FORMAT,
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=log_level,
)
genesis_account = SimpleNamespace()
genesis_account.account_id = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
genesis_account.seed = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"

host, port = sys.argv[1:3]
# host, port = "172.18.0.5", 5005

url  = f"http://{host}:{port}"

urand = SystemRandom()
randrange = urand.randrange
sample = urand.sample

s = requests.Session()

async def current_ledger() -> int:
    payload = {"method": "ledger_current"}
    try:
        tx_response = s.post(url, json=payload)
        return int(tx_response.json()["result"]["ledger_current_index"])
    except Exception as e:
        log.error(repr(e))
        raise

async def wait_until_ledger(wait_for_ledger_index):
    log.debug(f"Waiting for {wait_for_ledger_index} to close...")
    while await current_ledger() <= wait_for_ledger_index:
        await asyncio.sleep(2)
    log.debug(f"Ledger {wait_for_ledger_index + 1} arrived.")

async def wait_for_next_ledger():
    await wait_for_n_ledgers(0)

async def wait_for_n_ledgers(n):
    await wait_until_ledger(await current_ledger() + n)

async def wallet_propose():
    try:
        response = s.post(url, json={"method": "wallet_propose"})
        result = response.json()["result"]
        account = SimpleNamespace()
        account.account_id = result["account_id"]
        account.seed = result["master_seed"]
        return account
    except Exception as e:
        log.error(repr(e))

async def send_payment(destination, source=genesis_account, amount: dict|int=DEFAULT_PAYMENT):
    payment_payload = {
        "method": "submit",
        "params": [{
            "secret": source.seed,
            "tx_json": {
                "TransactionType": "Payment",
                "Account": source.account_id,
                "Destination": destination.account_id,
                "Amount": amount,
                # "Sequence": 1
            }
        }]
    }

    # payment_payload.update({"method": "whoops"}) if urand(2) else ""
    try:
        wait = 3
        response = s.post(url, json=payment_payload)
        result = response.json()["result"]
        while result.get("error") == "highFee":
            print("Waiting for fee to die down.")
            await wait_for_n_ledgers(wait)
            response = s.post(url, json=payment_payload)
            result = response.json()["result"]
            if result.get("error") == "highFee":
                wait += 1
        # log.debug(json.dumps(result, indent=2))
        return result
    except Exception as e:
        log.error(repr(e))
        raise

async def create_account():
    account = await wallet_propose()
    try:
        send_payment_response = await send_payment(destination=account)
        return (send_payment_response.get("status"), account)
    except Exception as e:
        log.error(repr(e))
        raise

async def create_trustline(account, amount, limit=1e15):
    trustline_limit = dict(amount, value=str(int(limit)))

    log.debug((f"Creating Trustline for {account.account_id} for {limit} {amount['currency']}"))
    log.debug(f"\tissued by: {amount['issuer']}")

    trustset_payload = {
        "method": "submit",
        "params": [{
            "tx_json": {
                "TransactionType": "TrustSet",
                "Account": account.account_id,
                "LimitAmount": trustline_limit
            },
            "secret": account.seed
        }]
    }
    try:
        response = s.post(url, json=trustset_payload)
        result = response.json()["result"]
        await wait_for_next_ledger()
        return result
    except Exception as e:
        log.error(repr(e))
        raise

async def distribute_currency(source, destination, currency: str="USD", amount: str="1000"):
    token = {
        "issuer": source.account_id,
        "currency": currency,
        }
    await asyncio.sleep(3)
    result = await create_trustline(destination, token)
    payment_amount = dict(token, value=amount)
    await send_payment(destination, source, payment_amount)

async def mint_nft(account, taxon=0):
    payload = {
        "method": "submit",
        "params": [{
            "tx_json": {
                "TransactionType": "NFTokenMint",
                "Account": account.account_id,
                "NFTokenTaxon": taxon
            },
            "secret": account.seed
        }]
    }
    mint_response = s.post(url, json=payload)
    log.debug(mint_response)
    if mint_response.json()["result"]["status"] == "success":
        log.debug(mint_response.json()["result"])
        log.debug("Minted nft")
    return mint_response

async def main():
    no_of_accounts = randrange(MAX_NUMBER_OF_ACCOUNTS)
    accounts = []
    failed_accounts = []
    results = []

    async with asyncio.TaskGroup() as tg:
        for _ in range(no_of_accounts):
            results.append(tg.create_task(create_account()))
    log.info(f"Tried creating {no_of_accounts} accounts during ledger: {await current_ledger()}")

    for result in results:
        result = result.result()
        accounts.append(result[1]) if result[0] == 'success' else failed_accounts.append(result[1])
    await wait_for_next_ledger()

    number_of_accounts = len(accounts)
    log.info(f"Tried to create {number_of_accounts} accounts.")
    number_of_failed_accounts = len(failed_accounts)
    log.info(f"Failed {number_of_failed_accounts}.")
    return accounts

async def distribute(accounts):
    number_of_accounts = len(accounts)
    print(f"{len(accounts)} accounts created.")
    async with asyncio.TaskGroup() as tg:
        # print(accounts)
        for _ in range(randrange(number_of_accounts)):
            alice, bob = sample(accounts, 2)
            random_amount = str(randrange(MAX_TOKEN))
            tg.create_task(distribute_currency(alice, bob, amount=random_amount))
            tg.create_task(mint_nft(alice, taxon=0))

accounts = asyncio.run(main())
asyncio.run(distribute(accounts))
