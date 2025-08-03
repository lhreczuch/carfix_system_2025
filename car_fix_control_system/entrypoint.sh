#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py migrate --run-syncdb
python manage.py migrate --noinput

python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
u, created = User.objects.get_or_create(
    username=os.environ['DJANGO_SUPERUSER_USERNAME'],
    defaults={
        'email': '',
        'is_staff': True,
        'is_superuser': True,
    }
)
u.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD'])
u.save()
"

exec gunicorn car_fix_control_system.wsgi:application --bind 0.0.0.0:8000
