Installation steps:

git clone https://github.com/sohailsal/einvoice
cd einvoice
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
(enter a username, then email and password...remember them)
python manage.py loaddata sales/sample
python manage.py runserver
goto localhost:8000 and login with the above username and password

Alternately, you may follow instructions given in following blog post:
https://bittenbook.com/steps-to-install-a-django-project/
