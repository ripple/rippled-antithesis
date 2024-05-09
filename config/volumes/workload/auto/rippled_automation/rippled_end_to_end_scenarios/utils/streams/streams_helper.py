from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants
from rippled_automation.rippled_end_to_end_scenarios.utils import helper, log_helper

log = log_helper.get_logger()


def compare_rippled_and_clio_responses(rippled_response, clio_response):
    for value in range(len(rippled_response)):
        assert helper.compare_dict(rippled_response[value], clio_response[value],
                                   ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"
    for value in range(len(clio_response)):
        assert helper.compare_dict(clio_response[value], rippled_response[value],
                                   ignore=constants.CLIO_IGNORES), "clio response differs from rippled response"


def find_a_txn_in_txns_list(account_id, response):
    for txn in response:
        if "transaction" in txn:
            try:
                if txn["transaction"]["Account"] == account_id and txn["status"] != "proposed":
                    return txn
            except KeyError as e:
                log.debug(e)
    return None


def find_a_book_change_in_book_changes_list(account_id, response):
    for book_change in response:
        if "changes" in book_change and book_change["changes"]:
            try:
                if book_change["changes"][0]["currency_b"].split('/')[0] == account_id:
                    return True
            except KeyError as e:
                log.debug(e)
    else:
        return False
