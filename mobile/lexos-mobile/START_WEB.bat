@echo off
echo 🌐 Starting LexOS Mobile in Web Browser...
echo.
echo ⚠️  Limited features in web mode:
echo    ✅ Text chat will work
echo    ❌ Voice features disabled
echo    ❌ TTS disabled
echo.
cd /d "C:\Users\Vince\Documents\lexos-core\lexcommand-shadow-autonomy\lexworking\mobile\lexos-mobile"
set BROWSER=chrome
npm start -- --web