APi app for restaurant deploy in aws
pipenv install django djangorestframework djoser
pipenv shell
django-admin startproject LittleLemon
cd LittleLemon
python manage.py startapp LittleLemonAPI


python manage.py runserver

logic for database model