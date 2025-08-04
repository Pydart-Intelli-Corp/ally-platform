/**
 * React Hooks for Configuration Management
 *
 * Provides React hooks for loading and managing configuration data
 * with automatic updates, error handling, and loading states.
 */

"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  BrandingConfig,
  clearConfigCache,
  Config,
  defaultConfig,
  FeaturesConfig,
  fetchBrandingConfig,
  fetchConfigSection,
  fetchFeaturesConfig,
  fetchFullConfig,
  getConfigWithFallback,
  notifyConfigUpdate,
  refreshConfig,
  setupConfigListener,
} from "./fetchConfig";

// Hook state interfaces
interface ConfigState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

interface UseConfigOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  fallback?: boolean;
  onError?: (error: string) => void;
}

// Generic configuration hook
function useConfigData<T>(
  fetchFunction: (useCache?: boolean) => Promise<T>,
  fallbackData?: T,
  options: UseConfigOptions = {}
): ConfigState<T> & { refresh: () => Promise<void> } {
  const {
    autoRefresh = false,
    refreshInterval = 5 * 60 * 1000, // 5 minutes
    fallback = true,
    onError,
  } = options;

  const [state, setState] = useState<ConfigState<T>>({
    data: null,
    loading: true,
    error: null,
    lastUpdated: null,
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountedRef = useRef(true);

  const loadConfig = useCallback(
    async (useCache = true) => {
      if (!mountedRef.current) return;

      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        let data: T;

        if (fallback && fallbackData) {
          data = await getConfigWithFallback(
            fetchFunction(useCache),
            fallbackData
          );
        } else {
          data = await fetchFunction(useCache);
        }

        if (mountedRef.current) {
          setState({
            data,
            loading: false,
            error: null,
            lastUpdated: new Date(),
          });
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "Unknown error";

        if (mountedRef.current) {
          setState((prev) => ({
            ...prev,
            loading: false,
            error: errorMessage,
          }));
        }

        if (onError) {
          onError(errorMessage);
        }
      }
    },
    [fetchFunction, fallbackData, fallback, onError]
  );

  const refresh = useCallback(async () => {
    await loadConfig(false);
  }, [loadConfig]);

  // Initial load
  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  // Auto-refresh setup
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      intervalRef.current = setInterval(() => {
        loadConfig();
      }, refreshInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [autoRefresh, refreshInterval, loadConfig]);

  // Setup cross-tab config listener
  useEffect(() => {
    setupConfigListener();

    const handleStorageChange = () => {
      loadConfig(false);
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [loadConfig]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { ...state, refresh };
}

// Specific configuration hooks
export function useConfig(options: UseConfigOptions = {}) {
  return useConfigData(fetchFullConfig, defaultConfig as Config, options);
}

export function useBrandingConfig(options: UseConfigOptions = {}) {
  return useConfigData(
    fetchBrandingConfig,
    defaultConfig.branding as BrandingConfig,
    options
  );
}

export function useFeaturesConfig(options: UseConfigOptions = {}) {
  return useConfigData(
    fetchFeaturesConfig,
    defaultConfig.features as FeaturesConfig,
    options
  );
}

export function useConfigSection(
  section: string,
  options: UseConfigOptions = {}
) {
  const fetchSection = useCallback(
    (useCache = true) => fetchConfigSection(section, useCache),
    [section]
  );

  return useConfigData(fetchSection, undefined, options);
}

// Configuration management hooks
export function useConfigManager() {
  const [refreshing, setRefreshing] = useState(false);

  const refreshAllConfigs = useCallback(async () => {
    setRefreshing(true);
    try {
      await refreshConfig();
      notifyConfigUpdate();
    } catch (error) {
      console.error("Failed to refresh configs:", error);
    } finally {
      setRefreshing(false);
    }
  }, []);

  const clearCache = useCallback(() => {
    clearConfigCache();
    notifyConfigUpdate();
  }, []);

  return {
    refreshing,
    refreshAllConfigs,
    clearCache,
  };
}

// Configuration provider hook for context
export function useConfigProvider() {
  const fullConfig = useConfig({ autoRefresh: true });
  const branding = useBrandingConfig({ autoRefresh: true });
  const features = useFeaturesConfig({ autoRefresh: true });
  const manager = useConfigManager();

  return {
    config: fullConfig,
    branding,
    features,
    manager,
    isLoading: fullConfig.loading || branding.loading || features.loading,
    hasError: Boolean(fullConfig.error || branding.error || features.error),
    errors: {
      config: fullConfig.error,
      branding: branding.error,
      features: features.error,
    },
  };
}

// Theme management hook
export function useTheme() {
  const { data: branding, loading, error } = useBrandingConfig();

  const theme = useMemo(() => {
    return branding
      ? {
          primaryColor: branding.primary_color,
          secondaryColor: branding.secondary_color,
          mode: branding.theme,
        }
      : null;
  }, [branding]);

  const applyTheme = useCallback(() => {
    if (theme && typeof document !== "undefined") {
      const root = document.documentElement;
      root.style.setProperty("--primary-color", theme.primaryColor);
      root.style.setProperty("--secondary-color", theme.secondaryColor);
      root.setAttribute("data-theme", theme.mode);
    }
  }, [theme]);

  useEffect(() => {
    applyTheme();
  }, [applyTheme]);

  return {
    theme,
    loading,
    error,
    applyTheme,
  };
}

// Feature flags hook
export function useFeatureFlags() {
  const { data: features, loading, error } = useFeaturesConfig();

  const isFeatureEnabled = useCallback(
    (feature: keyof FeaturesConfig): boolean => {
      return features ? features[feature] : false;
    },
    [features]
  );

  return {
    features,
    loading,
    error,
    isFeatureEnabled,
  };
}
