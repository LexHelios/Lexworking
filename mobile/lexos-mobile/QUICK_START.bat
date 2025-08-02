@echo off
cls
echo ╔════════════════════════════════════════════════╗
echo ║         LexOS Mobile - Quick Start Guide       ║
echo ╚════════════════════════════════════════════════╝
echo.
echo 🚀 Choose an option:
echo.
echo   1. Test on Phone (with Expo Go app)
echo   2. Build APK (takes 15-20 minutes)
echo   3. Check setup status
echo   4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto test_phone
if "%choice%"=="2" goto build_apk
if "%choice%"=="3" goto check_setup
if "%choice%"=="4" exit
goto :eof

:test_phone
echo.
echo 📱 Starting development server...
echo.
echo Instructions:
echo 1. Install "Expo Go" from Play Store on your phone
echo 2. Make sure phone and PC are on same WiFi
echo 3. Scan the QR code with Expo Go app
echo.
npm start
goto :eof

:build_apk
echo.
echo 🔨 Building APK...
echo.
if not exist "node_modules\eas-cli" (
    echo Installing EAS CLI...
    npm install -g eas-cli
)
echo.
echo Please log in to Expo (skip if already logged in):
eas whoami >nul 2>&1
if %errorlevel% neq 0 (
    eas login
)
echo.
call build-android.bat
goto :eof

:check_setup
echo.
echo 🔍 Checking setup...
echo.
node test-setup.js
echo.
pause
goto :eof