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
- 🚀In your web browser navigate to [http://server_domain_or_IP:8000](http://server_domain_or_IP:8000) and you should see the app.
```
gunicorn --bind 0.0.0.0:8000 yourprojectname.wsgi
```
- 🚀In your web browser navigate to [http://server_domain_or_IP:8000](http://server_domain_or_IP:8000) and you should see the app.

<p>Once you finishing testing the app press <code>ctrl + c</code> to stop the process and <code>deactivate</code> the virtual environment.</p>

```
deactivate
```
Create a gunicorn socket file <code>sudo nano /etc/systemd/system/gunicorn.socket</code> Add this to it:
```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```
Create a systemd file for gunicorn with <code>sudo privileges sudo nano /etc/systemd/system/gunicorn.service</code> And add this into it:
- <code>User=root</code>
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=newuser
Group=www-data
WorkingDirectory=/home/newuser/yourprojectname
ExecStart=/home/newuser/yourprojectname/venv/bin/gunicorn \
        --access-logfile - \
        --workers 3 \
        --bind unix:/run/gunicorn.sock \
        yourprojectname.wsgi:application

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl start gunicorn.socket && sudo systemctl enable gunicorn.socket
```
if <code>not working?</code>
```
sudo systemctl enable gunicorn.socket &&  sudo systemctl start gunicorn.socket
```
```
sudo systemctl status gunicorn.socket
```
- Check the existence of the new socket file <code>file /run/gunicorn.sock</code>
- Check the gunicorn status with <code>sudo systemctl status gunicorn</code> You should see <code>INACTIVE DEAD</code>
- 🧪Test the socket activation with a curl command <code>curl --unix-socket /run/gunicorn.sock localhost</code> You should see the <code>html output</code> of your site.
- ♻️If you didnt, something is wrong with gunicorn. Double check your wsgi.py file, double check the gunicorn paths.
- At this point it doesnt hurt to restart gunicorn with <code>sudo systemctl daemon-reload && sudo systemctl restart gunicorn</code>

## Create a new server block in nginx <code>sudo nano /etc/nginx/sites-available/yourprojectname</code> And add this:
- <code>server_domain_or_IP</code>: Type domain name or server IP.
- <code>/path/to/staticfiles</code>: change it!
```
server {
    listen      80;
    listen      [::]:80;
    server_name 167.172.xxx.xx;
    charset     UTF-8;

    error_log   /home/newuser/yourprojectname/nginx-error.log;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /media/ {
        alias /home/newuser/yourprojectname/media/;
    }
    location /static/ {
        alias /home/newuser/yourprojectname/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```
```
sudo ln -s /etc/nginx/sites-available/yourprojectname /etc/nginx/sites-enabled
```
```
sudo nginx -t
```
```
sudo systemctl restart nginx
```
Finally, we need to open up our firewall to normal traffic on port 80. Since we no longer need access to the development server, we can remove the rule to open port 8000 as well.
```
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```
When launching your website update your nginx settings <code>sudo nano /etc/nginx/sites-available/yourprojectname</code> Replace <code>167.172.xxx.xx</code> with <code>yourwebsite.com</code>
```
sudo nginx -t
```
```
sudo systemctl restart nginx
```
### Add your new domain to your allowed hosts <code>sudo nano yourprojectname/settings/production.py</code> Add <code>yourwebsite.com</code> to the <code>ALLOWED_HOSTS</code> and Remove the ip address of <code>167.172.xxx.xx</code>
- Add <code>167.172.xxx.xx</code> to your domain DNS settings and wait for it to <strong><mark>propogate</mark></strong>
- 🚀In your web browser navigate to [http://yourwebsite.com](http://yourwebsite.com) and you should see the app.

## Update the wagtail site settings Go to <code>http://yourwebsite.com/admin/sites/2/</code> and: change <bold>localhost</bold> to <bold>yourwebsite.com</bold>
- Open your browser and go to the URL: <code>http://yourwebsite.com/admin/sites/2/</code>
- Update the domain from "localhost" to your website's domain <bold>yourwebsite.com</bold>
- You will see the "Site settings" page for your website
- In this settings page, look for the "Hostname" field, which is likely set to "localhost."
- Change "localhost" to the actual domain name of your website, e.g., yourwebsite.com (replace with your domain).
- Save the changes.
## Why update the <bold>Wagtail site settings</bold> is Important:
- Wagtail uses site settings to determine the correct domain name for your project. By updating it from "localhost" to your website’s actual domain, the website will serve properly in a production environment.
