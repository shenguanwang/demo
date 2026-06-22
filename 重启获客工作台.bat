@echo off
chcp 65001 >nul
for /f "tokens=5" %%p in ('netstat -ano ^| findstr "127.0.0.1:8815" ^| findstr "LISTENING"') do (
  taskkill /PID %%p /F >nul 2>nul
)
timeout /t 1 /nobreak >nul
start "" /min python "C:\Users\sss\Documents\网站解析\server.py"
timeout /t 2 /nobreak >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "http://127.0.0.1:8815/index.html#lead-finder"
