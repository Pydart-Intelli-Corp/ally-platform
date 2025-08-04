/**
 * Configuration Context Provider
 *
 * Provides configuration data throughout the React application
 * using React Context API with automatic updates and error handling.
 */

"use client";

import React, { createContext, ReactNode, useContext } from "react";
import { BrandingConfig, Config, FeaturesConfig } from "./fetchConfig";
import { useConfigProvider } from "./useConfig";

// Context interfaces
interface ConfigContextValue {
  // Configuration data
  config: {
    data: Config | null;
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
    refresh: () => Promise<void>;
  };
  branding: {
    data: BrandingConfig | null;
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
    refresh: () => Promise<void>;
  };
  features: {
    data: FeaturesConfig | null;
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
    refresh: () => Promise<void>;
  };

  // Manager functions
  manager: {
    refreshing: boolean;
    refreshAllConfigs: () => Promise<void>;
    clearCache: () => void;
  };

  // Convenience properties
  isLoading: boolean;
  hasError: boolean;
  errors: {
    config: string | null;
    branding: string | null;
    features: string | null;
  };
}

// Create context
const ConfigContext = createContext<ConfigContextValue | undefined>(undefined);

// Provider component props
interface ConfigProviderProps {
  children: ReactNode;
}

// Provider component
export function ConfigProvider({ children }: ConfigProviderProps) {
  const configData = useConfigProvider();

  return (
    <ConfigContext.Provider value={configData}>
      {children}
    </ConfigContext.Provider>
  );
}

// Hook to use configuration context
export function useConfigContext(): ConfigContextValue {
  const context = useContext(ConfigContext);

  if (context === undefined) {
    throw new Error("useConfigContext must be used within a ConfigProvider");
  }

  return context;
}

// Convenience hooks for specific configuration sections
export function useAppConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.app || null,
    loading: config.loading,
    error: config.error,
  };
}

export function useDatabaseConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.database || null,
    loading: config.loading,
    error: config.error,
  };
}

export function useAPIConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.api || null,
    loading: config.loading,
    error: config.error,
  };
}

export function useSecurityConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.security || null,
    loading: config.loading,
    error: config.error,
  };
}

export function useNotificationConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.notification || null,
    loading: config.loading,
    error: config.error,
  };
}

export function useLoggingConfig() {
  const { config } = useConfigContext();
  return {
    data: config.data?.logging || null,
    loading: config.loading,
    error: config.error,
  };
}

// HOC for configuration injection
export function withConfig<P extends object>(
  Component: React.ComponentType<P & { config: ConfigContextValue }>
) {
  const WrappedComponent = (props: P) => {
    const config = useConfigContext();
    return <Component {...props} config={config} />;
  };

  WrappedComponent.displayName = `withConfig(${
    Component.displayName || Component.name
  })`;
  return WrappedComponent;
}

// Configuration loading wrapper component
interface ConfigLoaderProps {
  children: ReactNode;
  fallback?: ReactNode;
  errorFallback?: (error: string) => ReactNode;
}

export function ConfigLoader({
  children,
  fallback = <div>Loading configuration...</div>,
  errorFallback = (error: string) => (
    <div>Error loading configuration: {error}</div>
  ),
}: ConfigLoaderProps) {
  const { isLoading, hasError, errors } = useConfigContext();

  if (isLoading) {
    return <>{fallback}</>;
  }

  if (hasError) {
    const firstError =
      errors.config || errors.branding || errors.features || "Unknown error";
    return <>{errorFallback(firstError)}</>;
  }

  return <>{children}</>;
}

// Feature flag component
interface FeatureGateProps {
  feature: keyof FeaturesConfig;
  children: ReactNode;
  fallback?: ReactNode;
}

export function FeatureGate({
  feature,
  children,
  fallback = null,
}: FeatureGateProps) {
  const { features } = useConfigContext();

  if (features.loading) {
    return <>{fallback}</>;
  }

  const isEnabled = features.data?.[feature] ?? false;

  return isEnabled ? <>{children}</> : <>{fallback}</>;
}

// Theme wrapper component
interface ThemeWrapperProps {
  children: ReactNode;
}

export function ThemeWrapper({ children }: ThemeWrapperProps) {
  const { branding } = useConfigContext();

  React.useEffect(() => {
    if (branding.data && typeof document !== "undefined") {
      const root = document.documentElement;
      root.style.setProperty("--primary-color", branding.data.primary_color);
      root.style.setProperty(
        "--secondary-color",
        branding.data.secondary_color
      );
      root.setAttribute("data-theme", branding.data.theme);

      // Update page title
      document.title = branding.data.company_name;

      // Update favicon if logo_url is provided
      if (branding.data.logo_url) {
        const favicon = document.querySelector(
          'link[rel="icon"]'
        ) as HTMLLinkElement;
        if (favicon) {
          favicon.href = branding.data.logo_url;
        }
      }
    }
  }, [branding.data]);

  return <>{children}</>;
}
