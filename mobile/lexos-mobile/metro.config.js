
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Production optimizations
config.transformer = {
  ...config.transformer,
  minifierConfig: {
    // Terser options for production builds
    mangle: {
      keep_fnames: true,
    },
    compress: {
      drop_console: true, // Remove console.log in production
      drop_debugger: true,
      pure_funcs: ['console.log', 'console.info', 'console.debug'],
    },
  },
};

// Enable Hermes for better performance
config.resolver = {
  ...config.resolver,
  alias: {
    '@': './src',
    '@components': './src/components',
    '@services': './src/services',
    '@config': './src/config',
    '@utils': './src/utils',
    '@types': './src/types',
    '@assets': './assets',
  },
};

// Asset optimization
config.transformer.assetPlugins = ['expo-asset/tools/hashAssetFiles'];

module.exports = config;
