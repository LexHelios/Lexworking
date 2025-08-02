@echo off
echo 🚀 Building LexOS Mobile for Android...

:: Check if EAS CLI is installed
where eas >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing EAS CLI...
    npm install -g eas-cli
)

:: Check if logged in to Expo
eas whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please log in to your Expo account:
    eas login
)

:: Install dependencies
echo 📦 Installing dependencies...
npm install

:: Create assets directory
if not exist "assets" (
    mkdir assets
    echo 📁 Created assets directory
)

:: Build options
echo.
echo Select build type:
echo 1) Development APK (for testing)
echo 2) Production APK (optimized)
echo 3) AAB for Play Store
set /p choice="Enter choice [1-3]: "

if "%choice%"=="1" (
    echo 🔨 Building development APK...
    eas build --platform android --profile preview --local
) else if "%choice%"=="2" (
    echo 🔨 Building production APK...
    eas build --platform android --profile preview --local --clear-cache
) else if "%choice%"=="3" (
    echo 🔨 Building AAB for Play Store...
    eas build --platform android --profile production --local
) else (
    echo ❌ Invalid choice
    exit /b 1
)

echo.
echo ✅ Build process started!
echo 📱 Your APK will be available in the output directory when complete.
echo.
echo 🔧 To install on your device:
echo    adb install ^<path-to-apk^>
echo    or transfer the APK to your phone and install it
pause