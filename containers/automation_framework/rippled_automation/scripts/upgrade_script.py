import subprocess
import time
import datetime


def main():

    # Open file handlers in append mode
    get_upgrade_file_handler = open("upgrade.txt", "a")

    get_current_stats(get_upgrade_file_handler)
    start_upgrade_process(get_upgrade_file_handler)

    get_upgrade_file_handler.write('\n')
    get_upgrade_file_handler.write(subprocess.check_output('sudo /opt/ripple/bin/rippled --version', shell=True))
    get_upgrade_file_handler.write('\n')

    # Close file handler
    get_upgrade_file_handler.close()


def start_upgrade_process(get_upgrade_file_handler):
    time_to_restart_in_seconds = 1
    server_down = True

    # 1. Upgrade rippled (sudo yum install rippled)
    subprocess.check_output('sudo yum install rippled -y', shell=True)
    subprocess.check_output('sudo systemctl daemon-reload', shell=True)

    # 2. Restart rippled tracking the time it takes to restart
    subprocess.check_output('sudo systemctl restart rippled', shell=True)

    while server_down:

        # Check status of rippled server
        status = ''
        status = subprocess.check_output('sudo systemctl status rippled', shell=True)
        if 'running' in status:
            server_down = False
        else:
            time.sleep(1)
            time_to_restart_in_seconds = time_to_restart_in_seconds + 1

    # Time to restart
    get_upgrade_file_handler.write('\n')
    get_upgrade_file_handler.write(str(time_to_restart_in_seconds))
    get_upgrade_file_handler.write('\n')

    # 3e. Now check how long does it take to sync to the network: TBD


def get_current_stats(get_upgrade_file_handler):
    # Append current snapshot before upgrade
    get_upgrade_file_handler.write(str(datetime.datetime.now()))

    # Current version
    get_upgrade_file_handler.write('\n')
    get_upgrade_file_handler.write(subprocess.check_output('sudo /opt/ripple/bin/rippled --version', shell=True))
    get_upgrade_file_handler.write('\n')

    # Disk space
    get_upgrade_file_handler.write('\n')
    get_upgrade_file_handler.write(subprocess.check_output('df -h', shell=True))
    get_upgrade_file_handler.write('\n')

    # Memory info
    get_upgrade_file_handler.write('\n')
    get_upgrade_file_handler.write(subprocess.check_output('cat /proc/meminfo', shell=True))
    get_upgrade_file_handler.write('\n')


if __name__ == "__main__":
    main()
