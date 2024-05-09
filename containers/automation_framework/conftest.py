import json
import os
import pathlib
import pytest
import time
import signal
import sys

from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests.rippled import RippledServer
from rippled_automation.rippled_end_to_end_scenarios.clio_tests.clio import ClioServer
from rippled_automation.rippled_end_to_end_scenarios.sidechain import sidechain_config
from rippled_automation.rippled_end_to_end_scenarios.utils import log_helper
from rippled_automation.rippled_end_to_end_scenarios.utils import helper
from rippled_automation.rippled_end_to_end_scenarios.end_to_end_tests import constants

home_dir = str(pathlib.Path.home())
repo_base_dir = os.path.dirname(os.path.realpath(__file__))
log = log_helper.get_logger()
log_dir = None
fx_rippled_info = {}
funding_accounts_info = {}


def signal_handler(sig, frame):
    pytest.exit("**** Aborting test run! ****")


signal.signal(signal.SIGINT, signal_handler)  # Abort tests when Ctrl-C is issued


def pytest_configure(config):
    global cmd_args
    cmd_args = config.option

    global log_dir
    log_dir = cmd_args.logDir

    pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)
    pathlib.Path(constants.AUTOMATION_TMP_DIR).mkdir(parents=True, exist_ok=True)

    cmd_args.multipleTestSuiteInParallel = True if cmd_args.multipleTestSuiteInParallel == "true" else False

    log_helper.setup_logging(cmd_args)
    helper.update_parallel_run_pid_file(constants.TEST_RUN_PID_TEST_RESULT_DIR_KEY, log_dir)
    log.info("****************************************************************************************************")
    log.info("Log directory: {}".format(log_dir))
    log.info("****************************************************************************************************")


def pytest_addoption(parser):
    parser.addoption("--hostname", help="rippled hostname", default="localhost")
    parser.addoption("--port", help="rippled port number", default="51234")
    parser.addoption("--clioHost", help="clio hostname", default="localhost")
    parser.addoption("--clioPort", help="clio port number", default="51233")
    parser.addoption("--clioTests", help="Run CLIO tests", default=False)
    parser.addoption("--logLevel", help="Set log level", default="INFO")
    parser.addoption("--logDir", help="Log directory",
                     default=log_helper.get_log_dir(repo_base_dir, helper.get_test_suite_name_from_parallel_run()))
    parser.addoption("--rippledRepoPath", help="Path to rippled repo", default="{}/rippled".format(home_dir))
    parser.addoption("--automationDataRepoPath", help="Path to automation data repo",
                     default="{}/automation_data".format(home_dir))
    parser.addoption("--publishStats", help="Publish stats to prometheus", default=False)
    parser.addoption('--useWebsockets', default=False, help="Use websockets instead of JSON-RPC")
    parser.addoption("--rippled", help="rippled exec", default="/opt/ripple/bin/rippled")
    parser.addoption("--rippledConfig", help="rippled config", default="/opt/ripple/etc/rippled.cfg")
    parser.addoption("--standaloneMode", help="Set to true if rippled is started in standalone mode", default=False)
    parser.addoption("--network", help="Network (devnet, altnet, mainnet)", default=constants.DEVNET_NETWORK)
    parser.addoption("--multipleTestSuiteInParallel", help="Set to true if runing multiple test suites in parallel",
                     default=False)

    parser.addoption("--sidechainConfig", help="Path to sidechain config", default=None)
    parser.addoption("--sidechainTests", help="Run sidechain tests", default=False)
    parser.addoption("--xchainBridgeCreate", help="Create new sidechain", default=False)
    parser.addoption("--feature", help="Project feature like rippled, clio, sidechain, etc",
                     default=constants.TESTRAIL_DEFAULT_PROJECT)


@pytest.hookimpl(tryfirst=True)
def pytest_keyboard_interrupt(excinfo):
    balance_transfer(all_funding_accounts_info=funding_accounts_info)


@pytest.fixture(scope="session")
def fx_rippled(request):
    sidechain = None
    witnesses = None
    feature = cmd_args.feature
    address = f"{cmd_args.hostname}:{cmd_args.port}"
    use_websockets = True if cmd_args.useWebsockets == "true" else False
    xchain_bridge_create = True if cmd_args.xchainBridgeCreate == "true" else False
    standalone_mode = True if cmd_args.standaloneMode == "true" else False
    sidechain_setup_config = sidechain_config.get_sidechain_config(standalone_mode, cmd_args.network) \
        if cmd_args.sidechainConfig is None else cmd_args.sidechainConfig

    clio_server = None
    rippled_server = None
    if cmd_args.sidechainTests == "true":
        try:
            rippled_server, sidechain, witnesses = sidechain_config.setup_sidechain(
                sidechain_setup_config=sidechain_setup_config, standalone_mode=standalone_mode,
                xchain_bridge_create=xchain_bridge_create)
        except Exception as e:
            pytest.exit("**** Failed to initialize locking chain/create funding account. Check logs for more info")

    else:
        try:
            rippled_server = RippledServer(address=address, use_websockets=use_websockets, rippled_exec=cmd_args.rippled,
                                           rippled_config=cmd_args.rippledConfig,
                                           standalone_mode=standalone_mode)
        except Exception as e:
            pytest.exit("**** Failed to initialize rippled server/create funding account. Check logs for more info")

    try:
        if cmd_args.clioTests == "true":
            feature = constants.TESTRAIL_CLIO_PROJECT
            address = f"{cmd_args.clioHost}:{cmd_args.clioPort}"
            clio_server = ClioServer(address=address, use_websockets=use_websockets, rippled=rippled_server)
    except Exception as e:
        log.error("**** Failed to initialize clio server")

    save_testrun_info(rippled_server=rippled_server, clio_server=clio_server, feature=feature)

    prometheus_handle = None
    if cmd_args.publishStats == "true":
        log.info("**** Initializing prometheus client handler...")
        from scripts.prometheus_client.custom_metric_exporter import PrometheusMetricCollector
        prometheus_handle = PrometheusMetricCollector()
        prometheus_handle.initilize_metrics_collection()

    return {
        "rippled_server": rippled_server,
        "clio_server": clio_server,
        "sidechain": sidechain,
        "witnesses": witnesses,
        "prometheus_handle": prometheus_handle,
        "rippled_repo_path": cmd_args.rippledRepoPath,
        "automation_data_repo_path": cmd_args.automationDataRepoPath,
        "log_dir": cmd_args.logDir,
    }


def save_testrun_info(rippled_server=None, clio_server=None, feature=None):
    server = rippled_server if rippled_server else clio_server

    clio_rippled_version, clio_version = server.get_clio_rippled_version(verbose=False)

    log.info("**** Server: {}".format(server.address))

    if not clio_version and clio_server:
        clio_rippled_version, clio_version = clio_server.get_clio_rippled_version(verbose=False)
    if clio_rippled_version or clio_version:
        if not clio_server:
            server.rippled_as_clio = True  # rippled hostname/port is clio server
            # TODO: Enable this if rippled tests are duplicated under testrail project: clio
            # feature = constants.TESTRAIL_CLIO_PROJECT
        log.info("**** Clio: {}, Clio rippled: {}".format(clio_version, clio_rippled_version))

    rippled_version = rippled_server.get_rippled_version(verbose=False)
    if rippled_version and cmd_args.sidechainTests != "true":
        log.info("**** rippled: {}".format(rippled_version))

    log.debug("Writing server versions into file: {}".format(constants.TESTRUN_INFO_FILE))
    rippled_json = {
        constants.KEY_NAME_RIPPLED_VERSION: rippled_version,
        constants.KEY_NAME_CLIO_RIPPLED_VERSION: clio_rippled_version,
        constants.KEY_NAME_CLIO_VERSION: clio_version,
        constants.KEY_NAME_FEATURE: feature
    }
    with open(constants.TESTRUN_INFO_FILE, "w") as fp:
        json.dump(rippled_json, fp, indent=4)
    log.info("")


@pytest.fixture(autouse=True)
def pre_and_post_test(request, fx_rippled):
    if "standaloneModeOnly" in dir(request.module) and not fx_rippled["rippled_server"].standalone_mode:
        pytest.skip("Amendment Blocked on network")
    elif "skipTestSuite" in dir(request.module):
        pytest.skip(str(request.module.__getattribute__("skipTestSuite")))

    log.info("######################################################################")
    log.info("Testname: {}".format(request.node.name))
    log.info("######################################################################")
    yield
    # anything to do after each test, add here
    fx_rippled["rippled_server"].get_server_info(verbose=False)  # DEBUG log in file

    if cmd_args.sidechainTests == "true" and request.node.rep_call.outcome == "failed":
        # Start witness servers that are stopped due to test failure
        stopped_witness_servers = fx_rippled["witnesses"].servers_stopped.copy()
        if stopped_witness_servers:
            log.info(f'**** Unexpectedly stopped witness servers: {stopped_witness_servers}')
            for witness_name in stopped_witness_servers:
                bridge_type, witness_index = fx_rippled["witnesses"].get_witness_info(witness_name)
                fx_rippled["witnesses"].witness_server_start(witness_index, bridge_type=bridge_type,
                                                             mainchain=fx_rippled["rippled_server"],
                                                             sidechain=fx_rippled["sidechain"])

        # Reset reward account balances after every failed test
        sidechain_config.reset_reward_account_balances([fx_rippled["rippled_server"], fx_rippled["sidechain"]])


@pytest.fixture(scope='session', autouse=True)
def pre_and_post_session(fx_rippled):
    global fx_rippled_info
    fx_rippled_info = fx_rippled
    for rippled_server in [fx_rippled["rippled_server"], fx_rippled["sidechain"]]:
        if rippled_server:
            if rippled_server.funding_account:
                funding_accounts_info[rippled_server] = rippled_server.funding_account
            else:
                log.error(f"{rippled_server.name}: Funding account not created")
                sys.exit(1)

    if cmd_args.clioTests == "true" and fx_rippled["clio_server"] is None:
        pytest.exit("**** Failed to initialize clio server. Check logs for more info")

    yield
    if cmd_args.publishStats == "true":
        log.info("Wait 20 seconds for prometheus to scrape the last metric before exiting this module (and web server)")
        time.sleep(20)

    log.info("****************************************************************************************************")
    log.info("Log directory: {}".format(log_dir))
    log.info("****************************************************************************************************")


def balance_transfer(all_funding_accounts_info):
    if all_funding_accounts_info:
        log.info("")
        log.info(f"Transfer unused XRP to test genesis account: {constants.TEST_GENESIS_ACCOUNT_ID}...")
        for rippled_server, funding_account in all_funding_accounts_info.items():
            available_bal = rippled_server.get_account_balance(funding_account.account_id, verbose=False)
            bal_to_tranfer = int(available_bal) - int(constants.BASE_RESERVE) - int(constants.OWNER_RESERVE)
            log.info(f"  -> {rippled_server.name} ({funding_account}): {bal_to_tranfer}")
            rippled_server.make_payment(source=funding_account, dest=constants.TEST_GENESIS_ACCOUNT_ID,
                                        amount=str(bal_to_tranfer), verbose=False)
            log.info(
                f'  Updated balance: {rippled_server.get_account_balance(constants.TEST_GENESIS_ACCOUNT_ID, verbose=False)}')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        log.info("")
        log.info("**** Test Status: {} ****\n".format(rep.outcome))
        setattr(item, "rep_" + rep.when, rep)


# Teardown
def pytest_unconfigure():
    balance_transfer(all_funding_accounts_info=funding_accounts_info)
