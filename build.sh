#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create and set permissions for staticfiles directory
mkdir -p staticfiles
chmod 755 staticfiles

# Run migrations in correct order
python manage.py migrate auth
python manage.py migrate contenttypes
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate django_apscheduler
python manage.py migrate accounts
python manage.py migrate letters
python manage.py migrate

# Collect static files with force flag
python manage.py collectstatic --no-input --clear 