#!/usr/bin/env powershell
# Quick commands for running tests and generating allure reports

# Run all tests
Write-Host "Running all tests..." -ForegroundColor Green
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Generate allure report
Write-Host "Generating Allure report..." -ForegroundColor Green
.\.venv\Scripts\python.exe generate_allure_report.py

Write-Host "Done! Report is open in your browser." -ForegroundColor Cyan
