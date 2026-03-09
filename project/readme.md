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