@echo off
REM Run the FastAPI server with proper Python environment setup for Windows
cd /d "%~dp0"
python -m uvicorn main:app --reload --port 8000
