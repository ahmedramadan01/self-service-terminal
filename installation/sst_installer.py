#!/home/pi/.venv/self_service_terminal/bin/python3

# Venv:
# os.system("python3 -m venv ~/.venv/self_service_terminal")
# os.system("source ~/.venv/self_service_terminal/bin/activate")

import os
import getpass

# Prepare Raspberry Pi OS:
os.system("sudo apt update") 
os.system("sudo apt upgrade")
os.system("sudo apt install python3 apache2 apache2-dev cups -y")

# Python:
os.system("pip install django mod_wsgi django-import-export Pillow pdf2image")

# Wlan, currently not operational

os.system("sudo apt install hostpad")

os.system("sudo systemctl unmask hostapd")
os.system("sudo systemctl enable hostapd")
os.system("sudo apt install dnsmasq")

os.system("sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent")

# config StaticIP, edit config file for dhcp

with open("/etc/dhcpcd.conf", mode="a") as fp:
    fp.write("\ninterface wlan0\n\tstatic ip_address=192.168.4.1/24\n\tnohook wpa_supplicant\n")

# enable routing and ip masquerading by creating config file

with open("/etc/sysctl.d/routed-ap.conf", mode = "a") as fp:
    fp.write("\nnet.ipv4.ip_forward=1") 

# adding firewall rules

os.system("sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")
os.system("sudo netfilter-persistent save")

# configure dhcp and dns for wlan, NICHT FUNKTIONAL
# rename default config file and edit new one
 
os.system("sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig")
with open("/etc/dnsmasq.conf", mode="a") as fp:
    fp.write("""\ninterface=wlan0\t#\tListeningInterface\ndhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h\t#\tPool of IP addresses served via DHCP\ndomain=wlan\t#\tLocal wireless DNS domain\naddress=/gw.wlan/192.168.4.1\t#\tAlias for this router""")
# ensure wireless operation
os.system("sudo rfkill unblock wlan")

# configure access point software
# create config file

country_code = input("Wählen Sie einen Ländercode (z.B. GB,DE,US) zur Konfiguration der Access Point Software hostapd.")
ssid = input("Wählen Sie die SSID des Access Point.")
passphrase = getpass.getpass("Wählen Sie das Passwort für das Netzwerk.")
with open("/etc/hostapd/hostapd.conf") as fp:
    fp.write("""country_code={}
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
    rsn_pairwise=CCMP""".format(country_code, ssid, passphrase))

# sudo nano /etc/hostapd/hostapd.conf
# FILL IN INFO FROM DOCUMENTATION
check = input("Um die Einrichtung abzuschließen, muss das System neu gestartet werden. Wollen Sie das jetzt tun? (y/n)")
if check == "y":
    os.system("sudo systemctl reboot")



