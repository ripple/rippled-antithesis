import logging

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants


class Account:
    xrp_balance = {}
    last_recorded_account_sequence = {}

    def __init__(self, wallet, rippled=None):
        self._account_id = wallet['account_id']
        self._key_type = wallet['key_type']
        self._master_key = wallet['master_key']
        self._master_seed = wallet['master_seed']
        self._master_seed_hex = wallet['master_seed_hex']
        self._public_key = wallet['public_key']
        self._public_key_hex = wallet['public_key_hex']
        self._regular_key_seed = None
        self._regular_key_account = None
        self._signer = dict()
        self._signer_account = None
        self._signer_seed = None

        if rippled not in Account.xrp_balance:
            Account.xrp_balance[rippled] = {}
        if rippled not in Account.last_recorded_account_sequence:
            Account.last_recorded_account_sequence[rippled] = {}
        if self._account_id not in Account.xrp_balance[rippled]:
            Account.xrp_balance[rippled][self._account_id] = int(constants.NON_FUNDED_ACCOUNT_BALANCE)

        Account.last_recorded_account_sequence[rippled][self._account_id] = None

    @property
    def wallet(self):
        return {
            'account_id': self._account_id,
            'key_type': self._key_type,
            'master_key': self._master_key,
            'master_seed': self._master_seed,
            'master_seed_hex': self._master_seed_hex,
            'public_key': self._public_key,
            'public_key_hex': self._public_key_hex
        }

    def __repr__(self):
        return f'Account("{self._account_id}", "{self._master_seed}")'

    def __str__(self):
        return str(self.account_id)

    @property
    def master_seed(self):
        return self._master_seed

    @property
    def regular_key_seed(self):
        return self._regular_key_seed

    @property
    def account_id(self):
        return self._account_id

    @property
    def key_type(self):
        return self._key_type

    @property
    def master_key(self):
        return self._master_key

    @property
    def master_seed_hex(self):
        return self._master_seed_hex

    @property
    def public_key(self):
        return self._public_key

    @property
    def public_key_hex(self):
        return self._public_key_hex

    def regular_key(self, seed, account):
        self._regular_key_seed = seed
        self._regular_key_account = account

    def set_signers_list(self, seed, account, weight=2):
        self._signer_account = account
        self._signer_seed = seed
        # self._signer[seed]: [account, weight]
