@echo off
echo Instalando dependencias de Python...
pip install -r requirements.txt

echo Instalando Node.js dependencies...
npm install -g appium
appium driver install uiautomator2

echo Verificando instalacion...
appium driver list --installed

echo.
echo Instalacion completa!
echo Para ejecutar el bot:
echo 1. Inicia el emulador Android
echo 2. Ejecuta: appium --port 4701 --base-path /wd/hub
echo 3. En otra terminal: python app,py