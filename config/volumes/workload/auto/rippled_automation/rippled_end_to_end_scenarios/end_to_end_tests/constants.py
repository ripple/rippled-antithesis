MASTER_ACCOUNT_ID = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
MASTER_ACCOUNT_SEED = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
# This is a "test genesis account" used as the source funding account for all tests
# This "test genesis account" is funded with 1 billion XRP from account:
# "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"/"sn6Unf8nSvQZvJsv2RBx3mARbJMAv"
TEST_GENESIS_ACCOUNT_ID = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
TEST_GENESIS_ACCOUNT_SEED = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
RUNTIME_FUNDING_ACCOUNT_MAX_BALANCE = "100000000000"  # 100K XRP
DEVNET_NETWORK = "devnet"
AUTOMATION_TMP_DIR = "/tmp/automation_work_dir"
TESTRUN_INFO_FILE = f"{AUTOMATION_TMP_DIR}/testrun_info.json"
BASE_RESERVE = "10000000"  # Update if this value changes
OWNER_RESERVE = "2000000"  # Update if this value changes
DEFAULT_TRANSACTION_FEE = "20"  # Update if this value changes
DEFAULT_DELETE_ACCOUNT_FEE = OWNER_RESERVE  # same as Owner Reserve
MAX_LIMIT_NETWORK_ID_NOT_REQUIRED = 1024
KEY_TYPE_SECP256K1 = "secp256k1"
KEY_TYPE_ED25519 = "ed25519"
DEFAULT_ACCOUNT_KEY_TYPE = KEY_TYPE_SECP256K1
DEFAULT_ACCOUNT_BALANCE = "40000000"
RIPPLE_EPOCH = 946684800
NON_FUNDED_ACCOUNT_BALANCE = "0"
DEFAULT_DELETE_SETTLE_DELAY = 80
DEFAULT_TRANSFER_AMOUNT = "10000"
DEFAULT_CHECK_MAX_SEND = "30000000"
MAX_ACCOUNT_OBJECTS_LIMIT = 400
MAX_SIGNER_ENTRIES = 32  # https://xrpl.org/signerlistset.html#signerlistset
MAX_NFTOKEN_PAGE_OBJECTS_LIMIT = 32
NFTOKEN_CREATE_OFFER_SELL_TOKEN = 1  # tfSellToken
DEFAULT_MAX_SIGNER_WEIGHT = 65535
DEFAULT_PAYCHAN_SETTLE_DELAY = 20
DEFAULT_PAYCHAN_EXPIRATION = 30
DEFAULT_PAYCHAN_CANCEL_AFTER = 20
TESTRAIL_DEFAULT_PROJECT = "rippled"
TESTRAIL_CLIO_PROJECT = "clio"
KEY_NAME_RIPPLED_VERSION = "rippled_version"
KEY_NAME_CLIO_RIPPLED_VERSION = "clio_rippled_version"
KEY_NAME_CLIO_VERSION = "clio_version"
KEY_NAME_FEATURE = "feature"
RIPPLED_STOP_METHOD = "stop"
RIPPLED_SERVER_NAME = "rippled"
CLIO_SERVER_NAME = "clio"
FLAGS_DEPOSIT_AUTH_ENABLED = 16777216
SERVER_TYPE_CLIO = "clio"
SERVER_TYPE_RIPPLED = "rippled"
SERVER_TYPE_WITNESS = "witness"
XRP_ASSET = {"currency": "XRP"}
MAX_STREAM_TIMEOUT = 60
TEST_RUN_PID_TEST_SUITE_KEY = "test_suite"
TEST_RUN_PID_TEST_RESULT_DIR_KEY = "results_dir"
MAX_ACCOUNT_COUNT_FOR_PRICE_ORACLE_AGGREGATE = 200

# Sidechain specific
MAINCHAIN_NAME = "locking_chain"  # mainchain
SIDECHAIN_NAME = "issuing_chain"  # sidechain
WITNESS_CONFIG_MAINCHAIN_NAME = "LockingChain"  # mainchain
WITNESS_CONFIG_SIDECHAIN_NAME = "IssuingChain"  # sidechain
SIDECHAIN_IGNORE_VALIDATION = {"auto-submitted": True}
SIDECHAIN_BRIDGE_CURRENCY_XRP = XRP_ASSET
SIDECHAIN_BRIDGE_TYPE_XRP = "XRP"
SIDECHAIN_BRIDGE_TYPE_IOU = "IOU"
SIDECHAIN_INITIAL_ACCOUNT_CLAIM_COUNT = 0
SIDECHAIN_STANDALONE_CONFIG = "configs/rippled/sidechain/standalone/config.json"
SIDECHAIN_NETWORK_CONFIG = {
    DEVNET_NETWORK: "configs/rippled/sidechain/{}/config.json".format(DEVNET_NETWORK)
}
# master account to fund test accounts on issuing chain
ISSUING_CHAIN_MASTER_ACCOUNT_ID = "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh"
ISSUING_CHAIN_MASTER_ACCOUNT_MASTER_SEED = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
# INFO: LockingChainIssue.issuer "rnH6LV9V5Gv2xPNvXSmNNXWtRrf5rXunVV" in IOU witness config files
LOCKING_CHAIN_IOU_ISSUER_SEED = "sniYJ8tygdMR9UDYqrgDcHQEpRowJ"  # for LockingChainIssue.issuer
MAX_NO_OF_ACCOUNTS_FOR_A_TEST_RUN = 500  # to fund master accounts to source all accounts in the test run
SKIP_TEST_FOR_SOURCE_CHAIN = None  # None for run all, or SIDECHAIN_NAME or MAINCHAIN_NAME
SIDECHAIN_SUBMIT_ADD_ATTESTATION = False  # default mode: manual submit
SIDECHAIN_WITNESS_QUORUM = 0.8  # 80%
SIGNATURE_REWARDS = {
    MAINCHAIN_NAME: 204,  # drops
    SIDECHAIN_NAME: 304  # drops
}

IGNORE_FEE_INCUR_FOR = [
    "sign",
    "sign_for",
    "transaction_entry",
    "tx",
    -252,  # temARRAY_TOO_LARGE
    -253,  # temARRAY_EMPTY
    -296,  # temBAD_EXPIRATION
    -298,  # temBAD_AMOUNT
    -295,  # temBAD_FEE
    -299,  # temMALFORMED
    -394,  # telINSUF_FEE_P
    -279,  # temDST_IS_SRC
    -92,  # terPRE_SEQ
    -181,  # tefTOO_BIG
    -266,  # temINVALID_COUNT
    -190,  # tefPAST_SEQ
    -92,  # terPRE_SEQ
    -180,  # tefNO_TICKET
    -263,  # temSEQ_AND_TICKET
    -88,  # terPRE_TICKET
    -275,  # temREDUNDANT
    -292,  # temBAD_OFFER
    -283,  # temBAD_SEQUENCE
    -276,  # temINVALID_FLAG
    -293,  # temBAD_LIMIT
    -285,  # temBAD_SEND_XRP_PARTIAL
    -262,  # temBAD_TRANSFER_FEE
    -179,  # tefTOKEN_IS_NOT_TRANSFERABLE
    -282,  # temBAD_SIGNATURE
    -272,  # temBAD_SIGNER
    -270,  # temBAD_WEIGHT
    -271,  # temBAD_QUORUM
    -186,  # tefBAD_SIGNATURE
    -184,  # tefNOT_MULTI_SIGNING
    -267,  # temCANNOT_PREAUTH_SELF
    -259,  # temXCHAIN_BAD_PROOF
    -255,  # temXCHAIN_BRIDGE_BAD_REWARD_AMOUNT
    -94,  # terNO_LINE
    -294,  # temBAD_ISSUER
    -96,  # terNO_ACCOUNT
    -254,  # temEMPTY_DID
]

transactions = {
    "CREATING_OBJECTS": [
        "OracleSet",
        "EscrowCreate",
        "CheckCreate",
        "PaymentChannelCreate",
        "PaymentChannelClaim",
        "PaymentChannelFund",
        "OfferCreate",
        "TicketCreate",
        "SignerListSet",
        "TrustSet",
        "NFTokenMint",
        "NFTokenCreateOffer",
        "NFTokenAcceptOffer",
        "DepositPreauth",
        "XChainCreateBridge",
        "XChainModifyBridge",
        "XChainCreateClaimID",
        "AMMCreate",
        "DIDSet",
    ],
    "CLEARING_OBJECTS": [
        "OracleDelete",
        "EscrowCancel",
        "EscrowFinish",
        "AccountDelete",
        "CheckCash",
        "CheckCancel",
        "OfferCancel",
        "NFTokenBurn",
        "NFTokenCancelOffer",
        "XChainClaim",
        "AMMDelete",
        "DIDDelete",
    ],
    "NOT_CREATING_OBJECTS": [
        "Payment",
        "AccountSet",
        "SetRegularKey",
        "XChainCommit",
        "XChainAddClaimAttestation",
        "XChainAddAccountCreateAttestation",
        "XChainAccountCreateCommit",
        "AMMInfo",
        "AMMDeposit",
        "AMMWithdraw",
        "AMMBid",
        "AMMVote",
        "Clawback",
    ],
}

PAY_CHANNEL_TRANSACTIONS = [
    "PaymentChannelCreate",
    "PaymentChannelClaim",
    "PaymentChannelFund"
]

OFFER_CREATE_OBJECTS = [
    "RippleState",
    "Offer"
]

OFFER_CROSSING_FLAGS = [
    131072,  # tfImmediateOrCancel
    262144,  # tfFillOrKill
]

XRP_DEBIT = "XRP drops (debit)"
XRP_CREDIT = "XRP drops (credit)"

EXECUTE_TRANSACTION_AFTER = "Execute Transaction After"
EXECUTE_TRANSACTION_BEFORE = "Execute Transaction Before"
EXECUTE_TRANSACTION_NOW = "Execute Transaction Now"

DEFAULT_ESCROW_FINISH_AFTER = 15
DEFAULT_ESCROW_CANCEL_AFTER = 40
DEFAULT_NFTOKEN_EXPIRATION = 20
DEFAULT_CHECK_EXPIRATION_IN_SECONDS = 20
DEFAULT_OFFER_EXPIRATION_IN_SECONDS = 20

DEPOSIT_PREAUTHORIZE = "Authorize"
DEPOSIT_UNAUTHORIZE = "Unauthorize"

OFFER_MODE_CREATE = "Offer Create"
OFFER_MODE_CLAIM = "Offer Claim"

METHODS_NOT_IMPLEMENTED_IN_CLIO = [
    "validation_create",
    "wallet_propose",
    "can_delete",
    "crawl_shards",
    "download_shard",
    "node_to_shard",
    "sign",
    "sign_for",
    "connect",
    "peer_reservations_list",
    "consensus_info",
    "feature",
    "fetch_info",
    "get_counts",
    "validator_list_sites",
    "validators",
    "peer_reservations_add",
    "tx_history",
    "deposit_authorized",
    "server_state",
    "peer_reservations_del"
]

CLIO_IGNORES = [
    "type",
    "request",
    "warnings",
    "ledger_hash",
    "ledger_index",
    "limit",
    "validated",
    "error_code",
    "error_message",
    "ledger_current_index",
    "marker",
    "forwarded",
    "ledger_index_min",
    "ledger_index_max",
    "account",
    "hash",
    "accepted",
    "ctid",
    "inLedger",
    "expected_ledger_size",
    "max_queue_size",
    "current_ledger_size"
]

STREAM_PARAMS = {
    "ledgerClosed": ["type", "fee_base", "fee_ref", "ledger_hash", "ledger_index", "ledger_time", "reserve_base",
                     "reserve_inc", "txn_count", "validated_ledgers"],
    "transaction_proposed": ["engine_result", "engine_result_code", "engine_result_message", "ledger_current_index",
                             "status", "type", "validated", "transaction", "tx_json", "hash"],
    "transaction": ["close_time_iso", "status", "type", "engine_result", "engine_result_code", "engine_result_message", "ledger_hash",
                    "ledger_index", "meta", "validated", "transaction", "tx_json", "hash"],
    "consensusPhase": ["type", "consensus"],
    "serverStatus": ["base_fee", "load_base", "load_factor", "load_factor_fee_escalation", "load_factor_fee_queue",
                     "load_factor_fee_reference", "load_factor_server", "server_status", "type"],
    "validationReceived": ["type", "amendments", "base_fee", "cookie", "flags", "full", "ledger_hash", "ledger_index",
                           "load_fee", "master_key", "reserve_base", "reserve_inc", "server_version", "signature",
                           "signing_time", "validated_hash", "validation_public_key", "data"],
    "peerStatusChange": ["action", "date", "ledger_hash", "ledger_index", "ledger_index_max", "ledger_index_min", "type"],
    "bookChanges": ["changes", "ledger_hash", "ledger_index", "ledger_time", "type"]
}

DID_PARAMS = ["Data", "URI", "DIDDocument"]
PRICE_ORACLE_ACCOUNT_OBJECT_PARAMS = [
    "AssetClass",
    "LastUpdateTime",
    "Provider",
    "URI",
]

DEFAULT_AMM_XRP_CREATE = "10000000"
DEFAULT_AMM_XRP_DEPOSIT = "5000000"
DEFAULT_AMM_XRP_WITHDRAWAL = "5000000"
DEFAULT_AMM_TOKEN_CREATE = "10"
DEFAULT_AMM_TOKEN_DEPOSIT = "5"
DEFAULT_AMM_TOKEN_WITHDRAWAL = "5"
DEFAULT_AMM_TOKEN_TRANSFER = "5"
DEFAULT_AMM_LP_TOKEN_WITHDRAWAL = "5000"
DEFAULT_AMM_BID = "5"
DEFAULT_AMM_CREATE_FEE = OWNER_RESERVE
DEFAULT_AMM_TRADING_FEE = "0"
MAX_AMM_TRADING_FEE = "1000"
AMM_TRADE_FEES = ["0", "1", "500", "1000"]
AMM_FLAGS = {
    "tfLPToken": "65536",
    "tfSingleAsset": "524288",
    "tfTwoAsset": "1048576",
    "tfOneAssetLPToken": "2097152",
    "tfLimitLPToken": "4194304",
    "tfTwoAssetIfEmpty": "8388608",
}

AMM_DEPOSIT_FLAGS = AMM_FLAGS

AMM_WITHDRAW_FLAGS = {
    **AMM_FLAGS,
    "tfOneAssetWithdrawAll": "262144",
    "tfWithdrawAll": "131072"
}

# Rippled error codes
ERROR_CODE_noCurrent = 16  # Current ledger is unavailable
ERROR_CODE_noNetwork = 17  # Not synced to the network

# AccountRoot flags
FLAGS_CHECKS_asfDisallowIncomingCheck = 13
FLAGS_DEFAULT_RIPPLE_asfDefaultRipple = 8
FLAGS_DEPOSIT_AUTH_asfDepositAuth = 9
FLAGS_NO_FREEZE_asfNoFreeze = 6
FLAGS_GLOBAL_FREEZE_asfGlobalFreeze = 7
FLAGS_NFT_asfDisallowIncomingNFTOffer = 12
FLAGS_PAYCHAN_asfDisallowIncomingPayChan = 14
FLAGS_TRUSTLINE_asfDisallowIncomingTrustline = 15
FLAGS_ALLOW_CLAWBACK_asfAllowTrustLineClawback = 16

# TrustSet flags
FLAGS_SET_FREEZE_tfSetFreeze = 1048576
FLAGS_CLEAR_FREEZE_tfClearFreeze = 2097152
FLAGS_SET_NORIPPLE_tfSetNoRipple = 131072
FLAGS_CLEAR_NORIPPLE_tfClearNoRipple = 262144

# Payment flags
# All the flags above prefixed with "FLAGS" is redudant. Should also probably by enums so they can be looked up both ways
PAYMENT_FLAG = {
    "tfLimitQuality": 262144,  # TODO: implement test using this flag
    "tfNoDirectRipple": 65536,  # TODO: implement test using this flag
    "tfPartialPayment": 131072,
}
