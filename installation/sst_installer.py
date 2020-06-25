"""
It is recommended to call the script from within a Python virtual environment. 
"""

import os
from subprocess import run
import getpass

# git clone sst Pfadname: /home/Self-Service-Terminal/sp4/.....
# Prepare Raspberry Pi OS:
run("sudo apt update", shell=True) 
run("sudo apt upgrade", shell=True)
run("sudo apt install python3 apache2 apache2-dev cups -y", shell=True)

# Python:
run("pip3 install django mod_wsgi django-import-export Pillow pdf2image", shell=True)

# Wlan, currently not operational

run("sudo apt install hostpad", shell=True)

run("sudo systemctl unmask hostapd", shell=True)
run("sudo systemctl enable hostapd", shell=True)
run("sudo apt install dnsmasq", shell=True)

run("sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent", shell=True)

# config StaticIP, edit config file for dhcp

with open("/etc/dhcpcd.conf", mode="a") as fp:
    fp.write("\ninterface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant\n")

# enable routing and ip masquerading by creating config file

with open("/etc/sysctl.d/routed-ap.conf", mode = "w") as fp:
    fp.write("net.ipv4.ip_forward=1") 

# adding firewall rules

run("sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE", shell=True)
run("sudo netfilter-persistent save", shell=True)

# configure dhcp and dns for wlan, NICHT FUNKTIONAL
# rename default config file and edit new one
 
run("sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.old", shell=True)
with open("/etc/dnsmasq.conf", mode="w") as fp:
    fp.write("""interface=wlan0\t# ListeningInterface\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\t# Pool of IP addresses served via DHCP\ndomain=wlan\t# Local wireless DNS domain\naddress=/gw.wlan/192.168.4.1\t# Alias for this router""")
# ensure wireless operation
run("sudo rfkill unblock wlan", shell=True)

# configure access point software
# create config file

country_code = input("Wählen Sie einen Ländercode (z.B. GB,DE,US):")
ssid = input("Wählen Sie eine SSID:")
passphrase = getpass.getpass("Wählen Sie die WPA2-Passphrase:")
hostapd_config = """country_code={}
interface=wlan0
ssid={}
hw_mode=g
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP""".format(country_code, ssid, passphrase)

with open("/etc/hostapd/hostapd.conf", mode='w') as fp:
    fp.write(hostapd_config)

# sudo nano /etc/hostapd/hostapd.conf
# FILL IN INFO FROM DOCUMENTATION
check = input("Um die Einrichtung abzuschließen, muss das System neu gestartet werden. Wollen Sie das jetzt tun? (y/n)")
if check == "y":
    run("sudo systemctl reboot", shell=True)



# git clone des SST noch hinzufügen