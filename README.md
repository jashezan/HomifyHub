# HomifyHub

HomifyHub is a web application that allows users to create and manage their products for sale. It is built with only Django and Bootstrap.

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/jashezan/HomifyHub.git
$ cd HomifyHub
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv .venv
$ source .venv/bin/activate
```

Then install the dependencies (poetry):

```sh
(.venv)$ pip install poetry
```

NB: (.venv) in the command above is the name of the virtual environment. It is assumed that the virtual environment is activated.

The project uses poetry for dependency management. To install the dependencies, run:

```sh
(.venv)$ poetry install
```

Once `poetry install` is run, the dependencies will be installed and a virtual environment will be created. The virtual environment will be located in the `.venv` directory.

## Running the project

To run the project, run the following command:

```sh
(.venv)$ poetry run start
```

The project will be available at `http://localhost:8000`.

If you see migrations errors, run the following command:

```sh
(.venv)$ poetry run migrate-db
```

This will apply the migrations to the database.

## Creating a superuser

To create a superuser, run the following command:

```sh
(.venv)$ poetry run superuser
```

This will prompt you to enter a username, email, and password for the superuser.

## About

The project is built with Django and Bootstrap. It is a simple web application that allows users to create and manage products for sale. The project is built with the following features:

- Product creation
- Product update
- Product deletion
- Product listing
