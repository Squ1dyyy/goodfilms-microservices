import axios, { AxiosError } from "axios";
import { useAuthStore } from "../store/auth";

export class ApiError extends Error {
  status?: number;
  detail?: string;

  constructor(message: string, status?: number, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function getBaseUrl(): string {
  // Server-side (SSR inside Docker): use internal gateway URL
  if (typeof window === "undefined") {
    return process.env.INTERNAL_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080/api/v1";
  }
  // Client-side (browser): use public URL
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080/api/v1";
}

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach Auth Token + dynamic baseURL for SSR
apiClient.interceptors.request.use(
  (config) => {
    // Dynamically resolve baseURL per request (important for SSR vs client)
    config.baseURL = getBaseUrl();

    if (typeof window !== "undefined") {
      const token = useAuthStore.getState().accessToken;
      if (token && config.headers) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle errors and refresh tokens on 401
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    if (!originalRequest) {
      return Promise.reject(error);
    }

    interface RetryableRequestConfig {
      _retry?: boolean;
    }

    // Handle 401 Unauthorized (Token Expiry)
    // Avoid infinite loop if we already tried refreshing for this request
    if (error.response?.status === 401 && !(originalRequest as RetryableRequestConfig)._retry) {
      (originalRequest as RetryableRequestConfig)._retry = true;
      try {
        // Request new tokens from our Next.js Route Handler (which manages httpOnly cookies)
        const response = await axios.post(
          "/api/auth/refresh",
          {},
          { baseURL: "" }
        );
        const data = response.data;
        
        // Update session in Zustand store
        useAuthStore.getState().setSession(data.access_token, data.user);
        
        // Retry the original request with new token
        if (originalRequest.headers) {
          originalRequest.headers["Authorization"] = `Bearer ${data.access_token}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Clear session and redirect to login if refresh fails
        useAuthStore.getState().clearSession();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    // Extract unified ApiError
    let message = error.message;
    let detail: string | undefined = undefined;
    const status = error.response?.status;

    if (error.response?.data && typeof error.response.data === "object") {
      const data = error.response.data as Record<string, unknown>;
      if (typeof data.detail === "string") {
        detail = data.detail;
        message = data.detail;
      }
    }

    return Promise.reject(new ApiError(message, status, detail));
  }
);
