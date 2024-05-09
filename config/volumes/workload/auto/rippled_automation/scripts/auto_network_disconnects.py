import subprocess
import time


def main():
    while True:
        subprocess.check_output('sudo service network stop', shell=True)
        time.sleep(600)
        subprocess.check_output('sudo service network start', shell=True)
        time.sleep(3600)


if __name__ == "__main__":
    main()
