#!/bin/sh
# Setup script for Backup Wi-Fi Access Point (OpenWrt/Linux based)
# Run as root

SSID="BOB_Offline_Fallback"
PASS="OfflineMode2026!"
SUBNET="192.168.2.1"
DHCP_RANGE="192.168.2.100,192.168.2.200,12h"

echo "Setting up Backup Access Point..."

# 1. Configure Wireless Interface (hostapd)
# We assume wlan0 is the interface
cat <<EOF > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=$SSID
hw_mode=g
channel=6
wpa=2
wpa_passphrase=$PASS
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

echo "Wireless interface configured."

# 2. Configure Network Interface for the AP
cat <<EOF > /etc/network/interfaces.d/wlan0
auto wlan0
iface wlan0 inet static
    address $SUBNET
    netmask 255.255.255.0
EOF
# Note: For OpenWrt uci commands would be used, but this standard Linux approach is universal
echo "Network interface IP set to $SUBNET."

# 3. Configure dnsmasq for DHCP and local DNS
cat <<EOF > /etc/dnsmasq.conf
interface=wlan0
dhcp-range=$DHCP_RANGE
# Local DNS record for the hub
address=/homeassistant.local/192.168.1.10
EOF

echo "DHCP and local DNS configured."

# 4. Restart services
# systemctl restart hostapd
# systemctl restart dnsmasq
# systemctl restart networking

echo "Backup AP Setup complete. SSID: $SSID"
