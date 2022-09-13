python manage.py migrate
python manage.py collectstatic --no-input
python manage.py loaddata data.json
gunicorn foodgram.wsgi:application --bind 0:8000