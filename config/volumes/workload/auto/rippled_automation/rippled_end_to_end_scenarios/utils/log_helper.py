from datetime import datetime
import logging
import os
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TIMESTAMP = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
TESTLOG_FILE_NAME_PREFIX = "testrun"
FAILURE_LOG_FILE_NAME = "failures.log"


def get_log_dir(base_dir, test_suite=None):
    log_dir = f"{TIMESTAMP}_{test_suite}_logs" if test_suite else f"{TIMESTAMP}_logs"
    return os.path.join(base_dir, "logs", "test_logs", log_dir)


def get_logger():
    return logger


def add_stream_handler(log_level):
    formatter = logging.Formatter(fmt='\r%(asctime)s (%(filename)30s:%(lineno)-4s) %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    screen_handler.setLevel(log_level)

    get_logger().addHandler(screen_handler)
    get_logger().propagate = False


def add_file_handler(args, log_level):
    formatter = logging.Formatter(fmt='%(asctime)s (%(filename)25s:%(lineno)-3s) %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    log_filename = f"{TESTLOG_FILE_NAME_PREFIX}_{log_level}.log"
    test_log_filepath = os.path.join(args.logDir, log_filename)
    file_handler = logging.FileHandler(test_log_filepath, mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    get_logger().addHandler(file_handler)


def setup_logging(args):
    if not args.multipleTestSuiteInParallel:  # Enable console output only for Single testsuite run
        add_stream_handler(log_level=args.logLevel)
    for log_level in ["INFO", "DEBUG"]:
        add_file_handler(args, log_level=log_level)

