# Utility scripts for AuraD

For more information about AURA Staking see also [auraview.net](https://auraview.net)

## Requirements
Ubuntu machine with `python3` and `git` installed.
To check if those are installed:
```
python3 --version
git --version
```

## How  to use

### Clone this git repo
```
git clone https://github.com/Bobface/aurad-utils.git 
cd aurad-utils
``` 
### Setup
Run the setup script if you want to change some settings. This is only required once for each update.
After a update is released, it might be necessary to re-run the setup script.
Example:
```
cd aurad-utils
./setup-aurad-status.py
```
After the setup is complete, you can run the script as described below.
In case you want to change the settings again, just re-run the setup script.

### Execute a script
```
cd aurad-utils
./<script name.py>
```

Example:
```
cd aurad-utils
./aurad-status.py
```

### Stop a script

Press `CTRL+C`

## How to update
When changes are made to this repo and you want the latest version, `pull` the changes:
```
cd aurad-utils
git pull
```

## Having issues?
If you found a bug you can [write an issue on GitHub](https://github.com/Bobface/aurad-utils/issues) or contact me on Discord if you need help installing or using this repo: *Bobface#9040*. 
