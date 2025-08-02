@echo off
echo 🔄 Updating LexOS Mobile to Expo SDK 53...
echo.
echo This will update all dependencies to work with the latest Expo Go app.
echo.

echo 1. Cleaning old dependencies...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json

echo.
echo 2. Installing new dependencies...
npm install

echo.
echo 3. Clearing Expo cache...
npx expo start -c

echo.
echo ✅ Update complete! The app should now work with the latest Expo Go.
echo.
pause