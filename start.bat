@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
set PYTHONIOENCODING=UTF-8
python -m streamlit run frontend\app.py
