@echo off
cd ./venv/Scripts
call activate
cd ../../
py manage.py runserver
pause
