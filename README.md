[![Main Kittygram workflow](https://github.com/ViktorKors/kittygram_final/actions/workflows/main.yml/badge.svg)](https://github.com/ViktorKors/kittygram_final/actions/workflows/main.yml)

# Описание проекта
Foodgram - это онлайн-сервис, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии:
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)


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
