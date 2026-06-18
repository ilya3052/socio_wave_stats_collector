@echo off
cd /d "%~dp0..\..\"
call .venv\Scripts\activate.bat
python scheduled_collection.py %1 %2