python -m pip install -r requirements.txt
python -m PyInstaller --onefile --icon=icon.ico -F android.py
python -m pyinstaller -F web.py
