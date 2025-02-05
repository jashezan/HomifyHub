"""_summary_
"""
import sys
import os

def start_server():
    """
    start the server
    """
    python = sys.executable # get the python executable path
    os.system(f"{python} manage.py runserver")

def migrate_db():
    """
    migrate the database
    """
    python = sys.executable # get the python executable path
    os.system(f"{python} manage.py makemigrations")
    os.system(f"{python} manage.py migrate")

def create_super_user():
    """
    create super user
    """
    python = sys.executable # get the python executable path
    os.system(f"{python} manage.py createsuperuser")

def create_app():
    """
    create a new app
    """
    app_name = input("Enter the app name: ")
    python = sys.executable # get the python executable path
    os.system(f"{python} manage.py startapp {app_name}")
