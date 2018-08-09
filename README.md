# MyDiary
[![Maintainability](https://api.codeclimate.com/v1/badges/80c510abc272da1fe69d/maintainability)](https://codeclimate.com/github/flacode/my_diary/maintainability)
[![Build Status](https://travis-ci.org/flacode/my_diary.svg?branch=develop)](https://travis-ci.org/flacode/my_diary)
[![Coverage Status](https://coveralls.io/repos/github/flacode/my_diary/badge.svg?branch=develop)](https://coveralls.io/github/flacode/my_diary?branch=develop)

>  MyDiary is an online journal where users can pen down their thoughts and feelings.

My Diary is an API developed using the Django Rest Framework.

## Supported features.
pass

## Technologies used.
- Django Rest Framework.
- Postgres database.

## Getting started.
### Prerequisites
1. Install requirements, run
```sh
     pip install -r requirements.txt
```
2. Database configuration.
   - Download and install postgres from [here](https://www.postgresql.org/download/)
   - Create database in terminal
   ```sh
      $ psql postgres;
      $ CREATE DATABASE database_name;
   ```
3. Set the required environment variables.
    - Add a configuration file called `config.txt` where you will set the enviromnent variables.
        ```export SECRET_KEY='secret key'
            export DATABASE_URL='postgres://USER:PASSWORD@HOST:PORT/NAME'
            export EMAIL_HOST='email host'
            export EMAIL_PORT=465
            export EMAIL_HOST_USER='email host user'
            export EMAIL_HOST_PASSWORD='email host '
            export EMAIL_USE_TLS=True
        ```


   - Set these environment variables using the following command.
   ```sh
      $ source ./config.txt
   ```

3. Switch to the project's root directory and run migrations to create database tables.
```sh
    $ python manage.py makemigrations
    $ python manage.py migrate
 ```
 4. Then run the application.
 ```sh
    $ python manage.py runserver
 ```

## Tests
pass
