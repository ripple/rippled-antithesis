import pytest

from ..utils import log_helper
from ..utils import test_validator

log = log_helper.get_logger()


def test_nfts_by_issuer(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_malformed_issuer(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
            "issuer": "rfhdZze9fg61avJ52CX1SAvyvW9683ZXT"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, method="nfts_by_issuer", response_result="actMalformed")


def test_nfts_by_issuer_without_issuer(fx_rippled):
    clio_server = fx_rippled["clio_server"]

    payload = {
        "tx_json": {
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, method="nfts_by_issuer", response_result="invalidParams")


def test_nfts_by_issuer_with_nft_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "nft_taxon": 0
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_invalid_nft_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "nft_taxon": 2
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice])

    assert not clio_response["nfts"], "nfts found: {}".format(clio_response)


def test_nfts_by_issuer_with_malformed_nft_taxon(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "nft_taxon": "dfgh"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="invalidParams")


def test_nfts_by_issuer_with_valid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    tx_response = rippled_server.tx(tx_id=rpc_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[alice])

    clio_response = clio_server.get_ledger(ledger_index=tx_response["ledger_index"])
    test_validator.verify_test(clio_server, clio_response, method="ledger", accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_hash": clio_response["ledger_hash"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_invalid_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_hash": "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA78"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="lgrNotFound")


def test_nfts_by_issuer_with_malformed_ledger_hash(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_hash": "D638208ADBD04CBB10DE7B645D3AB4BA31489379411A3A347151702B6401AA7"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="invalidParams")


def test_nfts_by_issuer_with_valid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    tx_response = rippled_server.tx(tx_id=rpc_response["tx_json"]["hash"])
    test_validator.verify_test(rippled_server, tx_response, method="tx", accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_index": tx_response["ledger_index"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_invalid_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_index": clio_server.get_ledger_index_min()
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="actNotFound")


def test_nfts_by_issuer_with_malformed_ledger_index(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "TransactionType": "NFTokenMint",
            "Account": alice.account_id,
            "NFTokenTaxon": 0
        },
        "secret": alice.master_seed
    }
    rpc_response = rippled_server.execute_transaction(payload=payload)
    test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "ledger_index": "dfgh"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], response_result="invalidParams")


def test_nfts_by_issuer_with_limit_and_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    for i in range(20):
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenMint",
                "Account": alice.account_id,
                "NFTokenTaxon": 0
            },
            "secret": alice.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 10
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 10,
            "marker": clio_response["marker"]
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_more_than_20_NFTs(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    for i in range(25):
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenMint",
                "Account": alice.account_id,
                "NFTokenTaxon": 0
            },
            "secret": alice.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_malformed_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": "ghjgh"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer",
                               response_result="invalidParams")


def test_nfts_by_issuer_with_zero_limit(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 0
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer",
                               response_result="invalidParams")


def test_nfts_by_issuer_with_limit_and_invalid_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    for i in range(20):
        payload = {
            "tx_json": {
                "TransactionType": "NFTokenMint",
                "Account": alice.account_id,
                "NFTokenTaxon": 0
            },
            "secret": alice.master_seed
        }
        rpc_response = rippled_server.execute_transaction(payload=payload)
        test_validator.verify_test(rippled_server, rpc_response, accounts=[alice])

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 10
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 10,
            "marker": "000000004280875B1B0435334FCA9CC68152860A5DF34BEBABC033520015C2B7"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer")


def test_nfts_by_issuer_with_limit_and_malformed_marker(fx_rippled):
    rippled_server = fx_rippled["rippled_server"]
    clio_server = fx_rippled["clio_server"]

    alice = rippled_server.create_account(fund=True)

    payload = {
        "tx_json": {
            "issuer": alice.account_id,
            "limit": 10,
            "marker": "malformed marker"
        }
    }
    clio_response = clio_server.execute_transaction(payload=payload, method="nfts_by_issuer", verbose=True)
    test_validator.verify_test(clio_server, clio_response, accounts=[alice], method="nfts_by_issuer",
                               response_result="invalidParams")
