[![Main Kittygram workflow](https://github.com/ViktorKors/kittygram_final/actions/workflows/main.yml/badge.svg)](https://github.com/ViktorKors/kittygram_final/actions/workflows/main.yml)

# Краткое 
Фудграм - соцсеть для публикации вкусных рецептов.

## Технологии:
- ![Python version](https://img.shields.io/pypi/pyversions/django)
- ![Django version](https://img.shields.io/pypi/v/django?label=django)
- ![DRF version](https://img.shields.io/pypi/v/djangorestframework?label=djangorestframework)
- ![Docker](https://img.shields.io/badge/using-Docker-green)
- ![Nginx](https://img.shields.io/badge/using-nginx-green)


### Процесс установки:
- Скопируйте репозиторий ```git clone git@github.com:ViktorKors/Foodgram.git```
- <details>
    <summary>Для запуска на удалённом сервере</summary>
      <li>Подключитесь к своему удалённому серверу <code>ssh {username}@{ip}</code></li>
      <li>Обновите существующие пакеты <code>sudo apt update && sudo apt upgrade -y</code></li>
      <li>Установите docker <code>sudo apt install docker.io</code></li>
      <li>Установите docker-compose <code>curl -SL https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose</code></li>
      <li>Дайте нужные разрешения docker-compose <code>sudo chmod +x /usr/local/bin/docker-compose</code></li>
      <li>Создайте нужные папки для проекта: <code>mkdir -p projects/foodgram</code></li>
      <li>Скопируйте себе содержимое папки infra <code>scp -r infra/* {username}@{ip}:/home/{username}/projects/foodgram/</code></li>
  </details>
- Создайте .env файл с вашими данными ```touch .env``` в папке infra/
- Заполните его следующим образом:
```
ALLOWED_HOSTS=<ip 1> <ip 2>
CSRF_TRUSTED_ORIGINS=<ip 1> <ip 2>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<your db name>
POSTGRES_USER=<your postgres user>
POSTGRES_PASSWORD=<your postgres password>
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=<your django secret token>
```

# Автор
[Корсунов Виктор](https://github.com/ViktorKors)
