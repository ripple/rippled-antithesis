import requests
import time
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.src.commands.account import Account
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper

log = log_helper.get_logger()


class AMM_mixin:

    def amm_create(self, account, asset_1, asset_2, trading_fee=constants.DEFAULT_AMM_TRADING_FEE,
                   fee=constants.DEFAULT_AMM_CREATE_FEE, wait_for_ledger_close=True, verbose=True):

        payload = {
            "tx_json": {
                "TransactionType": "AMMCreate",
                "Account": account.account_id,
                "TradingFee": trading_fee,
                "Amount": asset_1,
                "Amount2": asset_2,
                "Fee": fee,
            }
        }

        self.set_default_ripple(account)

        response = self.execute_transaction(secret=account.master_seed, payload=payload,
                                            wait_for_ledger_close=wait_for_ledger_close, verbose=verbose)


        return response

    def amm_bid(self, account_object, asset_1, asset_2, sequence=None, bid_min=None, bid_max=None, auth_accounts=None):

        for asset in [asset_1, asset_2]:  # NOTE: A currency amount without a "value" isn't strictly necessary,
            if not isinstance(asset, str):  # but it's removed here anyway.
                if asset.get('value'):
                    del asset['value']

        payload = {
            "secret": account_object.master_seed,
            "tx_json": {
                "TransactionType": "AMMBid",
                "Account": account_object.account_id,
                "Asset": asset_1,
                "Asset2": asset_2,
            }
        }

        if sequence is not None:
            payload['tx_json']['Sequence'] = sequence
        if bid_min is not None:
            payload['tx_json']['BidMin'] = bid_min
        if bid_max is not None:
            payload['tx_json']['BidMax'] = bid_max
        if auth_accounts is not None:
            payload['tx_json']['AuthAccounts'] = auth_accounts

        return self.execute_transaction(payload=payload)

    def amm_deposit(self, account, asset_1, asset_2,
                    amount=None,
                    amount2=None,
                    lp_token_out=None,
                    eprice=None,
                    mode='tfSingleAsset', verbose=True):

        asset_1, asset_2 = [
            constants.XRP_ASSET if not isinstance(asset, dict)
            else asset for asset in [asset_1, asset_2]
        ]
        payload = {
            "tx_json": {
                "TransactionType": "AMMDeposit",
                "Account": account.account_id,
                "Asset": asset_1,
                "Asset2": asset_2,
                "Amount": amount,
                "Fee": constants.DEFAULT_TRANSACTION_FEE,
                "Flags": constants.AMM_DEPOSIT_FLAGS[mode],
            },
            "secret": account.master_seed
        }

        if mode == 'tfTwoAsset' and amount2:
            payload['tx_json']['Amount2'] = amount2

        if mode in ['tfOneAssetLPToken', 'tfLPToken'] and lp_token_out:
            payload['tx_json']['LPTokenOut'] = lp_token_out
            if mode == 'tfLPToken' and lp_token_out:
                del payload['tx_json']['Amount']

        try:
            deposit_response = self.execute_transaction(payload=payload, verbose=verbose)
        except Exception as e:
            print("Deposit failed!")
            print(repr(e))

        return deposit_response

    def amm_withdraw(self, account, asset_1, asset_2,
                     amount=None,
                     amount2=None,
                     lp_token_in=None,
                     eprice=None,
                     mode='tfSingleAsset',
                     verbose=True):

        asset_1, asset_2 = [constants.XRP_ASSET if not isinstance(asset, dict)
                            else asset for asset in [asset_1, asset_2]]

        payload = {
            "tx_json": {
                "TransactionType": "AMMWithdraw",
                "Account": account.account_id,
                "Asset": asset_1,
                "Asset2": asset_2,
                "Amount": amount,
                "Fee": constants.DEFAULT_TRANSACTION_FEE,
                "Flags": constants.AMM_WITHDRAW_FLAGS[mode],
            },
            "secret": account.master_seed
        }

        if mode in ['tfLPToken', 'tfTwoAsset'] and amount2:
            payload['tx_json']['Amount2'] = amount2
        elif mode == 'tfLPToken':
            payload['tx_json']['Amount2'] = amount2

        elif mode in ['tfOneAssetLPToken']:
            payload['tx_json']['LPTokenIn'] = lp_token_in
        elif mode in ['tfLimitLPToken']:
            payload['tx_json']['EPrice'] = eprice
        elif mode == 'tfWithdrawAll':
            del payload['tx_json']['Amount']
        withdraw_response = self.execute_transaction(payload=payload)
        return withdraw_response

    def amm_vote(self, account, asset_1, asset_2, trading_fee=constants.DEFAULT_AMM_TRADING_FEE):

        payload = {
                "secret": account.master_seed,
                "tx_json": {
                    "TransactionType": "AMMVote",
                    "Account": account.account_id,
                    "Asset": asset_1,
                    "Asset2": asset_2,
                    "TradingFee": trading_fee,
                    "Fee": constants.DEFAULT_TRANSACTION_FEE,
                }
        }

        return self.execute_transaction(payload=payload)

    def amm_info(self, asset_1, asset_2, verbose=True):
        asset_1, asset_2 = [constants.XRP_ASSET if not isinstance(asset, dict)
                            else asset for asset in [asset_1, asset_2]]
        payload = {
            "tx_json": {
                "asset": asset_1,
                "asset2": asset_2,
                "ledger_index": "validated",
            }
        }
        try:
            amm_info = self.execute_transaction(payload=payload, method="amm_info", verbose=verbose)
            return amm_info
        except KeyError as e:
            msg = "No AMM to get info from!"
            log.error(msg)
            e.add_note(msg)

    # Methods that aren't API wrappers

    def get_amm_id(self, asset_1, asset_2, verbose=True):
        amm_info = self.amm_info(asset_1, asset_2, verbose=verbose)
        amm_id = amm_info["amm"]["account"]
        return amm_id

    def get_amm_lp_token(self, asset_1, asset_2, verbose=True):
        amm_info = self.amm_info(asset_1, asset_2, verbose=verbose)
        lp_token = amm_info['amm']['lp_token']
        return lp_token

    def get_amm_lp_token_balance(self, account_id, asset_1, asset_2, verbose=True):
        if isinstance(account_id, Account):
            account_id = account_id.account_id
        amm_info = self.amm_info(asset_1, asset_2, verbose=verbose)
        amm_id = amm_info['amm']['account']
        lines = self.get_account_lines(account_id)['lines']
        try:
            [balance] = [line['balance']
                         for line in lines
                         if (line['account'] == amm_id)
                         and (len(line['currency']) > 3)
                         ]
            # TODO: check 1st byte of amm currency if it's 0x03...
            return balance
        except ValueError:
            msg = f"{account_id} doesn't hold LP tokens!"
            log.info(msg)
            return 0

        amm_info = self.amm_info(asset_1, asset_2, verbose=verbose)
        lp_token = amm_info['amm']['lp_token']
        return lp_token

    def get_amm_vote_slots(self, asset_1, asset_2):
        amm_info = self.amm_info(asset_1, asset_2)
        vote_slots = amm_info['amm']['vote_slots']
        return vote_slots

    def get_amm_auction_price(self, asset_1, asset_2):
        amm_info = self.amm_info(asset_1, asset_2)
        return amm_info['amm']['auction_slot']['price']['value']

    def get_amm_auction_slot_holder(self, asset_1, asset_2):
        info = self.amm_info(asset_1, asset_2)
        return info['amm']['auction_slot']['account']

    def withdraw_all(self, account, asset_1, asset_2):
        return self.amm_withdraw(account, asset_1, asset_2, mode="tfWithdrawAll")


# Non-rippled AMM helpers
def amm_vote_setup_voters(server, n=8):
    account_1 = server.create_account(fund=True)
    account_2 = server.create_account(fund=True)

    xrp = constants.DEFAULT_AMM_XRP_CREATE
    usd = {
        "currency": "USD",
        "issuer": account_1.account_id,
        "value": constants.DEFAULT_AMM_TOKEN_CREATE,
    }

    accounts = [server.create_account(fund=True) for i in range(n)]
    for i in range(len(accounts)):
        server.create_trustline(accounts[i], usd)
        server.make_payment(account_1, accounts[i], usd)

    return account_1, account_2, xrp, usd, accounts


def payment(dest_account, amount=str(20_000000)):
    data = {
        "method": "submit",
        "params": [{
            "tx_json": {
                "TransactionType": "Payment",
                "Account": constants.TEST_GENESIS_ACCOUNT_ID,
                "Destination": dest_account,
                "Amount": amount,
                "Fee": 20000000,
            },
            "secret": constants.TEST_GENESIS_ACCOUNT_SEED,
        }],
    }
    return data


def setup_env(server, number_of_accounts, currency, trustline_limit=None):
    # TODO: Implement batch submission with exponential back-off to avoid rate-limiting by rippled and use for payments
    # and trustset
    url = server.address
    base_wait = 0.05
    wait_factor = 2

    def wallet_propose():
        data = {"method": "wallet_propose"}
        account = requests.post(url, json=data).json()["result"]
        return {"address": account["account_id"], "secret": account["master_seed"]}

    def trustline(account, currency):
        address, secret = account.values()
        payload = {
            "method": "submit",
            "params": [{
                "tx_json": {
                    "TransactionType": "TrustSet",
                    "Account": address,
                    "LimitAmount": currency
                },
                "secret": secret
            }],
        }
        return payload

    accounts = []
    try:
        while len(accounts) < number_of_accounts:
            account = wallet_propose()
            payload = payment(account["address"])  # TODO: pass server as a param to get server.funding_account.account_id?
            time.sleep(base_wait) # TODO: rewrite to back off like trustsets
            result = requests.post(url, json=payload).json()["result"].get("engine_result")
            if result == 'tesSUCCESS':
                accounts.append(account)
    except AttributeError as e:
        log.error("Funding account not found!")
        log.error(e)
        raise

    all_accounts_created = len(accounts) == number_of_accounts
    log.debug(f"{all_accounts_created=}")

    trustset_results = []
    try:
        while len(trustset_results) < number_of_accounts:
            for account in accounts:
                trustset = False
                wait = base_wait
                while not trustset:
                    trustset_payload = trustline(account, trustline_limit)
                    result = requests.post(url, json=trustset_payload).json()["result"]
                    time.sleep(wait)
                    try:
                        if trustset := result["engine_result"] == "tesSUCCESS":
                            trustset_results.append(result)
                        else:
                            log.info(f"{result['engine_result']=}")
                            wait *= wait_factor
                            log.info(f"Waiting longer... {wait} seconds!")
                    except KeyError as e:
                        log.error(f"No key [{e}] ins result")
                        log.error("Error:" + result["error"] + " - " + result["error_message"])
                        wait *= wait_factor
                        log.error(f"Trying again after {wait}s")
    except AssertionError as e:
        log.error(e)
        log.error("Couldn't create all accounts!")
        return False
    except Exception as e:
        log.error(repr(e))

    trustlines_set = all([response["engine_result"] == "tesSUCCESS" for response in trustset_results])
    assert trustlines_set, "Not trustlines_set!"
    log.debug(f"{len(trustset_results)=}")  # TODO: log debug
    server.wait_for_ledger_close(server.ledger_current() + 1)
