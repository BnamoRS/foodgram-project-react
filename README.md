# Проект foodgram-project-react

![example workflow](https://github.com/BnamoRS/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Сайт Foodgram, «Продуктовый помощник» и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**Workflow** для проекта **foodgram-project-react**

При `git push` проекта на **Git Hub** настроен  **CI/CD**:
- автоматическая проверка линтером flake8;
- создается образ foodgram и пушится на Docker Hub;
- проект **foodgram-project-react** автоматически деплоится на сервер;
- при успешном прохождении всех этапов отправляется сообщение в Telegram.


## Зависимости:

- asgiref==3.5.2
- certifi==2022.6.15
- cffi==1.15.1
- charset-normalizer==2.1.1
- coreapi==2.3.3
- coreschema==0.0.4
- cryptography==37.0.4
- defusedxml==0.7.1
- Django==3.2.15
- django-cors-headers==3.13.0
- django-filter==22.1
- django-templated-mail==1.1.1
- djangorestframework==3.13.1
- djangorestframework-simplejwt==4.8.0
- djoser==2.1.0
- flake8==5.0.4
- gunicorn==20.1.0
- idna==3.3
- importlib-metadata==1.7.0
- itypes==1.2.0
- Jinja2==3.1.2
- MarkupSafe==2.1.1
- mccabe==0.7.0
- oauthlib==3.2.0
- Pillow==9.2.0
- psycopg2-binary==2.8.6
- pycodestyle==2.9.1
- pycparser==2.21
- pyflakes==2.5.0
- PyJWT==2.4.0
- python-dotenv==0.21.0
- python3-openid==3.2.0
- pytz==2022.2.1
- requests==2.28.1
- requests-oauthlib==1.3.1
- six==1.16.0
- social-auth-app-django==4.0.0
- social-auth-core==4.3.0
- sqlparse==0.4.2
- typing_extensions==4.3.0
- uritemplate==4.1.1
- urllib3==1.26.12
- zipp==3.8.1


## Установка:

### Описание переменных окружения:

- `DB_ENGINE=django.db.backends.postgresql` -  Указание, что используется postgresql;
- `DB_NAME=postgres` - имя базы данных;
- `POSTGRES_USER=postgres` - пользователь базы данных;
- `POSTGRES_PASSWORD=postgres` - пароль базы данных;
- `DB_HOST=db` - host базы данных;
- `DB_PORT=5432` - порт базы данных;
- `SECRET_KEY=p&l*******************(vs` - секретный ключ Django;
- `COMPOSE_PROJECT_NAME=yamdb` - имя проекта.

### Развернуть проект локально через docker:

- Установить `docker` и `docker-compose`;
- клонировать репозиторий;
- в директории  `.../foodgram-project-react/backend/foodgram/` создать файл `.env` с переменными окружения;
- из директории `.../foodgram-project-react/infra/` выполнить команду:
	```
	sudo docker-compose up -d
	```
- войти в терминал контейнера:
		```sudo docker exec -it infra_web_1 bash```
	- выполнить команды:
		```
		python manage.py migrate
		```
- создать суперпользователя комндой:
		```
		python manage.py createsuperuser
		```
- можно загрузить тестовую базу данных:

	- войти в терминал django:
		```
		python3 manage.py shell
		```
	- выполнить в открывшемся терминале django:
		```
		>>> from django.contrib.contenttypes.models import ContentType
		>>> ContentType.objects.all().delete()
		>>> quit()
		```
	- загрузить тестовую базу данных:
		```
		python manage.py loaddata data.json
		```

	- выйти из терминала контейнера командой:
		```
		exit

		```

Сайт **FOODGRAM** будет доступен по адресу: `http://localhost/`

## Автор:

***Роман Буцких***
