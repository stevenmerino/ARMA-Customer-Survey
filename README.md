# ARMA-Customer-Survey
University of Arizona Capstone


## Run
### Windows 10 - Powershell
Activate venv: `.\venv\Scripts\activate`\
Set Flask environment variable: `$env:FLASK_APP = customer_survey.py`\
Configure and rename `config_template.py` to `config.py`\
`flask db init`\
`flask db migrate -m "users table"`\
`flask db upgrade`\
Run: `flask run`\
Enter `http://localhost:5000/` in browser\

## Prerequisites
[Requirements](requirements.md)