#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root: sudo ./install-aurad.sh"
  exit
fi

clear

echo "This program will automatically install aurad on your system."
echo ""
echo "This program is for INSTALLING aurad. Do not use it for upgrading to a new version."
echo ""
echo "Tested on Ubuntu 18.04. Might not work on other OSes."
echo ""
echo "To install aurad, it is required to create a non-root user."
echo "Please enter a username and password for the new user."
echo "If you have already created a new user, just enter the existing credentials."
echo ""



# Setting up a non-root user with root privileges

echo -n "	Username: "
read new_user_name



echo -e "\n"

if [ "$new_user_name" = "" ]; then
	
	echo "Please fill in a username."
	exit
fi

id -u $new_user_name > /dev/null 2>&1

if [ $? -ne 0 ]; then
	echo "User does not exist. Creating new user \"$new_user_name\""

	echo -n "	Password for the new user: "
	read -s new_user_password

	if [ "$new_user_password" = "" ]; then
		echo "Please fill in a password."
		exit
	fi

	useradd -g sudo -m -d /home/$new_user_name -s /bin/bash $new_user_name

	if [ $? -ne 0 ]; then
		echo "Could not create new user. Please contact tech support. Beep boop."
		exit
	fi

	echo $new_user_name:$new_user_password | chpasswd

	if [ $? -ne 0 ]; then
		echo "Could not set password for new user. Please contact tech support. Beep boop."
		exit
	fi
else 
	echo "User exists already."

	if getent group sudo | grep &>/dev/null "\b${new_user_name}\b"; then
    	echo "User is in sudoers group already."
	else
	    echo "User is not in sudoers group. Adding."
	    usermod -aG sudo $new_user_name > /dev/null 2>&1

	    if [ $? -ne 0 ]; then
		echo "Could not add existing user to sudo group. Please contact tech support. Beep boop."
		exit
		fi
	fi
fi
 
echo ""
echo "Installation begins now"
echo ""

apt update -y
apt install apt-transport-https ca-certificates curl software-properties-common ufw -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt update -y
apt install docker-ce -y
usermod -aG docker $new_user_name
apt install build-essential python docker-compose -y
ufw allow 22/tcp
ufw allow 8443/tcp
echo y | ufw enable


# Running as new user 

su $new_user_name -c "curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash"
su $new_user_name -c 'cd ~; NVM_DIR="$HOME/.nvm"; [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"; nvm install 10.15; npm install -g @auroradao/aurad-cli'

echo ""
echo "Set and done! Please logout (close the terminal) and login again to finish the installation."
echo "Then you can now run 'aura config' to setup your node. Happy staking!"
echo ""
