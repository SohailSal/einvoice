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
touch project/.env (enter API_KEY_FBR="your api key" in this project/.env file) 
python manage.py runserver
goto localhost:8000 and login with the above username and password

In case of vps with public ip address, follow a couple of steps:
In project/settings.py file, insert your server ip address in ALLOWED_HOSTS = ['your server ip address']
python manage.py runserver 0.0.0.0:8000

Alternately, you may follow instructions given in following blog post:
https://bittenbook.com/steps-to-install-a-django-project/
