#!/bin/bash

echo "🚀 Building LexOS Mobile for Android..."

# Check if EAS CLI is installed
if ! command -v eas &> /dev/null; then
    echo "📦 Installing EAS CLI..."
    npm install -g eas-cli
fi

# Check if logged in to Expo
if ! eas whoami &> /dev/null; then
    echo "🔐 Please log in to your Expo account:"
    eas login
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create assets if they don't exist
if [ ! -d "assets" ]; then
    mkdir -p assets
    echo "📁 Created assets directory"
fi

# Generate placeholder assets if needed
if [ ! -f "assets/icon.png" ]; then
    echo "🎨 Creating placeholder icon..."
    # Create a simple icon using ImageMagick if available, otherwise use a placeholder
    if command -v convert &> /dev/null; then
        convert -size 1024x1024 xc:black \
                -fill '#00ff00' -draw "circle 512,512 512,100" \
                -fill '#00ff00' -font Arial -pointsize 400 \
                -gravity center -annotate +0+0 'LEX' \
                assets/icon.png
    else
        echo "⚠️  Please add an icon.png (1024x1024) to the assets folder"
    fi
fi

if [ ! -f "assets/splash.png" ]; then
    echo "🎨 Creating placeholder splash..."
    if command -v convert &> /dev/null; then
        convert -size 1284x2778 xc:black \
                -fill '#00ff00' -font Arial -pointsize 200 \
                -gravity center -annotate +0+0 'LEX' \
                assets/splash.png
    else
        echo "⚠️  Please add a splash.png (1284x2778) to the assets folder"
    fi
fi

if [ ! -f "assets/adaptive-icon.png" ]; then
    cp assets/icon.png assets/adaptive-icon.png 2>/dev/null || echo "⚠️  Please add adaptive-icon.png"
fi

# Build options
echo ""
echo "Select build type:"
echo "1) Development APK (for testing)"
echo "2) Production APK (optimized)"
echo "3) AAB for Play Store"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "🔨 Building development APK..."
        eas build --platform android --profile preview --local
        ;;
    2)
        echo "🔨 Building production APK..."
        eas build --platform android --profile preview --local --clear-cache
        ;;
    3)
        echo "🔨 Building AAB for Play Store..."
        eas build --platform android --profile production --local
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Build process started!"
echo "📱 Your APK will be available in the output directory when complete."
echo ""
echo "🔧 To install on your device:"
echo "   adb install <path-to-apk>"
echo "   or transfer the APK to your phone and install it"