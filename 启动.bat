@echo off
title VRChat Auto Fish
cd /d "%~dp0"

:: ============================================
::  Check Python
:: ============================================
python --version >nul 2>&1
if errorlevel 1 (
    echo ============================================
    echo   [ERROR] Python not found.
    echo   Please install Python 3.10+ and check "Add to PATH"
    echo   Download: https://www.python.org/downloads/
    echo ============================================
    pause
    exit /b 1
)

:: ============================================
::  Check if dependencies are installed
:: ============================================
python -c "import cv2, keyboard, torch, ultralytics" 2>nul
if errorlevel 1 (
    echo ============================================
    echo   First run detected, installing dependencies...
    echo   (This only runs once, please wait)
    echo ============================================
    echo.
    call :install_deps
    if errorlevel 1 (
        echo [ERROR] Install failed. Check your network and try again.
        pause
        exit /b 1
    )
    echo.
    echo ============================================
    echo   Dependencies installed, launching app...
    echo ============================================
    echo.
)

:: ============================================
::  Launch
:: ============================================
python main.py
if errorlevel 1 pause
exit /b 0

:: ============================================
::  Install subroutine
:: ============================================
:install_deps
echo.
echo [1/2] Installing PyTorch...
call :install_torch

echo.
echo [2/2] Installing other dependencies...
pip install -r requirements.txt
if errorlevel 1 exit /b 1
exit /b 0

:install_torch
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo   No NVIDIA GPU detected, installing CPU version of PyTorch
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
) else (
    echo   NVIDIA GPU detected, installing CUDA version of PyTorch (GPU acceleration)
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
)
exit /b 0
