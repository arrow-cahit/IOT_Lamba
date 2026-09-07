@echo off
title IOT Lamba Kontrol Sunucusu
cd /d "%~dp0"
echo ===================================================
echo     IOT Lamba Kontrol Sunucusu Baslatiliyor...
echo ===================================================
start "" "http://localhost:8000"
python server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Sunucu baslatilamadi! Python'un yuklu oldugundan emin olun.
    pause
)
