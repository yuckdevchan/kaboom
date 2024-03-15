rm -rf dist
pyinstaller --onefile --noconsole --icon=logo.png --add-data "logo.png;." --add-data "config.toml;." main.py
mv dist\main.exe dist\kaboom.exe
cp logo.png dist\logo.png
cp config.toml dist\config.toml