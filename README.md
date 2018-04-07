# ARMA Survey Management System
University of Arizona Capstone


## Run
### Windows 10 - Powershell
Create virtual environment: `virtualenv venv`\
Activate venv: `.\venv\Scripts\activate`\
Install requirements: `pip install -r requirements.txt`
Set Flask environment variable: `$env:FLASK_APP = arma_sms.py`\
Configure and rename `config_template.py` to `config.py`\
`flask db init`\
`flask db migrate -m "users table"`\
`flask db upgrade`\
Run: `flask run`\
Enter `http://localhost:5000/` in browser

## Prerequisites
[Requirements](requirements.txt)