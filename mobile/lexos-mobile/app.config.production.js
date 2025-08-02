
import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "LexOS",
  slug: "lexos-mobile",
  version: "2.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "automatic",
  splash: {
    image: "./assets/splash.png",
    resizeMode: "contain",
    backgroundColor: "#000000"
  },
  assetBundlePatterns: [
    "**/*"
  ],
  ios: {
    supportsTablet: true,
    bundleIdentifier: "ai.lexos.mobile",
    buildNumber: "1",
    infoPlist: {
      NSCameraUsageDescription: "LexOS needs camera access for image analysis and document scanning",
      NSMicrophoneUsageDescription: "LexOS needs microphone access for voice commands and audio processing",
      NSPhotoLibraryUsageDescription: "LexOS needs photo library access to analyze and process your images",
      NSDocumentsFolderUsageDescription: "LexOS needs document access to help you manage and analyze files",
      ITSAppUsesNonExemptEncryption: false
    },
    config: {
      usesNonExemptEncryption: false
    },
    associatedDomains: [
      "applinks:lexos.ai",
      "applinks:api.lexos.ai"
    ]
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#000000"
    },
    package: "ai.lexos.mobile",
    versionCode: 1,
    permissions: [
      "android.permission.CAMERA",
      "android.permission.RECORD_AUDIO",
      "android.permission.READ_EXTERNAL_STORAGE",
      "android.permission.WRITE_EXTERNAL_STORAGE",
      "android.permission.INTERNET",
      "android.permission.ACCESS_NETWORK_STATE",
      "android.permission.WAKE_LOCK",
      "android.permission.VIBRATE"
    ],
    intentFilters: [
      {
        action: "VIEW",
        autoVerify: true,
        data: [
          {
            scheme: "https",
            host: "lexos.ai"
          },
          {
            scheme: "https", 
            host: "api.lexos.ai"
          }
        ],
        category: ["BROWSABLE", "DEFAULT"]
      }
    ]
  },
  web: {
    favicon: "./assets/favicon.png",
    bundler: "metro"
  },
  plugins: [
    "expo-router",
    [
      "expo-build-properties",
      {
        android: {
          enableProguardInReleaseBuilds: true,
          enableShrinkResourcesInReleaseBuilds: true,
          compileSdkVersion: 34,
          targetSdkVersion: 34,
          minSdkVersion: 24
        },
        ios: {
          deploymentTarget: "13.0"
        }
      }
    ],
    [
      "@sentry/react-native/expo",
      {
        organization: "lexos",
        project: "lexos-mobile",
        authToken: process.env.SENTRY_AUTH_TOKEN,
        url: "https://sentry.io/"
      }
    ],
    [
      "expo-notifications",
      {
        icon: "./assets/notification-icon.png",
        color: "#ffffff",
        sounds: ["./assets/notification.wav"]
      }
    ],
    [
      "expo-tracking-transparency",
      {
        userTrackingUsageDescription: "This identifier will be used to deliver personalized AI experiences and measure advertising effectiveness."
      }
    ]
  ],
  extra: {
    eas: {
      projectId: "your-eas-project-id"
    },
    apiUrl: process.env.EXPO_PUBLIC_API_URL || "https://api.lexos.ai",
    wsUrl: process.env.EXPO_PUBLIC_WS_URL || "wss://api.lexos.ai/ws",
    cdnUrl: process.env.EXPO_PUBLIC_CDN_URL || "https://cdn.lexos.ai",
    sentryDsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
    analyticsKey: process.env.EXPO_PUBLIC_ANALYTICS_KEY,
    environment: "production"
  },
  owner: "lexos-team",
  privacy: "public",
  updates: {
    url: "https://u.expo.dev/your-project-id"
  },
  runtimeVersion: {
    policy: "sdkVersion"
  }
});
