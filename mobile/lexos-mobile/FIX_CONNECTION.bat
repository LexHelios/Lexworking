@echo off
echo 🔧 Fixing Expo Connection Issues...
echo.

echo 1. Checking if phone and PC are on same network...
echo    Your PC IP: 192.168.50.155
echo    Your phone should be on network: 192.168.50.x
echo.

echo 2. Restarting Expo with tunnel mode (works across networks)...
echo.
echo Press Ctrl+C to stop current server, then press any key to continue...
pause

npx expo start --tunnel

echo.
echo 📱 This will create a public URL that works from any network!
echo    Just scan the new QR code with Expo Go app.