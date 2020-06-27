# Installation Guide
## Preconditions
- existing Python virtual environment
  - create with `python3 -m venv /path/to/venv/venv_name`
- existing installation directory (e.g. `/home/{user}/Self-Service-Terminal`)

## Constraints
The following commands are to be run
1. in the virtual Python environment. (venv)
2. as root. (root)
3. in the installation directory. (dir)

## Steps
### 1. Update your system and install all necessary packages
(root)  
`sudo apt update && sudo apt upgrade -y`  
`sudo apt install apache2 apache2-dev cups`  

### 2. Install all necessary pip packages
(venv)  
`pip install django django-import-export mod_wsgi Pillow pdf2image`  
