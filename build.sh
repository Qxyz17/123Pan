python -m pip install -r requirements.txt
python -m PyInstaller --onefile --windowed --icon=icon.ico --clean --exclude-module=PyQt5.QtWebEngine 123pan.py
