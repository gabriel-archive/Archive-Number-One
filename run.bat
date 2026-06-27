@echo off
title tetriz starter
echo press enter to start
pause >nul
echo running enjoy!
timeout /t 1 /nobreak >nul
cd Desktop/tetriz
py -3.12 tetriz.py
pause >nul