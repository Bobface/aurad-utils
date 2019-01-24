#!/usr/bin/env python3

import json

def boolToString(b):
	if b == True:
		return "Yes"
	else:
		return "No"

auto_restart = False
wait_before_restart = 0
rpc = ""
download_latest = False

print("\n--- aurad-status setup\n")

inp = input("Do you want to restart your node automatically when it goes offline? [Y/N]: ")

if inp == "Y" or inp == "y":
	auto_restart = True

	inp = input("Enter the time in seconds your node must be offline before restarting: ")

	if not inp.isdigit():
		print("Invalid input")
		exit()
	else:
		wait_before_restart = int(inp)

		rpc = input("Enter the RPC you want to use (for example \"https://mainnet.infura.io/v3/<API KEY>\"). Leave empty for default: ")


		inp = input("Download the latest version when automatically restarting? [Y/N]: ")

		if inp == "Y" or inp == "y":
			download_latest = True


print("\nSaving the following settings:\n")
print("Automatic restart when node goes offline: " + boolToString(auto_restart))

if auto_restart:
	print("Time to wait before restarting: " + str(wait_before_restart) + " seconds")
	print("RPC to use: " + str(rpc))
	print("Download latest version on restart: " + boolToString(download_latest))


inp = input("\nIs that correct? [Y/N]: ")

if inp == "Y" or inp == "y":
	jobj = {}
	jobj["auto_restart"] = auto_restart
	jobj["wait_before_restart"] = wait_before_restart
	jobj["rpc"] = rpc
	jobj["download_latest"] = download_latest

	try:
		with open('aurad-status-settings.json', 'w') as f:
  			json.dump(jobj, f)
	except:
  		print("Could not write settings to disk. Please make sure you have write permissions in this directory.")

	print("\nSettings saved. You can now run ./aurad-status.py")
else:
	print("\nAborted. No settings were changed.")



