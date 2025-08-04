/**
 * Configuration Module Exports
 *
 * Centralized exports for all configuration-related utilities,
 * hooks, and components for easy importing throughout the application.
 */

// Core configuration fetching utilities
export {
  clearConfigCache,
  defaultConfig,
  fetchBrandingConfig,
  fetchConfigSection,
  fetchFeaturesConfig,
  fetchFullConfig,
  getConfigWithFallback,
  notifyConfigUpdate,
  refreshConfig,
  setupConfigListener,
} from "./fetchConfig";

export type { BrandingConfig, Config, FeaturesConfig } from "./fetchConfig";

// React hooks
export {
  useBrandingConfig,
  useConfig,
  useConfigManager,
  useConfigProvider,
  useConfigSection,
  useFeatureFlags,
  useFeaturesConfig,
  useTheme,
} from "./useConfig";

// Context provider and related components
export {
  ConfigLoader,
  ConfigProvider,
  FeatureGate,
  ThemeWrapper,
  useAPIConfig,
  useAppConfig,
  useConfigContext,
  useDatabaseConfig,
  useLoggingConfig,
  useNotificationConfig,
  useSecurityConfig,
  withConfig,
} from "./ConfigProvider";
