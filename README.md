#config
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic

#create supper user
python manage.py createsuperuser

#migrate 
python manage.py migrate

#runserver
python manage.py runserver
python manage.py runserver 8080

#create app to project
python manage.py startapp <AppName>
python manage.py makemigrations <AppName> // create migrations with app name models
- add module AppName to admin
+ AppName/admin.py
+ from .models import Question, Choice
+ admin.site.register(Question)
+ admin.site.register(Choice)

#create menu
python manage.py jet_side_menu_items_example

#crontab
python scheduleCron.py

#PostgreSQL Dump Files
pg_dump -U postgres -h localhost -p 5432 postgres > coaching-db.dump
psql -U app -h three-min-coach-service-prod-rds.ciprjsc7qspm.ap-northeast-1.rds.amazonaws.com -d django_rest_api -f coaching-db.dump

#######################################----STEP BY STEP----#########################################
- python3 -m pip install --user virtualenv
- python3 -m venv venv
- source venv/bin/activate
- python manage.py migrate
- config file .env
    
    #config static 
    + API_ENDPOINT=<--domain api-->
    + WEB_CLIENT=<--domain frontend--> 
    + CLIENT_ID=LJUiw5yOp0eEfs8l1EDdHbAaozRha4odpC3cCZde
    + CLIENT_SECRET=oeBsob03pSzaezb9WK4PvFeV97Jxek573BR5ctUCkq2DBGbTvrAB6pgJkRFgQ2Xl8MvqlkQolbcG0XFiRGVQFP1Yw0rIcE8TqZBkc29GiOg0E9Afb7JaPTpjtLVkovjt
    + ALLOWS_HTTPS='https'
    + PATH_ACCESS_LOG=''<--path access log file-->
    + PATH_ERROR_CRONJOB_LOG=''<--path error log file-->
    
    #config database
    + DATABASES_NAME=postgres
    + DATABASES_USER=postgres
    + DATABASES_PASSWORD=123456aA@
    + DATABASES_HOST=localhost
    + DATABASES_PORT=5432

- user admin : masamitsu.watanabe@ensemble.vn , pass : 123456aA@