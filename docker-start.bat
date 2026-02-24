@echo off
echo ========================================
echo   Mimanasa Backend - Docker Setup
echo ========================================
echo.

echo Building Docker image...
docker-compose build

echo.
echo Starting container...
docker-compose up

pause
