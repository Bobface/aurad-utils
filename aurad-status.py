#!/usr/bin/env python3

import subprocess
import os
import time
import sys
import signal

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

fetch_latest_version_counter = 0
version_status = ""
latest_version = ""
version = ""
status = ""
percentage_uptime = 0
percentage_downtime = 0
current_block_num = 0

def read_logs():

	global fetch_latest_version_counter;
	global version_status;
	global latest_version;
	global version;
	global status;
	global percentage_uptime;
	global percentage_downtime;
	global current_block_num;

	dockerProc = subprocess.Popen(['docker','logs','docker_aurad_1'],stdout=subprocess.PIPE)

	online = 0
	offline = 0

	while True:
		line = dockerProc.stdout.readline().decode("utf-8")
		if line != '':
			if "STAKING" in line:
				status = ""
				if "ONLINE" in line:
					online += 1
					status += bcolors.OKGREEN
				else:
					offline += 1
					status += bcolors.FAIL

				status += line + bcolors.ENDC
			elif "Processing blocks" in line:
				current_block_num = extract_integers(line)[1]
			elif "Waiting for" in line:
				current_block_num = extract_integers(line)[0]
		else:
			break

	percentage_uptime = (float(online) / (online + offline)) * 100
	percentage_downtime = 100 - float(percentage_uptime)

	auraProc = subprocess.Popen(['aura','status'],stdout=subprocess.PIPE)

	version_line = auraProc.stdout.readline().decode("utf-8")
	if version_line != '':
		version = version_line.split()[1]


	# we don't need to fetch the latest version every time
	if fetch_latest_version_counter == 0 or fetch_latest_version_counter >= 50:
		npmProc = subprocess.Popen(['npm','show','@auroradao/aurad-cli','version'],stdout=subprocess.PIPE)

		latest_version_line = npmProc.stdout.readline().decode("utf-8")
		if latest_version_line != '':
			latest_version = "v" + latest_version_line.rstrip()

		fetch_latest_version_counter = 1
	else:
		fetch_latest_version_counter += 1


	if latest_version != version:
		version_status = bcolors.FAIL + bcolors.BOLD + "YOUR VERSION OF AURAD IS OUTDATED" + bcolors.ENDC
	else:
		version_status = bcolors.OKGREEN + "UP TO DATE" + bcolors.ENDC


def extract_integers(string):
	return [int(s) for s in string.split() if s.isdigit()]

def wait():
	progress_length = 20
	sleep_dur = 5
	for i in range(progress_length):
		string = "Next update: ["
		for j in range(i):
			string += "="
		for j in range(i,progress_length - 1):
			string += "-"

		string += "]"
		print('{0}\r'.format(string), end='', flush=True)

		time.sleep(float(sleep_dur)/progress_length)

def reset():
	global version_status;
	global version;
	global status;
	global percentage_uptime;
	global percentage_downtime;
	global current_block_num;

	version_status = ""
	version = ""
	status = ""
	percentage_uptime = 0
	percentage_downtime = 0
	current_block_num = 0

def exit_handler(sig, frame):
	os.system("reset")
	sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

#hide the cursor, restored on sigint
sys.stdout.write("\033[?25l")
sys.stdout.flush()

while True:
	reset()
	read_logs()
	os.system("clear")
	print("")
	print("Your version: " + version + " | Latest version: " + latest_version + " | " + version_status)
	print("Status: " + status+ "\n")
	print("Uptime: {0:.2f}%\n".format(percentage_uptime))
	print("Downtime: {0:.2f}%\n".format(percentage_downtime))
	print("Current block: " + str(current_block_num) + "\n")
	wait()

