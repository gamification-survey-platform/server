# Use this script to restart your psql database locally
# Modify username and data file fields
sudo -u dbuser psql postgres -c "DROP DATABASE dev;"
sudo -u dbuser psql postgres -c "CREATE DATABASE dev;"
python manage.py migrate
python manage.py loaddata app/gamification/fixtures/initial_data_prod.json