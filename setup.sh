#A setup script to initialize a pi for the project. The project requires a few commands regarding enabling I2C permissions, wifi setup, and installing dependencies.
#Rather than doing it manually, this file will (hopefully) do it all in on go

#Execute this script by running: bash setup.sh

#!/bin/bash

#Enable I2C

#sudo apt install python3-smbus

#Adjust the config files to enable the I2C flag. This should automatically setup
#echo "Setting I2C device permissions..."
#sudo chmod 666 /dev/i2c-*

#echo "Installing Python dependencies from requirements.txt..."
#pip install -r requirements.txt

#Installing nodejs
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

echo "Installing Node.js dependencies..."
npm install

#Change parameters that fit your organization/locations wifi
echo "Adjusting wifi prioritizations..."
#nmcli connection add type wifi ifname wlan0 con-name orgwifi ssid "ORG_WIFI_NAME" \
#  802-11-wireless-security.key-mgmt wpa-eap \
#  802-1x.eap peap \
#  802-1x.identity "your_username" \
#  802-1x.password "your_password" \
#  802-1x.phase2-auth mschapv2

#nmcli connection modify orgwifi connection.autoconnect yes

# Org Wi-Fi: first choice. (Setting Priorities is optional)
#nmcli connection modify orgwifi connection.priority 100

#nmcli connection modify "<connection-name>" connection.autoconnect-priority <priority-value>

#nmcli connection modify "Hotspot" connection.autoconnect-retries 0 //Infinite amount of retries




