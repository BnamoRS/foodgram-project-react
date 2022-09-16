FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
RUN echo python manage.py collectstatic --no-input
#RUN gunicorn foodgram.wsgi:application --bind 0:8000
ENTRYPOINT ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
#CMD ["python", "manage.py", "migrate", "--no-input"]
RUN echo python manage.py migrate --no-input
