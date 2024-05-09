import subprocess
import time

disk_space_reached_slash = False
disk_space_reached_mnt = False

'''
During startup we want to capture the following
1. > /var/log/rippled_regular/iostat.txt
2. > /var/log/rippledrippled_process.out
'''

#Removing old data
subprocess.check_output('sudo rm -rf /mnt/rippled_data/db', shell=True)

# Clearing out iostart file from previous run
subprocess.check_output('> /home/mdoshi/iostat.txt', shell=True)

# Starting iostart file from previous run
subprocess.check_output("iostat 60 -t -x -d >/home/mdoshi/iostat.txt&", shell=True)

# Clearing out rippled_process file from previous run
subprocess.check_output('> /home/mdoshi/rippled_process.out', shell=True)

# Starting out the top to track rippled_regular process
subprocess.check_output('nohup top -b -p `pgrep rippled_regular|tail -1` -d 60 >/home/mdoshi/rippled_process.out 2>&1 &', shell=True)

subprocess.check_output('sudo /opt/ripple/bin/rippled_regular --quorum 1 --valid --fg&', shell=True)
time.sleep(120)

# Starting rippled_regular
output_rippled_process = subprocess.check_output('ps -ef | grep rippled_regular', shell=True)
if not "/opt/ripple/bin/rippled_regular --quorum 1 --fg" in str(output_rippled_process):
    subprocess.check_output('mail mdoshi@ripple.com -s "Rippled not starting" <<< "Warning your disk space is for mnt folder"', shell=True)