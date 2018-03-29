# ARMA Survey Management System
University of Arizona Capstone


## Run
### Windows 10 - Powershell
Activate venv: `.\venv\Scripts\activate`\
Set Flask environment variable: `$env:FLASK_APP = arma_sms.py`\
Configure and rename `config_template.py` to `config.py`\
`flask db init`\
`flask db migrate -m "users table"`\
`flask db upgrade`\
Run: `flask run`\
Enter `http://localhost:5000/` in browser

## Prerequisites
[Requirements](requirements.txt)