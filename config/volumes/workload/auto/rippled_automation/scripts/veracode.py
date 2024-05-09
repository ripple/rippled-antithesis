import os
import time
import argparse
import requests
from pathlib import Path
import gzip
import os
from subprocess import check_call
import subprocess
from shutil import copyfile
import xml.etree.ElementTree as etree

parser = argparse.ArgumentParser(description='Submit Veracode Scan')
parser.add_argument("username", help="Veracode API Username")
parser.add_argument("password", help="Veracode API Password")
parser.add_argument("app_id", help="Veracode Application Id")
parser.add_argument("project_jar", help="Main Project Jar")
parser.add_argument("project_version", help="Project Version")
parser.add_argument("project_build_path", help="Project Build Path")
parser.add_argument("sleep_time", help="Sleep Time to wait for Prescan in Seconds")
parser.add_argument("--skip_upload_dependencies", help="skip uploading dependenices in lib dir from build path",
                    action="store_true")

#args = parser.parse_args()

username = 'mdoshi@ripple.com'
password = 'Rippled1'
app_id = "475599"
skip_upload_dependencies = True
#project_jar = args.project_jar
#project_version = args.project_version
#project_build_path = args.project_build_path
#sleep_time = int(args.sleep_time)

project_jar = ""
project_version = 1.2
project_build_path = ""
sleep_time = int(600)

module_id = None


def main(project_version):
    print
    "Starting to Upload Build for Veracode Scan..."

    print
    "Creating Application Build Profile..."
    #createBuild()

    #print
    #"Uploading Main Application File... : " + project_jar + " - " + project_version

    upload_files(project_version)

    #if not args.skip_upload_dependencies:
    if not skip_upload_dependencies:
        print
        "Uploading Dependencies..."
        dirList = os.listdir(project_build_path + "/lib/")
        for fname in dirList:
            print
            "  Uploading : " + fname
            upload_files(project_build_path + "/lib/" + fname)
    else:
        print
        "Skipping Uploading Dependencies..."

    print
    "Running PreScan..."
    run_pre_scan()

    # Add some sleep logic here
    # print
    # "Waiting for PreScan to Complete..."
    # time.sleep(sleep_time)
    print("Done")

    # print
    # "Checking Results of PreScan..."
    # xmlPreScan = getPreScanResults()
    # namespace = "{https://analysiscenter.veracode.com/schema/5.0/prescanresults}"
    # root = etree.fromstring(xmlPreScan)
    # for module in root.findall(".//{0}module[@name='{1}']".format(namespace, project_jar)):
    #     print
    #     module.attrib
    #     module_id = module.get('id')
    #
    # print(module_id)
    # print
    # "Submitting Static Scan Request to Veracode..."
    # # Kick off Full Scan
    #beginScan()


def list_apps():
    r = requests.get("https://analysiscenter.veracode.com/api/5.0/getapplist.do", auth=(username, password))
    print(r.text)


def create_build(project_version):
    payload = {'app_id': app_id, 'version': project_version}
    r = requests.post("https://analysiscenter.veracode.com/api/5.0/createbuild.do", params=payload,
                      auth=(username, password))
    print(r.text)


def begin_scan():
    payload = {'app_id': app_id}
    r = requests.post("https://analysiscenter.veracode.com/api/5.0/beginscan.do",
                      params=payload, auth=(username, password))
    print(r.text)


def upload_files(uploadFileName):
    files = {'file': open(os.getcwd() + '/rippled.gz', 'rb')}
    payload = {'app_id': app_id}
    r = requests.post("https://analysiscenter.veracode.com/api/5.0/uploadfile.do", params=payload, files=files,
                      auth=(username, password))
    time.sleep(600)
    print(r.text)


def run_pre_scan():
    payload = {'app_id': app_id}
    r = requests.post("https://analysiscenter.veracode.com/api/5.0/beginprescan.do", params=payload,
                      auth=(username, password))
    print(r.text)


def get_pre_scan_results():
    payload = {'app_id': app_id}
    r = requests.post("https://analysiscenter.veracode.com/api/5.0/getprescanresults.do", params=payload,
                      auth=(username, password))
    # print r.text
    return r.text


def check_is_rippled_upgraded():
    execution_dir = os.getcwd()
    p = subprocess.Popen(['/opt/ripple/bin/rippled','--version'], stdout=subprocess.PIPE)
    current_version = (p.stdout.read())
    current_version = str(current_version)
    current_version = current_version[2:23]

    config = Path('current_version.txt')
    if config.is_file():
        version_file = open(config, 'r')
        rippled_version = version_file.read()
        if rippled_version == current_version:
            print("Rippled hasn't upgraded and there is nothing to do")
        else:
            if os.path.exists('rippled.gz'):
                os.remove("rippled.gz")
            copyfile('/opt/ripple/bin/rippled', execution_dir + '/rippled')
            time.sleep(3)
            check_call(['gzip', "rippled"])
            main(current_version)
            version_file = open(config, 'w+')
            version_file.truncate(0)
            version_file.write(current_version)
            version_file.close()
    else:
        print("Please create a version.txt file whose content should be the current rippled version example: "
              "rippled version 1.2.3")
    print("Done")


if __name__ == "__main__":
    check_is_rippled_upgraded()