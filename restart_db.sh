# Use this script to restart your psql database locally
# Modify username and data file fields
sudo -u <username> psql postgres -c "DROP DATABASE dev;"
sudo -u <username> psql postgres -c "CREATE DATABASE dev;"
python manage.py migrate
python manage.py loaddata <data file>