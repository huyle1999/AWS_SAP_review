## welcome to my guild aws sap
- lab run-through (only screenshot Diagram , config , result(dashboard , output) , CLI , errors): **25–40 mins**  
- write note again: **5–10 mins**  
## python app.
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install psycopg2-binary
docker run -d \
  --name postgres \
  -e POSTGRES_DB=restaurant \
  -e POSTGRES_USER=django \
  -e POSTGRES_PASSWORD=mypassword \
  -p 5432:5432 \
  postgres:16
python manage.py dumpdata \
  --exclude contenttypes \
  --exclude auth.permission \
  --indent 2 > data.json