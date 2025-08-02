
/**
 * Production Configuration for LexOS Mobile
 * Optimized for production deployment with H100 backend
 */

export const ProductionConfig = {
  // API Configuration
  api: {
    baseUrl: process.env.EXPO_PUBLIC_API_URL || 'https://api.lexos.ai',
    wsUrl: process.env.EXPO_PUBLIC_WS_URL || 'wss://api.lexos.ai/ws',
    cdnUrl: process.env.EXPO_PUBLIC_CDN_URL || 'https://cdn.lexos.ai',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
  },

  // Authentication
  auth: {
    tokenStorageKey: 'lexos_auth_token',
    refreshTokenKey: 'lexos_refresh_token',
    tokenExpiryBuffer: 300, // 5 minutes
    biometricPrompt: 'Use biometric authentication to access LexOS',
  },

  // Performance
  performance: {
    enableHermes: true,
    enableFlipper: false, // Disabled in production
    enableReactDevTools: false,
    maxConcurrentRequests: 10,
    requestQueueSize: 50,
    cacheSize: 100 * 1024 * 1024, // 100MB
    imageCacheSize: 50 * 1024 * 1024, // 50MB
  },

  // Offline Support
  offline: {
    enabled: true,
    maxStorageSize: 500 * 1024 * 1024, // 500MB
    syncInterval: 300000, // 5 minutes
    maxOfflineActions: 1000,
    compressionEnabled: true,
  },

  // AI Features
  ai: {
    maxContextLength: 8192, // Matches H100 backend config
    streamingEnabled: true,
    voiceEnabled: true,
    visionEnabled: true,
    maxImageSize: 10 * 1024 * 1024, // 10MB
    supportedImageFormats: ['jpg', 'jpeg', 'png', 'webp'],
    maxAudioDuration: 300, // 5 minutes
    supportedAudioFormats: ['mp3', 'wav', 'm4a'],
  },

  // Security
  security: {
    enableSSLPinning: true,
    certificateHashes: [
      // Add your production SSL certificate hashes
      'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
    ],
    enableJailbreakDetection: true,
    enableRootDetection: true,
    enableDebuggerDetection: true,
    enableTamperDetection: true,
    obfuscateApiKeys: true,
  },

  // Analytics & Monitoring
  analytics: {
    enabled: true,
    provider: 'mixpanel', // or 'amplitude', 'firebase'
    apiKey: process.env.EXPO_PUBLIC_ANALYTICS_KEY,
    trackingEnabled: true,
    crashReportingEnabled: true,
    performanceMonitoringEnabled: true,
    sessionTimeout: 1800000, // 30 minutes
  },

  // Error Reporting
  errorReporting: {
    enabled: true,
    sentryDsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
    environment: 'production',
    release: '2.0.0',
    enableNativeCrashHandling: true,
    enableJavaScriptErrorHandling: true,
    enablePromiseRejectionHandling: true,
    beforeSend: (event: any) => {
      // Filter sensitive data
      if (event.request?.headers?.authorization) {
        delete event.request.headers.authorization;
      }
      return event;
    },
  },

  // Push Notifications
  notifications: {
    enabled: true,
    channels: {
      default: {
        name: 'Default',
        importance: 'default',
        sound: true,
        vibrate: true,
      },
      ai_responses: {
        name: 'AI Responses',
        importance: 'high',
        sound: true,
        vibrate: true,
      },
      system_updates: {
        name: 'System Updates',
        importance: 'low',
        sound: false,
        vibrate: false,
      },
    },
  },

  // Feature Flags
  features: {
    voiceCommands: true,
    imageAnalysis: true,
    documentProcessing: true,
    offlineMode: true,
    darkMode: true,
    biometricAuth: true,
    pushNotifications: true,
    backgroundSync: true,
    advancedSettings: false, // Hidden in production
    debugMenu: false, // Disabled in production
  },

  // UI/UX
  ui: {
    theme: 'auto', // 'light', 'dark', 'auto'
    animations: {
      enabled: true,
      duration: 300,
      easing: 'ease-in-out',
    },
    haptics: {
      enabled: true,
      lightImpact: true,
      mediumImpact: true,
      heavyImpact: false, // Battery optimization
    },
    accessibility: {
      enabled: true,
      highContrast: false,
      largeText: false,
      reduceMotion: false,
    },
  },

  // Storage
  storage: {
    encryptionEnabled: true,
    compressionEnabled: true,
    maxCacheAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    cleanupInterval: 24 * 60 * 60 * 1000, // 24 hours
    maxLogSize: 10 * 1024 * 1024, // 10MB
    logRetentionDays: 7,
  },

  // Network
  network: {
    enableNetworkLogging: false, // Disabled in production
    enableRequestInterception: true,
    enableResponseCaching: true,
    cacheMaxAge: 3600, // 1 hour
    enableGzipCompression: true,
    enableHttps: true,
    enableHttp2: true,
  },

  // Development (disabled in production)
  development: {
    enableDevMenu: false,
    enableRemoteDebugging: false,
    enablePerformanceMonitor: false,
    enableNetworkInspector: false,
    enableReduxDevTools: false,
    logLevel: 'error', // Only log errors in production
  },

  // App Store / Play Store
  store: {
    appStoreId: 'your-app-store-id',
    playStoreId: 'ai.lexos.mobile',
    reviewPromptMinSessions: 10,
    reviewPromptMinDays: 7,
    updatePromptEnabled: true,
    forceUpdateMinVersion: '1.0.0',
  },

  // Legal & Compliance
  legal: {
    privacyPolicyUrl: 'https://lexos.ai/privacy',
    termsOfServiceUrl: 'https://lexos.ai/terms',
    supportUrl: 'https://lexos.ai/support',
    contactEmail: 'support@lexos.ai',
    gdprCompliant: true,
    ccpaCompliant: true,
  },
};

export default ProductionConfig;
