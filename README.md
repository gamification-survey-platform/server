# Gamification Platform

This project aims to provide a platform where students can give feedback to
their classmates' presentation assignments, with specially designed gamification
elements to encourage students' engagement. It is based on Django 3.2 and
PostgreSQL server database.
You can access the application here https://gamification-client.onrender.com/.

# Developer Environment Setup with Docker

1. Download and install docker from https://www.docker.com

2. Add a `.env` file at the project directory (the same level as `manage.py`)
   with the following environment variables:

   ```
   SECRET_KEY='django-insecure-2-mg5vw^&skma(kxqan1_7^2acwc74pb54g6&ea&&a=0g=!!0g'
   DEBUG=True
   ALLOWED_HOSTS='localhost 127.0.0.1'
   DB_ENGINE='django.db.backends.postgresql'
   DB_NAME='dev'
   DB_USER='dbuser'
   DB_PASSWORD='dbuser'
   DB_PORT='5432'
   DB_HOST='db'
   ``` 

   For more information about these environment variables, please go to step 4 in `Developer Environment Setup without Docker`

3. Open a terminal and navigate to the same directory(where .env and readme file located)

3. run `docker-compose up --build`

4. You are good to go

Note: If you want to shut down the container, please first stop all containers that are running (with Ctrl-C) and run `docker-compose down`. With the current docker configuration, everytime you restart the database container, the database will be refreshed

# Developer Environment Setup without Docker

1. Install required python packages

   It is suggested to create a brand-new virtual environment then `pip install -r requirements.txt`.

2. Install PostgreSQL server locally

   Follow the instructions [here](https://www.postgresql.org/download/) to
   install PostgreSQL compatible with your platform. PostgreSQL server's
   version should be >= 9.6, as is required by Django 3.2.

3. Configure PostgreSQL server

   - Start PostgreSQL server

     Follow the instructions [here](https://tableplus.com/blog/2018/10/how-to-start-stop-restart-postgresql-server.html)
     to start the local postgres server.

   - Create a database `dev`

     Run `sudo -u postgres psql` to get into psql shell as `postgres` user.
     Then execute the following SQL statement to add a new database called `dev`.

     ```sql
     CREATE DATABASE dev;
     ```

     You can view all available psql commands by tying `\?`. Some common commands are:

     - `\l`: list all databases;
     - `\c <DATABASE_NAME>`: connect to a database;
     - `\dt`: list all tables in current database;
     - `\d <TABLE_NAME>`: describe table info;
     - `\q`: quit the shell;

   - Add a user `dbuser`

     Run `sudo -u postgres psql` to get into psql shell. Then execute the
     following SQL statements to add a user named `dbuser` with password as
     `dbuser`, and grant all privileges on table `dev` to `dbuser`.

     ````sql
     CREATE USER dbuser WITH PASSWORD 'dbuser';
     GRANT ALL PRIVILEGES ON DATABASE dev TO dbuser;
     ```python manage.py makemigrations

     Afterwards, you can modify a few of the connection parameters for the
     `dbuser` you just created. This will speed up database operations so that
     the correct values do not have to be queried and set each time a
     connection is established.

     ```sql
     ALTER ROLE dbuser SET client_encoding TO 'utf8';
     ALTER ROLE dbuser SET default_transaction_isolation TO 'read committed';
     ALTER ROLE dbuser SET timezone TO 'US/Pacific';
     ````

     After creating new user `dbuser`, we can login into psql shell as this
     new user with command `psql -h localhost -d dev -U dbuser` and then enter
     the password.

4. Configure environment variables

   Add a `.env` file at the project directory (the same level as `manage.py`)
   with the following environment variables:

   ```
   SECRET_KEY='django-insecure-2-mg5vw^&skma(kxqan1_7^2acwc74pb54g6&ea&&a=0g=!!0g'
   DEBUG=True
   ALLOWED_HOSTS='localhost 127.0.0.1'
   DB_ENGINE='django.db.backends.postgresql'
   DB_NAME='dev'
   DB_USER='dbuser'
   DB_PASSWORD='dbuser'
   DB_PORT='5432'
   DB_HOST='localhost'
   ```

   > In production environment,
   >
   > - `SECRET_KEY` should be kept as a real secret and not exposed to users.
   > - `DEBUG` should be set to `False`.
   > - `ALLOWED_HOSTS` should be added with the IP address or the domain name
   >   of the production server.
   > - `DATABASE_URL` should be the external IP address from the Hosting server.
   You can also customize your environment by setting different database related
   variables like:

   - `DB_ENGINE`: default to `django.db.backends.postgresql`, the engine of the database
   - `DB_NAME`: default to `dev`, the name of the database
   - `DB_USER`: default to `dbuser`, the username used to access the database
   - `DB_PASSWORD`: default to `dbuser`, the password for `DB_USER`
   - `DB_HOST`: default to `localhost`, the host for the database
   - `DB_PORT`: default to `5432`, the port where MySQL server is on
   - `USE_S3`: default to 'False', whether upload files to AWS


These are already set in the default application.

1. Test if everything is working

   Run command `python manage.py runserver`

2. Install fixtures

   - load data for dev env: `python manage.py loaddata app/gamification/fixtures/initial_data_dev.json --app app.model_name`
   - load data for prd env: `python manage.py loaddata app/gamification/fixtures/initial_data_prod.json --app app.model_name`

3. Django Migration

   After each time you make changes on the models, migrate the database run : `python manage.py makemigrations` (make migration) `python manage.py migrate` (migrate the database to the new changes)

# How to Run

After setting up the environment, export following environment variables by creating a `.env` file in the root directory of the project.

```python
'''You should be given access-key and secret-key from whoever is managing the aws account for the gamification. If you want to create a new developer role to access it, follow those steps:`
- Login the AWS account -> IAM -> User -> Add users -> Attach policies directly/Copy permissions -> click your username -> Security credentials -> Create access key
'''
AWS_ACCESS_KEY_ID="<Access Key Id>"
AWS_SECRET_ACCESS_KEY="<Secret Key Id>"
AWS_REGION_NAME="us-west-1"
AWS_STORAGE_BUCKET_NAME_PROD="aws-gamification-platform"
AWS_STORAGE_BUCKET_NAME_DEV="aws-gamification-platform-dev"
```

run `python manage.py runserver` to start the server.

# Contributing

## Pull requests and branches

There will be mainly 3 types of branches while developing:

- `main`: Always be deployable and the most stable version. Never commit directly
  on `main` branch. All code changes on `main` should come from merging
  with pull requests.
- `dev`: The branch for evolving the development. Once a major set of features
  has been implemented, a version tag like `x.0.0` will be added, and this
  branch will be merged into `main` for release.
- `{new_feat}`: A type of branch for developing different features. Whenever a
  new feature is to be developed, checkout a feature branch from `dev`,
  name it after the feature description, and write code on that branch.
  After finishing developing, merge this branch into `dev`.

Developers are free to add as many `{new_feat}` branches as needed, but code
changes in `dev` and `main` branch should always be done through pull requests
and code reviews.

## Python formatter

We use `flake8` in conjuction with `black` and `isort` to format our code.

## Commit message convention

The commit message should be structured as follows, quoted from [here](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(optional scope): <description>

[optional body]

[optional footer(s)]
```

The types are specified as followed:

- **fix**: patches a bug in the codebase.
- **feat**: introduces a new feature to the codebase.
- **style**: codebase changes related to code format problems
- **test**: add test code
- **doc**
- **chore**
- **refactor**
- ......

## Commit as often as possible

Break down the code you implemented into small parts and commit as soon as you
finish a small part.

**DO NOT** squash all the work into one commit!

## Multiple authors for a commit

If there are multiple authors for a commit (for example, pair-programming), follow the instructions from this
[link](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors#creating-co-authored-commits-on-the-command-line)
here to add co-authors.
