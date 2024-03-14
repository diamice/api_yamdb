# Проект «API для YaMDb»

Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
## Требования к установке

- Python 3.x
- Установленные зависимости из `requirements.txt`


## Установка зависимостей
Перед установкой зависимостей рекомендуется создать виртуальное окружение:

```bash
python -m venv venv
```
Активируйте виртуальное окружение:

На Windows:
```bash
venv\Scripts\activate
```
На Linux или MacOS:
```bash
source venv/bin/activate
```
Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск проекта
Перейти в директорию yatube_api:

```bash
cd api_yamdb
```
Выполнить миграции:
```bash
python manage.py migrate
```

Выполнить команду:
```bash
python manage.py runserver
```

## Документация API
Примеры запросов к API доступны в документации Redoc по адресу: http://127.0.0.1:8000/redoc/. 

## Лицензия
This project is Licensed under [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
