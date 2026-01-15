@echo off
setlocal

echo ================================
echo Creating / Activating venv
echo ================================
py -3.10 -m venv venv
call venv\Scripts\activate

echo ================================
echo Installing Python dependencies
echo ================================
venv\Scripts\python -m pip install -r requirements.txt|| exit /b

echo ================================
echo Building Frontend
echo ================================
call npm --prefix frontend run build || exit /b

echo ================================
echo Running PyInstaller
echo ================================
venv\Scripts\python -m PyInstaller --distpath "./executables" app.spec || exit /b

echo ================================
echo Cleaning build folders
echo ================================
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo ================================
echo BUILD COMPLETED SUCCESSFULLY
echo ================================
pause
