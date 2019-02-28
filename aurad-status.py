#!/usr/bin/env python3

import subprocess
import os
import time
import sys
import signal
import json

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

config_auto_restart = False
config_wait_before_restart = 0
config_rpc = ""
config_download_latest = False

restarts = 0
fetch_latest_version_counter = 0
version_status = ""
latest_version = ""
version = ""
status = ""
percentage_uptime = 0
percentage_downtime = 0
current_block_num = 0
last_line = ""

was_online_once = False # Don't restart he node when it is syncing
is_online = False
offline_seconds = 0
last_run = time.time()

def read_config():
	global config_auto_restart;
	global config_wait_before_restart;
	global config_download_latest;
	global config_rpc;

	try:
		with open('aurad-status-settings.json', 'r') as f:
			jobj = json.loads(f.read())

			config_auto_restart = jobj["auto_restart"]
			config_wait_before_restart = jobj["wait_before_restart"]
			config_download_latest = jobj["download_latest"]
			config_rpc = jobj["rpc"]
			
			if config_auto_restart == True and config_wait_before_restart < 60:
				print("Timeout before restart must be at least 60 seconds. Using default settings with auto-restart disabled.")
				config_auto_restart = False
				config_wait_before_restart = 0
				config_rpc = ""
				config_download_latest = False
				time.sleep(3)

	except:
		print("Warning: Could not read config file! Continuing with default settings in 3 seconds.")
		time.sleep(3)

def read_logs():

	global fetch_latest_version_counter;
	global version_status;
	global latest_version;
	global version;
	global status;
	global percentage_uptime;
	global percentage_downtime;
	global current_block_num;
	global is_online;
	global was_online_once;
	global last_line;

	dockerProc = subprocess.Popen(['docker','logs','docker_aurad_1'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

	online = 0
	offline = 0

	last_line_current_run = ""
	while True:
		line = dockerProc.stdout.readline().decode("utf-8")
		if line != '':
			last_line_current_run = line
			if "STAKING" in line:
				status = ""
				if "ONLINE" in line:
					online += 1
					status += bcolors.OKGREEN

					if not was_online_once:
						offline_seconds = 0

					was_online_once = True
					is_online = True
				else:
					offline += 1
					status += bcolors.FAIL
					is_online = False

				status += line + bcolors.ENDC
			elif "Processing blocks" in line:
				if len(extract_integers(line)) >= 2:
					current_block_num = extract_integers(line)[1]
			elif "Waiting for" in line:
				if len(extract_integers(line)) >= 1:
					current_block_num = extract_integers(line)[0]
		else:
			break
			
	# Check that the container has not died and is not stuck
	if last_line_current_run == last_line:
		is_online = False
	
	last_line = last_line_current_run

	if online + offline == 0:
		percentage_uptime = 0
	else:
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


def check_for_restart():
	global config_auto_restart;
	global config_wait_before_restart;
	global config_download_latest;
	global config_rpc;
	global offline_seconds;
	global restarts;
	global was_online_once;

	if not config_auto_restart:
		return

	if offline_seconds > config_wait_before_restart:

		print("Offline for " + str(int(offline_seconds)) + " seconds. Restarting.")

		offline_seconds = 0
		was_online_once = False

		
		print("Stopping...")
		subprocess.Popen(['aura','stop']).wait()

		if config_download_latest:
			print("Downloading latest version...")
			subprocess.Popen(['npm','install','-g','@auroradao/aurad-cli']).wait()

		print("Starting...")

		if config_rpc != "" and config_rpc != " ":
			subprocess.Popen(['aura','start','--rpc',config_rpc]).wait()
		else:
			subprocess.Popen(['aura','start']).wait()

		restarts += 1
		os.system("clear")


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

read_config()

while True:
	reset()
	read_logs()
	os.system("clear")

	current_time = time.time()

	if was_online_once and not is_online:
		offline_seconds += current_time - last_run
		check_for_restart()
	elif is_online:
		offline_seconds = 0

	last_run = current_time

	
	print("")
	print("Your version: " + version + " | Latest version: " + latest_version + " | " + version_status)
	print("Status: " + status+ "\n")
	print("Uptime: {0:.2f}%\n".format(percentage_uptime))
	print("Downtime: {0:.2f}%\n".format(percentage_downtime))
	print("Restarts: " + str(restarts) + "\n")
	print("Current block: " + str(current_block_num) + "\n")
	wait()

