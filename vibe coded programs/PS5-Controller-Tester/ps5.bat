@echo off
title ps 5 controller tester starter
echo press enter to start
pause >nul
cls
cd /d "%~dp0"
start py -3.12 main.py
cls
echo app running, enjoy!
echo please do not close the second pop-up, or else the app will close.
pause >nul