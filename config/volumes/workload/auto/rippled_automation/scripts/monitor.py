import subprocess
import time
import datetime


def main():
    count = 0
    while True:
        # Open file handlers in append mode
        get_counts_file_handler = open("get_counts.txt", "a")
        memory_usage_file_handler = open("memory_usage.txt", "a")

        # Append get_counts output to the file

        get_counts_file_handler.write(str(datetime.datetime.now()))
        get_counts_file_handler.write('\n')
        get_counts_file_handler.write(subprocess.check_output('/opt/ripple/bin/rippled get_counts', shell=True))
        get_counts_file_handler.write('\n')

        # Append memory usage output to the file
        get_counts_file_handler.write(str(datetime.datetime.now()))
        get_counts_file_handler.write('\n')
        memory_usage_file_handler.write(subprocess.check_output('sudo python ps_mem.py', shell=True))
        memory_usage_file_handler.write('\n')

        # Sleep for 2 minutes
        time.sleep(120)
        count = count + 1
        if count == 30:
            get_counts_file_handler.truncate(0)
            memory_usage_file_handler.truncate(0)
            count = 0


if __name__ == "__main__":
    main()
