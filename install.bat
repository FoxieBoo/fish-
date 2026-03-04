@echo off
echo Installing dependencies...

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.10+ and add to PATH
    pause
    exit /b 1
)

:: Install PyTorch (CPU version by default, change URL for CUDA)
echo Installing PyTorch (CPU)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

:: Install other dependencies
echo Installing other packages...
pip install -r requirements.txt

echo.
echo Installation complete!
echo Run "python main.py" or "start.bat" to launch
pause
