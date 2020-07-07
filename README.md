# Self-Service Terminal for Health Insurance Offices

Using the self-service terminal for health insurance branches, customers of health insurance companies with little or no experience with technology can perform elementary functions independently on site in a branch.

Currently, forms can be selected and printed out via the terminal.

Currently the terminal is only available in German.

## Installation
The following things are necessary for operation:

- Raspberry Pi with WLAN module
- WLAN-enabled end devices (e.g. tablets)
- a printer

The installation steps are to be carried out on the Pi. Follow the instructions under installation.md. The terminal can be reached under the IP 192.168.4.1:8000 if you have followed the steps correctly. The backend is located at 192.168.4.1/admin.

The default logins for the backend are:
```
user=admin
password=admin
```
Change the password after installation.  
In `settings.py` change the value of `SECRET_KEY` to a different key of same length.
