# 🚀Wagtail_Hetzner_Deployment
In this article, we will learn how to deploy a <mark>wagtail</mark> application with Nginx, Gunicorn, PostgreSQL

## Production Stack Architecture
- OS - Ubuntu
- WSGI Server - Gunicorn
- Web Server - Nginx
- Database - PostgreSQL

## The following diagram illustrates how <mark>Wagtail</mark> works in the production environment
<p align="center">
  <img src="https://djangocentral.com/media/uploads/django_nginx_gunicorn.png"/>
</p>

## Log in to the server
```
ssh root@IP_Address
```

## Create a system user
```
adduser master
```
```
usermod -aG sudo master
```

## Make sure OpenSSH is enabled
```
ufw app list
ufw allow OpenSSH
ufw enable
ufw status
```

## Copy your root SSH Key to the new Ubuntu user account(<code>Optional</code>)
```
rsync --archive --chown=newuser:newuser ~/.ssh /home/newuser
```
- exit your ssh session with <code>ctrl + d</code>
```
ssh newuser@167.172.xxx.xx
```

## Install Packages
```
sudo apt update
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```
## Setting up PostgreSQL
```
sudo -u postgres psql
```
```
CREATE USER database_user WITH PASSWORD 'some_password';
CREATE DATABASE database_name OWNER database_user;
ALTER ROLE database_user SET client_encoding TO 'utf8';
ALTER ROLE database_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE database_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE database_name TO database_user;
\q
```

## Creating a Virtual Environment
```
python3 -m venv venv_name
 
source venv_name/bin/activate
```
## Settings up the project
- Create a new project directory <code>mkdir ~/yourprojectname && cd ~/yourprojectname</code>
```
git clone git_url
```
```
pip install gunicorn psycopg2-binary
```
```
pip install -r requirements.txt
```
## changes in settings.py file to make it deployment-ready
<code>production.py:</code>
```
SECRET_KEY = "secret-key"

ALLOWED_HOSTS = ["Ip_Address"]
```
<code>settings.py</code>
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangodb',
        'USER': 'djangouser',
        'PASSWORD': 'm0d1fyth15',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
<p>Luckily Django/Wagtail comes with a utility to run checks for a production-ready application run the following command in your terminal.</p>

```
python manage.py check --deploy
```
- You will see an output with no errors but several warnings. This means the check was successful, but you should go through the warnings to see if there is anything more you can do to make your project safe for production.
```
python manage.py collectstatic --settings=yourprojectname.settings.production
```
```
python manage.py runserver 0.0.0.0:8000 --settings=yourprojectname.settings.production
```
- At this point you should see migrations are required.<code>Cancel</code> your server and run it normally with Set the DJANGO SETTINGS MODULE with:
```
export DJANGO_SETTINGS_MODULE='yourprojectname.settings.production'
```
- Re run the server <code>python manage.py runserver</code> and we no longer need to specify a settings file
```
python manage.py migrate
```
```
python manage.py createsuperuser
```
```
sudo ufw allow 8000
```
```
python manage.py runserver 0.0.0.0:8000
```
- ## 🚀In your web browser navigate to [http://server_domain_or_IP:8000](http://server_domain_or_IP:8000) and you should see the app.












  
