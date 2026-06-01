#A setup script to initialize a pi for the project. The project requires a few commands regarding enabling I2C permissions, wifi setup, and installing dependencies.
#Rather than doing it manually, this file will (hopefully) do it all in on go

#Execute this script by running: bash setup.sh
#!/bin/bash
set -e

echo "=============================="
echo " Raspberry Pi Project Setup"
echo "=============================="

# ----------------------------
# SYSTEM UPDATE
# ----------------------------
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# ----------------------------
# SYSTEM DEPENDENCIES (IMPORTANT)
# ----------------------------
echo "Installing system dependencies..."

sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-opencv \
    python3-smbus \
    i2c-tools \
    libzbar0 \
    nodejs \
    npm

# ----------------------------
# I2C ENABLE (PERSISTENT)
# ----------------------------
echo "Enabling I2C..."

sudo raspi-config nonint do_i2c 0

echo "Loading I2C kernel module..."
sudo modprobe i2c-dev || true

echo "Adding user to i2c group..."
sudo usermod -aG i2c $USER

# ----------------------------
# PYTHON VIRTUAL ENV (FIX PEP 668)
# ----------------------------
echo "Creating Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

deactivate

# ----------------------------
# NODE (OPTIONAL SAFE)
# ----------------------------
if [ -f "package.json" ]; then
    echo "Installing Node dependencies..."
    npm install
else
    echo "No package.json found, skipping Node setup."
fi

# ----------------------------
# VERIFY I2C
# ----------------------------
echo "Checking I2C device..."

if ls /dev/i2c-* 1> /dev/null 2>&1; then
    echo "I2C detected ✔"
else
    echo "WARNING: I2C not detected (reboot required)"
fi

# ----------------------------
# FINAL MESSAGE
# ----------------------------
echo "=============================="
echo " Setup complete!"
echo " IMPORTANT:"
echo " - Reboot required for I2C + group permissions"
echo "   sudo reboot"
echo "=============================="

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

# Adjust time zone settings
# sudo timedatectl set-timezone America/Los_Angeles

# source /etc/default/locale

