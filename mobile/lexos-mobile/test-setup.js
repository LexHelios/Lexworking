/**
 * Test script to verify LexOS Mobile setup
 */
const fs = require('fs');
const path = require('path');

console.log('🔍 Checking LexOS Mobile setup...\n');

// Check required files
const requiredFiles = [
  'package.json',
  'App.js',
  'app.json',
  'eas.json',
  'src/services/LexService.js',
  'src/utils/AudioUtils.js',
  'src/components/VoiceVisualizer.js'
];

let allFilesExist = true;

console.log('📁 Checking required files:');
requiredFiles.forEach(file => {
  const exists = fs.existsSync(path.join(__dirname, file));
  console.log(`   ${exists ? '✅' : '❌'} ${file}`);
  if (!exists) allFilesExist = false;
});

console.log('\n📦 Checking dependencies:');
try {
  const packageJson = require('./package.json');
  const requiredDeps = [
    'expo',
    'expo-av',
    'expo-speech',
    'react',
    'react-native',
    '@react-native-async-storage/async-storage'
  ];
  
  requiredDeps.forEach(dep => {
    const installed = packageJson.dependencies[dep] || packageJson.devDependencies[dep];
    console.log(`   ${installed ? '✅' : '❌'} ${dep} ${installed || 'NOT FOUND'}`);
  });
} catch (error) {
  console.log('   ❌ Could not read package.json');
}

console.log('\n🎨 Checking assets:');
const assetFiles = ['icon.png', 'splash.png', 'adaptive-icon.png'];
assetFiles.forEach(file => {
  const exists = fs.existsSync(path.join(__dirname, 'assets', file));
  console.log(`   ${exists ? '✅' : '⚠️'} assets/${file} ${exists ? '' : '(will use placeholder)'}`);
});

console.log('\n📱 Platform Info:');
console.log(`   Node.js: ${process.version}`);
console.log(`   Platform: ${process.platform}`);
console.log(`   Current Directory: ${__dirname}`);

if (allFilesExist) {
  console.log('\n✅ Setup looks good! You can now:');
  console.log('   1. Run "npm install" to install dependencies');
  console.log('   2. Run "npm start" to start the development server');
  console.log('   3. Run "npm run android" to launch on Android');
  console.log('   4. Run build-android.bat/.sh to build APK');
} else {
  console.log('\n❌ Some files are missing. Please check the setup.');
}

console.log('\n💡 Tips:');
console.log('   - Make sure you have Expo CLI installed globally');
console.log('   - For building APKs, install EAS CLI: npm install -g eas-cli');
console.log('   - Add your Alibaba Cloud API key in the app settings');
console.log('   - Connect to your LexOS server for enhanced features');