@echo off
cd ../venv/Scripts
call activate
cd ../../The_Travelling_Therapist
py manage.py runserver
pause
