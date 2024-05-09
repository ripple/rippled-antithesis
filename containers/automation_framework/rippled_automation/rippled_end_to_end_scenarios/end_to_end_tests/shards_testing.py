#!/usr/bin/env python
import os
import sys
import time
import json

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(path)
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer as RippledTest


def test_set_public_key_value_true(hostname="localhost"):
    # Waiting for the cache to expire so we get fresh results
    time.sleep(120)

    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        public_key="true",
                                                        limit=0)
    assert (crawled_shards['status'] == 'success')
    assert (crawled_shards['public_key'] == rippled_server.get_server_info()['info']['pubkey_node'])

    for x in range(crawled_shards['peers'].__len__()):
        assert (crawled_shards.get('peers')[x].__len__() == 3)
        assert (crawled_shards.get('peers')[x]["complete_shards"] is not "")
        assert (crawled_shards.get('peers')[00]['ip'] is not "")
        assert (crawled_shards.get('peers')[00]['pwd'] is not "")


def test_set_public_key_value_false(hostname="localhost"):
    # Waiting for the cache to expire so we get fresh results
    time.sleep(120)

    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        limit=0)
    assert (crawled_shards['status'] == 'success')

    for x in range(crawled_shards['peers'].__len__()):
        assert (crawled_shards.get('peers')[x].__len__() == 2)
        assert (crawled_shards.get('peers')[x]["complete_shards"] is not "")
        assert (crawled_shards.get('peers')[00]['ip'] is not "")


def test_hop_limit_value(hostname="localhost"):
    # Waiting for the cache to expire so we get fresh results
    time.sleep(180)
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)

    # Hop Limit of 0
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        limit=0)
    assert (crawled_shards['status'] == 'success')
    # Count how many shards results are there with limit 0
    number_peers_level_0 = crawled_shards['peers'].__len__()
    print(number_peers_level_0)

    # Waiting for the cache to expire so we get fresh results
    time.sleep(180)
    # Hop Limit of 1
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        limit=1)
    assert (crawled_shards['status'] == 'success')
    number_peers_level_1 = crawled_shards['peers'].__len__()
    print(number_peers_level_1)
    assert (number_peers_level_0 <= number_peers_level_1)

    # Waiting for the cache to expire so we get fresh results
    time.sleep(180)
    # Hop Limit of 2
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        limit=2)
    assert (crawled_shards['status'] == 'success')
    number_peers_level_2 = crawled_shards['peers'].__len__()
    print(number_peers_level_2)
    assert (number_peers_level_1 <= number_peers_level_2)

    # Waiting for the cache to expire so we get fresh results
    time.sleep(180)
    # Hop Limit of 3
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        limit=3)
    number_peers_level_3 = crawled_shards['peers'].__len__()
    print(number_peers_level_3)
    assert (crawled_shards['status'] == 'success')
    assert (number_peers_level_2 <= number_peers_level_3)


def test_verify_completed_shards(hostname="localhost"):
    # Waiting for the cache to expire so we get fresh results
    time.sleep(120)

    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        public_key="true",
                                                        limit=0)
    assert (crawled_shards['status'] == 'success')
    assert (crawled_shards['complete_shards'] == '1176,1888')


def test_verify_downloading_one_shard(hostname="localhost"):
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="download_shard",
                                                        shards=[{
                                                            "index": 1,
                                                            "url": "https://dl.dropboxusercontent.com/s/qeekdx2bfufxsd3/5.tar.lz4"}])
    assert (crawled_shards['message'] == 'Downloading shard 1')
    assert (crawled_shards['status'] == 'success')


def test_verify_downloading_multiple_shards(hostname="localhost"):
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="crawl_shards",
                                                        public_key="true",
                                                        limit=0)
    # Setup a connection to the rippled_regular server
    host = "http://" + str(hostname) + ":51234/"
    rippled_server = RippledTest(host)
    crawled_shards = rippled_server.execute_transaction(method="download_shard",
                                                        shards=[
                                                            {"index": 1,
                                                             "url": "https://dl.dropboxusercontent.com/s/qeekdx2bfufxsd3/5.tar.lz4"},
                                                            {"index": 2,
                                                             "url": "https://dl.dropboxusercontent.com/s/qeekdx2bfufxsd3/5.tar.lz4"},
                                                            {"index": 3,
                                                             "url": "https://dl.dropboxusercontent.com/s/qeekdx2bfufxsd3/5.tar.lz4"},
                                                            {"index": 4,
                                                             "url": "https://dl.dropboxusercontent.com/s/qeekdx2bfufxsd3/5.tar.lz4"}])
    assert (crawled_shards['message'] == 'Downloading shard 1-4')
    assert (crawled_shards['status'] == 'success')


if __name__ == "__main__":
    # test_set_public_key_value_true(hostname="localhost")
    # test_set_public_key_value_false(hostname="localhost")
    # test_hop_limit_value(hostname="localhost")
    # test_verify_completed_shards(hostname="localhost")
    # test_verify_downloading_one_shard(hostname="localhost")
    test_verify_downloading_multiple_shards(hostname="localhost")
    print("Test passed")
