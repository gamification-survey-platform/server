#!/bin/sh
# Use this script to relaunch the server AND restart the database
ssh -i ~/.ssh/aws-gamification-ec2.pem ec2-user@ec2-13-57-207-133.us-west-1.compute.amazonaws.com "screen -S server -X quit;"

export PGPASSWORD=gamificationIsFun!;
psql --host=gamification-free-tier.coktz054p2k3.us-west-1.rds.amazonaws.com --user=gamification --dbname=postgres -c "DROP DATABASE aws_free_tier;"
psql --host=gamification-free-tier.coktz054p2k3.us-west-1.rds.amazonaws.com --user=gamification --dbname=postgres -c "CREATE DATABASE aws_free_tier;"

ssh -i ~/.ssh/aws-gamification-ec2.pem ec2-user@ec2-13-57-207-133.us-west-1.compute.amazonaws.com "cd server && git pull origin main && source venv/bin/activate && python manage.py migrate && python manage.py loaddata app/gamification/fixtures/end_user_testing.json && screen -S server -d -m python manage.py runserver 0.0.0.0:8000"