#!/bin/sh
# Use this shell script to Relaunch the server (pulling changes from Git) without relaunching the database
ssh -i ~/.ssh/aws-gamification-ec2.pem ec2-user@ec2-13-57-207-133.us-west-1.compute.amazonaws.com "screen -S server -X quit;"

ssh -i ~/.ssh/aws-gamification-ec2.pem ec2-user@ec2-13-57-207-133.us-west-1.compute.amazonaws.com "cd server && git pull origin main && source venv/bin/activate && screen -S server -d -m python manage.py runserver 0.0.0.0:8000"