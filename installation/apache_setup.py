# run like this: sudo /path/to/venv/bin/python apache_setup.py

from subprocess import run
import sys
import getpass

# get ouput from command and convert to string and write output to wsgi.load config file

result = run("sudo mod_wsgi-express install-module", shell=True, capture_output=True)
with open("/etc/apache2/mods-available/wsgi.load", mode="w") as fp:
    fp.write(result.stdout.decode("ascii"))


run("sudo a2enmod wsgi", shell=True)

# get paths needed in 000-default.config file and add them to string

venv_path = sys.prefix
current_user = getpass.getuser()
default_path = "/home/{}/Self-Service-Terminal/sp4".format(current_user)
sst_path = default_path + "/self_service_terminal"
sp4_path = default_path + "/sp4"

default_config = """
\tWSGIDaemonProcess sp4 python-home={venv_path} python-path={sst_path}
\tWSGIProcessGroup sp4
\t
\tAlias /files/ {sst_path}/files/
\tAlias /static/ {sst_path}/static/
\t
\t<Directory {sst_path}/static>
\tRequire all granted
\t</Directory>
\t
\t<Directory {sst_path}/files>
\tRequire all granted
\t</Directory>
\t
\tWSGIScriptAlias / {sp4_path}/sp4/wsgi.py
\t
\t<Directory {sp4_path}/sp4>
\t<Files wsgi.py>
\tRequire all granted
\t</Files>
\t</Directory>
"""
default_config = default_config.format(venv_path=venv_path, sst_path=sst_path, sp4_path=sp4_path)

# insert modified string after "Virtual Host" in string - overwrite config file with added content

with open("/etc/apache2/sites-enabled/000-default.conf", mode="r") as fp:
    config_content = fp.read()

before, seperator, after = config_content.partition("</VirtualHost>")
return_config = before + default_config + seperator + after

with open("/etc/apache2/sites-enabled/000-default.conf", mode = "w") as fp:
    fp.write(return_config)
