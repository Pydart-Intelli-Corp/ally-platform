/**
 * Frontend Configuration Utilities
 *
 * Provides utilities to fetch and manage configuration from the backend API.
 * Supports caching, error handling, and real-time configuration updates.
 */

// Configuration types
export interface Config {
  database: {
    host: string;
    port: number;
    name: string;
    connection_timeout: number;
  };
  app: {
    name: string;
    version: string;
    debug: boolean;
    secret_key: string;
    allowed_hosts: string[];
  };
  api: {
    base_url: string;
    timeout: number;
    rate_limit: {
      requests: number;
      window: number;
    };
  };
  features: {
    user_registration: boolean;
    email_verification: boolean;
    password_reset: boolean;
    file_upload: boolean;
    admin_panel: boolean;
  };
  branding: {
    company_name: string;
    logo_url: string;
    primary_color: string;
    secondary_color: string;
    theme: "light" | "dark";
  };
  security: {
    session_timeout: number;
    max_login_attempts: number;
    password_policy: {
      min_length: number;
      require_uppercase: boolean;
      require_lowercase: boolean;
      require_numbers: boolean;
      require_symbols: boolean;
    };
  };
  notification: {
    email_enabled: boolean;
    sms_enabled: boolean;
    push_enabled: boolean;
  };
  logging: {
    level: "DEBUG" | "INFO" | "WARNING" | "ERROR";
    file_enabled: boolean;
    console_enabled: boolean;
  };
}

export interface BrandingConfig {
  company_name: string;
  logo_url: string;
  primary_color: string;
  secondary_color: string;
  theme: "light" | "dark";
}

export interface FeaturesConfig {
  user_registration: boolean;
  email_verification: boolean;
  password_reset: boolean;
  file_upload: boolean;
  admin_panel: boolean;
}

// Cache management
class ConfigCache {
  private cache = new Map<
    string,
    { data: unknown; timestamp: number; ttl: number }
  >();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  set(key: string, data: unknown, ttl?: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL,
    });
  }

  get(key: string): unknown | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear(): void {
    this.cache.clear();
  }

  delete(key: string): void {
    this.cache.delete(key);
  }
}

// Global cache instance
const configCache = new ConfigCache();

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_TIMEOUT = 10000; // 10 seconds

// Fetch utilities
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

// Configuration fetching functions
export async function fetchFullConfig(
  useCache: boolean = true
): Promise<Config> {
  const cacheKey = "full-config";

  if (useCache) {
    const cached = configCache.get(cacheKey);
    if (cached) return cached as Config;
  }

  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/config`);

    if (!response.ok) {
      throw new Error(
        `Failed to fetch config: ${response.status} ${response.statusText}`
      );
    }

    const config = await response.json();
    configCache.set(cacheKey, config);
    return config;
  } catch (error) {
    console.error("Error fetching full config:", error);
    throw error;
  }
}

export async function fetchBrandingConfig(
  useCache: boolean = true
): Promise<BrandingConfig> {
  const cacheKey = "branding-config";

  if (useCache) {
    const cached = configCache.get(cacheKey);
    if (cached) return cached as BrandingConfig;
  }

  try {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/config/branding`
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch branding config: ${response.status} ${response.statusText}`
      );
    }

    const branding = await response.json();
    configCache.set(cacheKey, branding);
    return branding;
  } catch (error) {
    console.error("Error fetching branding config:", error);
    throw error;
  }
}

export async function fetchFeaturesConfig(
  useCache: boolean = true
): Promise<FeaturesConfig> {
  const cacheKey = "features-config";

  if (useCache) {
    const cached = configCache.get(cacheKey);
    if (cached) return cached as FeaturesConfig;
  }

  try {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/config/features`
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch features config: ${response.status} ${response.statusText}`
      );
    }

    const features = await response.json();
    configCache.set(cacheKey, features);
    return features;
  } catch (error) {
    console.error("Error fetching features config:", error);
    throw error;
  }
}

// Configuration section fetching
export async function fetchConfigSection(
  section: string,
  useCache: boolean = true
): Promise<Record<string, unknown>> {
  const cacheKey = `config-${section}`;

  if (useCache) {
    const cached = configCache.get(cacheKey);
    if (cached) return cached as Record<string, unknown>;
  }

  try {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/config/${section}`
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch ${section} config: ${response.status} ${response.statusText}`
      );
    }

    const config = await response.json();
    configCache.set(cacheKey, config);
    return config;
  } catch (error) {
    console.error(`Error fetching ${section} config:`, error);
    throw error;
  }
}

// Cache management functions
export function clearConfigCache(): void {
  configCache.clear();
}

export function refreshConfig(): Promise<Config> {
  configCache.clear();
  return fetchFullConfig(false);
}

// Configuration update listener
export function setupConfigListener(): void {
  // Listen for storage events (for cross-tab synchronization)
  if (typeof window !== "undefined") {
    window.addEventListener("storage", (event) => {
      if (event.key === "config-updated") {
        clearConfigCache();
      }
    });
  }
}

// Utility to trigger config refresh across tabs
export function notifyConfigUpdate(): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("config-updated", Date.now().toString());
    localStorage.removeItem("config-updated");
  }
}

// Default configuration fallback
export const defaultConfig: Partial<Config> = {
  app: {
    name: "Ally Platform",
    version: "1.0.0",
    debug: false,
    secret_key: "",
    allowed_hosts: ["localhost"],
  },
  branding: {
    company_name: "Ally Platform",
    logo_url: "/logo.png",
    primary_color: "#007bff",
    secondary_color: "#6c757d",
    theme: "light",
  },
  features: {
    user_registration: true,
    email_verification: false,
    password_reset: true,
    file_upload: true,
    admin_panel: false,
  },
};

// Error handling utility
export function getConfigWithFallback<T>(
  configPromise: Promise<T>,
  fallback: T
): Promise<T> {
  return configPromise.catch((error) => {
    console.warn("Using fallback config due to error:", error);
    return fallback;
  });
}
