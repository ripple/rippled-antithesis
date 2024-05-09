from datetime import datetime
import json
import os
import subprocess
from subprocess import check_output
from subprocess import CalledProcessError
import time
from . import log_helper
from ..end_to_end_tests import constants

log = log_helper.get_logger()


def compare_dict(d1, d2, ignore):
    ignore = set(ignore)
    for k in d1:
        if k in ignore:
            log.debug("ignored value " + k)
            continue
        try:
            log.debug("Comparing " + str(k) + "\n" + str(d1[k]) + "\n" + str(d2[k]))
            if d1[k] != d2[k]:
                log.debug("'{}':'{}' does not match with '{}': '{} ".format(k, d1[k], k, d2[k]))
                return False
        except KeyError as missing_key:
            log.error(f"{missing_key} key not found in d2")
            return False
    for k in d2:
        if k in ignore:
            log.debug("ignored value " + k)
            continue
        try:
            log.debug("Comparing " + str(k) + "\n" + str(d1[k]) + "\n" + str(d2[k]))
            if d1[k] != d2[k]:
                log.debug("'{}':'{}' does not match with '{}': '{} ".format(k, d1[k], k, d2[k]))
                return False
        except KeyError as missing_key:
            log.error(f"{missing_key} key not found in d1")
            return False
    return True


def is_number(value):
    """
    Verify if 'value' is a number (int, float or a number passed as string)
    return: True if number, else false
    """
    is_value_str = isinstance(value, str)
    if is_value_str:
        for ch in value:
            if ch.isalpha() and ch != ".":
                log.debug("'{}' is not a number".format(value))
                return False

        log.debug("'{}' is a number in string format".format(value))
        return True
    else:
        log.debug("'{}' is a number".format(value))
        return True


def get_config_value(config_file="/opt/ripple/etc/rippled.cfg", section=None, key=None):
    """
    Return the value for a given key from a config file
    @param config_file: config file (default: /opt/ripple/etc/rippled.cfg)
    @param section: section to parse (example: "port_peer")
    @param key: key for which value is to be found (example: "ip")
    return: value if found, else None
    """
    log.debug("Get value from config file...")

    section_str = "[{}]".format(section)
    key_str = "{}=".format(key)
    value = None
    section_found = False

    if os.path.isfile(config_file) and section and key:
        with open(config_file, "r") as fp:
            lines = fp.readlines()

        for line in lines:
            line = line.replace(' ', '').strip('\n')
            if line.startswith('['):
                log.debug("Analyzing section: {}...".format(line))
                section_found = False
                if line == section_str:
                    log.debug("  Section '{}' found".format(section))
                    section_found = True

            if section_found and line.startswith(key_str):
                log.debug("  Key '{}' found".format(key))
                value = line.split('=')[1]
                log.debug("  value: {}".format(value))
                break

    return value


def string_to_hex(str):
    hex_value = None
    if str:
        hex_value = str.encode('utf-8').hex()
        log.debug("64bit hex: {}".format(hex_value))
    return hex_value


def hex_to_string(hex):
    str_value = None
    if str:
        str_value = bytes.fromhex(hex).decode('utf-8')
        log.debug("String value: {}".format(str_value))
    return str_value


def get_test_suite_name_from_parallel_run():
    pid_file = os.path.join(constants.AUTOMATION_TMP_DIR, str(os.getpid()))
    if os.path.isfile(pid_file):
        with open(pid_file, "r") as fp:
            for line in fp.readlines():
                if constants.TEST_RUN_PID_TEST_SUITE_KEY in line:
                    full_test_suite = line.split('=')[1]
                    return full_test_suite.split('/')[-1].split('.')[0]  # Example: payment_test.py
    return None


def update_parallel_run_pid_file(key, value):
    pid_file = os.path.join(constants.AUTOMATION_TMP_DIR, str(os.getpid()))
    if os.path.isfile(pid_file):
        with open(pid_file, "a") as fp:
            fp.write(f"{key}={value}\n")


def run_external_command(cmd, timeout=60, wait=True, output_dir="/tmp", skip_logging=False):
    cmd_to_run = cmd.split(' ')
    log.debug("Command to run: {}".format(cmd_to_run))

    if skip_logging:
        stdout = subprocess.PIPE
    else:
        time_stamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        cmd_exec = cmd.split()[0].rsplit('/', 1)[-1]
        output_file = "{}/{}_{}.log".format(output_dir, cmd_exec, time_stamp)
        log.debug("Output file: {}".format(output_file))
        stdout = open(output_file, "w")
    process = subprocess.Popen(cmd_to_run, stdout=stdout, stderr=subprocess.STDOUT, close_fds=True,
                               universal_newlines=True)
    output = None
    if wait:
        try:
            output, errors = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            process.kill()
            output, errors = process.communicate()

        log.debug("stdout:\n{}".format(output))
        log.debug("stderr:{}".format(errors))

    exit_code = process.returncode
    log.debug("Command exit status: {}".format(exit_code))
    if exit_code == 0:
        return True, output
    return False, output


def is_process_running(cmd):
    log.debug("Is process running?")
    cmd_to_run = ["pgrep", "-f", cmd]
    try:
        output = check_output(cmd_to_run)
        log.debug("PID: {}".format(output))
        if output:
            return output
    except CalledProcessError as e:
        pass

    return None


def wait_for_server_stop(rippled_exec, config, cmd=None):
    if not cmd:
        cmd = "{} --conf {}".format(rippled_exec, config)
    max_timeout = 180  # max wait to stop server completely
    start_time = time.time()
    end_time = start_time + max_timeout
    while time.time() <= end_time and is_process_running(cmd):
        log.debug("Check if server is stopped completely...")
        log.debug("Try after 1 second...")
        time.sleep(1)

    if is_process_running(cmd) is None:
        return True

    return False


def wait_for_rippled_start(rippled_exec, config, cmd=None):
    if not cmd:
        cmd = "{} --conf {} --silent server_info".format(rippled_exec, config)
    server_proposing = False
    max_timeout = 1200  # max wait rippled to sync
    start_time = time.time()
    end_time = start_time + max_timeout
    wait_time = 5  # seconds to wait before retry
    while time.time() <= end_time and not server_proposing:
        status, output = run_external_command(cmd)
        log.debug("server_info response: {}".format(output))
        server_info = json.loads(output)

        if "result" in server_info:
            server_state = server_info["result"]["info"]["server_state"]
            log.debug("Server State: {}".format(server_state))
            if server_state == "proposing":
                log.info("  Server state: proposing")
                server_proposing = True
            else:
                log.debug("Check server status after {} seconds...".format(wait_time))
                time.sleep(wait_time)

    if server_proposing:
        return True
    return False


def rippled_stop(rippled_exec, config):
    log.info("  Stopping rippled...")
    cmd_to_stop = "{} --conf {} --silent stop".format(rippled_exec, config)
    run_external_command(cmd_to_stop)
    return wait_for_server_stop(rippled_exec, config)


def rippled_start(rippled_exec, config):
    log.info("  Starting rippled...")
    cmd_to_start = "{} --conf {} --silent".format(rippled_exec, config)
    run_external_command(cmd_to_start, wait=False)
    return wait_for_rippled_start(rippled_exec, config)


def format_currency(amount):
    """
    amount: drops or currency amount
    """
    if isinstance(amount, str):
        xrp = (int(amount)/1e6)
        return f"{xrp} XRP"
    amount_string = f"{amount['currency']}"
    if amount.get('issuer'):
        amount_string = f"{amount_string}.{amount['issuer'][:6]}"
    if amount.get('value'):
        amount_string = f"{amount.get('value')} {amount_string}"
    return amount_string


def get_unix_epoch_time():
    return int(time.time())
