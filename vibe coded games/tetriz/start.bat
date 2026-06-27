@echo off
title tetriz starter
echo press enter to start
pause >nul
cls
cd /d "%~dp0"
start py -3.12 tetriz.py
cls
echo game running, enjoy!
echo please do not close the second pop-up, or else the game will close.
pause >nul