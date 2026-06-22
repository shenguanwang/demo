@echo off
chcp 65001 >nul
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "chrome://extensions/"
start "" explorer.exe "C:\Users\sss\Documents\网站解析\chrome-social-capture"
echo.
echo 1. 在Chrome扩展页面开启右上角“开发者模式”
echo 2. 点击“加载已解压的扩展程序”
echo 3. 选择已经打开的 chrome-social-capture 文件夹
echo 4. 将“海外获客页面采集器”固定到Chrome工具栏
echo.
pause
