# Gamification Platform

This project aims to provide a platform where students can give feedback to 
their classmates' presentation assignments, with specially designed gamification 
elements to encourage students' engagement. It is based on Django 3.2 and
PostgreSQL server database.

# Developer Environment Setup

1. Install required python packages

    It is suggested to create a brand-new virtual environment then `pip install -r requirements.txt`.
   
    > **Deprecated**
    > 
    > For Mac users, replace `mysqlclient==2.1.0` with `PyMySQL==1.0.2` in `requirements.txt` file. Then add the following lines to `config/__init__.py`
    >
    > ```python
    > import pymysql
    > pymysql.install_as_MySQLdb()
    > ```
    >
    > > Note: Don't forget to add `config/__init__.py` to your local 'ignore' file
    > > list so as not to mess up the repo. Follow instructions in this [link](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files#excluding-local-files-without-creating-a-gitignore-file)
    > > for how to ignore files locally.
    >
    > > What we are doing here is essentially changing the [MySQL driver](https://docs.djangoproject.com/en/3.2/ref/databases/#mysql-db-api-drivers) for Django,
    > since `mysqlclient` seems to have some compatiblity issues on Mac while [`PyMySQL`](https://pypi.org/project/PyMySQL/)
    > is purely based on Python and will work on any platform. But `mysqlclient` is
    > officially supported by Django in this [list](https://docs.djangoproject.com/en/3.2/ref/databases/#mysql-db-api-drivers), so we will stick with it on other platforms.

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

      ```sql
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
      ```

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
    ```

    > In production environment,
    > - `SECRET_KEY` should be kept as a real secret and not exposed to users.
    > - `DEBUG` should be set to `False`.
    > - `ALLOWED_HOSTS` should be added with the IP address or the domain name 
    > of the production server.
    
    You can also customize your environment by setting different database related
    variables like:
    - `DB_NAME`: default to `dev`, the name of the database
    - `DB_USER`: default to `dbuser`, the username used to access the database
    - `DB_PASSWORD`: default to `dbuser`, the password for `DB_USER`
    - `DB_HOST`: default to `localhost`, the host for the database
    - `DB_PORT`: default to `3306`, the port where MySQL server is on

5. Test if everything is working

    Run command `python manage.py runserver`

6. Install fixtures

    Run command `python manage.py loaddata assignments courses entities membership registration survey users artifact constraint rule rule_constraint`
    
7. Django Migration 
    
    After each time you make changes on the models, migrate the database run : `python manage.py makemigrations` (make migration) `python manage.py migrate` (migrate the database to the new changes)  

# How to Run

After setting up the environment, run `python manage.py runserver` to start the server. Here are a few pages implemented at the moment:

- Sign in page `127.0.0.1:8000/signin/`

  The sign in page is where you input your andrew ID and password to login into
  the system. If the andrew ID doesn't exist or the password is incorrect, an
  error message will be displayed to ask you to enter again. \
  After successful sign in, you will be redirected to your profile page.

- Sign up page `127.0.0.1:8000/signup/`

  The sign up page is where you register an account. You will be asked to enter
  your andrew ID (required), email (required), password (required), and enter
  the password one more time for confirmation. The password should be at least
  8 characters, irrelavant to your personal information (andrew ID or email),
  not too common or entirely numeric. If any of the field above doesn't meet the
  requirement, you will be asked to input the information again. \
  After successful sign up, you will be redirected to your profile page.

- Profile page `127.0.0.1:8000/profile/`

  The profile page is where you can view your personal information. You can edit
  your account information (andrew ID, email address, first name, last name and
  profile image) by filling in the form on this page. Currently, only the 'edit'
  tab is clickable and all other tabs are not implemented yet.

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

We use `autopep8` to format our code. Properly set your IDE to automatically 
format the python file before saving.

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
