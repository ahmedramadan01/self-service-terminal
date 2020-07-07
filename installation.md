# Preconditions
- existing Python virtual environment
  - create with `python3 -m venv /path/to/venv/venv_name`
- existing installation directory (e.g. `/home/{user}/Self-Service-Terminal`)

# Constraints
The following commands are to be run
1. in the virtual Python environment. (venv)
2. as root. (root)
3. in the installation directory. (dir)

# Steps
## 1. Update your system and install all necessary packages
(root)  
```bash
sudo apt update && sudo apt upgrade -y  
sudo apt install apache2 apache2-dev cups hostapd dnsmasq  
```

## 2. Install all necessary pip packages
(venv)  
```bash
pip install django django-import-export mod_wsgi Pillow pdf2image  
```

## 3. Clone the source code into your installation directory
(dir)  
```bash
git clone {url/to/self_service_terminal}
```  

## 4. [Setup the Wireless Access Point](https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md)
(root)  

```bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent
```

Append the following text to the file `/etc/dhcpcd.conf`:
```
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

Create the file `/etc/sysctl.d/routed-ap.conf`:
```
net.ipv4.ip_forward=1
```

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save
```

Change to content of `/etc/dnsmasq.conf` to:
```bash
interface=wlan0                                         # Listening interface
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h   # Pool of IP addresses served via DHCP
domain=wlan                                             # Local wireless DNS domain
address=/gw.wlan/192.168.4.1                            # Alias for this router
```

```bash
sudo rfkill unblock wlan
```

Change the content of `/etc/hostapd/hostapd.conf` (the Access Point settings) to :
```
country_code={}
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
rsn_pairwise=CCMP
```
`country_code` should be for example GB, DE, US according to where you are.  
`ssid` should be the name of the network and `wpa_passphrase` a strong passphrase.

Run
```bash
sudo systemctl reboot
```
to restart the system and make the Access Point available.  

Useful commands for hostapd:  
- `systemctl status hostapd`
- `sudo systemctl stop hostapd`
- `sudo systemctl start hostapd`
- `sudo systemctl disable hostapd`
- `sudo systemctl enable hostapd`

## 5. Setup Autostart with a Unit File
(root)  
Create the file `/lib/systemd/system/runmodwsgi.service` and add the following content:

```ini
[Unit]
Description=Run mod_wsgi
After=multi-user.target

[Service]
ExecStart={venv_path}/bin/python3 {installation_path}/sp4/manage.py runmodwsgi --reload-on-change --user {username} --group {username}

[Install]
WantedBy=multi-user.target
```

__Substitute the parts in curly brackets {}__

__{venv_path}__ is the absolute path to the virtual Python environment.  
__{installation_path}__ is the absolute path to the installation directory.  
__{username}__ is the name of the user in whose home directory contains the installation directory.

Then run
```bash
sudo systemctl daemon-reload
sudo systemctl enable runmodwsgi.service
```

The Self-Service-Terminal is now available as a website on port 8000 after every reboot.


## [OPTIONAL] 6. Setup the remote interface for CUPS`
(root)  
```bash
sudo usermod -a -G lpadmin $USER
```
`$USER` is the user in whose home directory the self-service-terminal was installed.  

Change `/etc/cups/cupsd.conf` like this:  
```
# Only listen for connections from the local machine
# Listen localhost:631
Port 631

< Location / >
    Order allow,deny
    Allow @local
< /Location >

< Location /admin >
    Order allow,deny
    Allow @local
< /Location >

< Location /admin/conf >
    AuthType Default
    Require user @SYSTEM
    Order allow,deny
    Allow @local
< /Location >
```

Restart the cups server:  
```bash
sudo systemctl restart cups
```

The CUPS GUI Interface can now be accessed via a webbrowser:  
```
{IP or hostname}:631
```