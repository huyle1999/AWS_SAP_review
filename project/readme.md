APi app for restaurant deploy in aws
pipenv install django djangorestframework djoser
pipenv shell
django-admin startproject LittleLemon
cd LittleLemon
python manage.py startapp LittleLemonAPI


cd LittleLemon
pipenv shell
pipenv install
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

logic for database model


luc migrate , bi hang ko biet loi do gi 
django June 15, 2026, 18:44 [2026-06-15 11:44:01 +0000] [1] [ERROR] Worker (pid:9) was sent SIGKILL! Perhaps out of memory? b55c476d2dc94c2cb9d98cc63cb79c22 django