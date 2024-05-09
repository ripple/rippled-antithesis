from ..end_to_end_tests.rippled import RippledServer
from ..end_to_end_tests import constants
from ..utils import log_helper

log = log_helper.get_logger()


class ClioServer(RippledServer):
    def __init__(self, address, use_websockets, rippled):
        super().__init__(address=address, use_websockets=use_websockets, server_name=constants.CLIO_SERVER_NAME,
                         server_type=constants.SERVER_TYPE_CLIO)
        self.rippled = rippled  # reference to rippled handle (for account balance verification, etc)

    def compare_responses(self, response, response_1, response_2, key):
        match_found = False
        for value in response[key]:
            if value in response_1[key]:
                log.debug(f"{value} found in response_1")
                match_found = True
            elif value in response_2[key]:
                log.debug(f"{value} found in response_2")
                match_found = True
            else:
                log.debug(f"{value} not found")
                return False
        if match_found:
            return True

        log.debug(f"{key} has empty value in response: {response}")
        return False
