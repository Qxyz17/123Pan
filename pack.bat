@echo off
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --icon=icon.ico -F android.py

python -m PyInstaller -F web.py