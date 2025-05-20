#!/bin/bash

# Kleuren voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Functie voor het printen van status berichten
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

# Check of script als root draait
if [ "$EUID" -ne 0 ]; then 
    print_error "Dit script moet als root worden uitgevoerd (gebruik sudo)"
    exit 1
fi

# Huidige map opslaan
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

print_status "Start installatie van Raspberry Pi Dashboard..."

# Update systeem en installeer benodigde pakketten
print_status "Updaten van systeem en installeren van benodigde pakketten..."
apt update
apt install -y chromium-browser xorg openbox python3 python3-pip

# Maak zeker dat de scripts uitvoerbaar zijn
print_status "Scripts uitvoerbaar maken..."
chmod +x "$SCRIPT_DIR/start_dashboard.sh"
chmod +x "$SCRIPT_DIR/main.py"

# Configureer autostart voor de GUI
print_status "Configureren van autostart..."
mkdir -p /etc/xdg/lxsession/LXDE-pi/
cat > /etc/xdg/lxsession/LXDE-pi/autostart << EOL
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xset s off
@xset -dpms
@xset s noblank
EOL

# Configureer de service
print_status "Configureren van systemd service..."
cat > /etc/systemd/system/dashboard.service << EOL
[Unit]
Description=Raspberry Pi Dashboard
After=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/bin/bash ${SCRIPT_DIR}/start_dashboard.sh
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
EOL

# Start en enable de service
print_status "Activeren van de service..."
systemctl daemon-reload
systemctl enable dashboard.service
systemctl start dashboard.service

# Configureer autologin voor de pi gebruiker
print_status "Configureren van automatisch inloggen..."
raspi-config nonint do_boot_behaviour B4

# Schakel screensaver uit
print_status "Uitschakelen van screensaver..."
if [ -f /etc/xdg/lxsession/LXDE-pi/autostart ]; then
    sed -i 's/@xscreensaver/#@xscreensaver/' /etc/xdg/lxsession/LXDE-pi/autostart
fi

# Configureer HDMI instellingen
print_status "Configureren van HDMI instellingen..."
if ! grep -q "hdmi_group" /boot/config.txt; then
    echo "hdmi_group=2" >> /boot/config.txt
    echo "hdmi_mode=87" >> /boot/config.txt
    echo "hdmi_cvt=2560 1080 60" >> /boot/config.txt
    echo "hdmi_force_hotplug=1" >> /boot/config.txt
fi

print_status "Installatie voltooid!"
print_status "Het systeem moet opnieuw worden opgestart om alle wijzigingen door te voeren."
print_status "Wil je nu herstarten? (j/n)"
read -r response

if [[ "$response" =~ ^([jJ]|[yY])$ ]]; then
    print_status "Systeem wordt herstart..."
    reboot
else
    print_status "Herstart het systeem handmatig wanneer je klaar bent."
fi 