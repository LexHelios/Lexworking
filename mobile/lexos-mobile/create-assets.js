const fs = require('fs');
const path = require('path');

// Simple SVG icon
const iconSVG = `<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <rect width="1024" height="1024" fill="#000000"/>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#00ff00" stroke-width="40"/>
  <text x="512" y="580" font-family="Arial" font-size="300" font-weight="bold" fill="#00ff00" text-anchor="middle">LEX</text>
</svg>`;

// Simple splash screen SVG
const splashSVG = `<svg width="1284" height="2778" xmlns="http://www.w3.org/2000/svg">
  <rect width="1284" height="2778" fill="#000000"/>
  <text x="642" y="1400" font-family="Arial" font-size="200" font-weight="bold" fill="#00ff00" text-anchor="middle">LEX</text>
  <text x="642" y="1550" font-family="Arial" font-size="60" fill="#00ff00" text-anchor="middle">Loading...</text>
</svg>`;

// Save files
fs.writeFileSync(path.join(__dirname, 'assets', 'icon.svg'), iconSVG);
fs.writeFileSync(path.join(__dirname, 'assets', 'splash.svg'), splashSVG);

console.log('✅ Created SVG assets');
console.log('⚠️  Note: For production, convert these to PNG:');
console.log('   - icon.png (1024x1024)');
console.log('   - splash.png (1284x2778)');
console.log('   - adaptive-icon.png (1024x1024)');
console.log('');
console.log('You can use online tools like:');
console.log('   https://cloudconvert.com/svg-to-png');
console.log('   https://svgtopng.com/');