@echo off
title Requirement Intelligence - Streamlit

cd /d "%~dp0"

echo ==========================================
echo   Requirement Intelligence
echo   Starting Streamlit application...
echo ==========================================
echo.

python -m streamlit run app.py

pause
