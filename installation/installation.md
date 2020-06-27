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

## 5. Setup the Apache Webserver
(dir) (venv) (root)  

```bash
sudo mod_wsgi-express install-module
```

Copy the output into the `/etc/apache2/mods-available/wsgi.load` file.  
Activate mod-wsgi.
```bash
sudo a2enmod wsgi
```

Change the default VirtualHost configuration (`/etc/apache2/sites-available/000-default.conf`).  
`{venv_dir}` is the path to the virtual Python environment (e.g.`/home/pi/.venv/Self-Service-Terminal`).  
`{sst_dir}` is the path to the installation dir.
```
<VirtualHost *:80>
	# The ServerName directive sets the request scheme, hostname and port that
	# the server uses to identify itself. This is used when creating
	# redirection URLs. In the context of virtual hosts, the ServerName
	# specifies what hostname must appear in the request's Host: header to
	# match this virtual host. For the default virtual host (this file) this
	# value is not decisive as it is used as a last resort host regardless.
	# However, you must set it for any further virtual host explicitly.
	#ServerName www.example.com

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/html

	# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
	# error, crit, alert, emerg.
	# It is also possible to configure the loglevel for particular
	# modules, e.g.
	#LogLevel info ssl:warn

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	# For most configuration files from conf-available/, which are
	# enabled or disabled at a global level, it is possible to
	# include a line for only one particular virtual host. For example the
	# following line enables the CGI configuration for this host only
	# after it has been globally disabled with "a2disconf".
	#Include conf-available/serve-cgi-bin.conf
	
	WSGIDaemonProcess sp4 python-home={venv_dir} python-path={sst_dir}/softwareprojekt---self-service-terminal/sp4
	WSGIProcessGroup sp4 
	WSGIScriptAlias / {sst_dir}/softwareprojekt---self-service-terminal/sp4/sp4/wsgi.py
	
	Alias /files/ {sst_dir}/softwareprojekt---self-service-terminal/sp4/self_service_terminal/files/
	Alias /static/ {sst_dir}/softwareprojekt---self-service-terminal/sp4/self_service_terminal/static/

	<Directory {sst_dir}/softwareprojekt---self-service-terminal/sp4/self_service_terminal/static>
	Require all granted
	</Directory>

	<Directory {sst_dir}/softwareprojekt---self-service-terminal/sp4/self_service_terminal/files>
	Require all granted
	</Directory>


	<Directory {sst_dir}/softwareprojekt---self-service-terminal/sp4/sp4>
	<Files wsgi.py>
	Require all granted
	</Files>
	</Directory>	

</VirtualHost>
```

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