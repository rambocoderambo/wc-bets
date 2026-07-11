@echo off
cd /d "E:\AI llms\WC Bets"
start "" "C:\Users\m\AppData\Local\Programs\Python\Python311\python.exe" server.py
timeout /t 5 /nobreak >nul
start "" "http://localhost:5000"
