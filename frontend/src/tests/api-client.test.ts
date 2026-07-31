import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { apiClient, ApiError } from "../lib/api-client";
import { useAuthStore } from "../store/auth";
import axios from "axios";

// Mock raw axios
vi.mock("axios", async (importOriginal) => {
  const actual = await importOriginal<typeof import("axios")>();
  return {
    ...actual,
    default: {
      ...actual.default,
      post: vi.fn(),
    },
  };
});

describe("apiClient", () => {
  const originalAdapter = apiClient.defaults.adapter;
  const mockAdapter = vi.fn();

  beforeEach(() => {
    useAuthStore.getState().clearSession();
    vi.clearAllMocks();
    apiClient.defaults.adapter = mockAdapter;
  });

  afterEach(() => {
    apiClient.defaults.adapter = originalAdapter;
  });

  it("should attach Authorization header when token exists", async () => {
    useAuthStore.getState().setSession("test-token", { id: 1, username: "user" });

    mockAdapter.mockResolvedValue({
      data: { success: true },
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    });

    const result = await apiClient.get("/test-endpoint");

    expect(mockAdapter).toHaveBeenCalled();
    const config = mockAdapter.mock.calls[0][0];
    expect(config.headers?.["Authorization"]).toBe("Bearer test-token");
    expect(result.data.success).toBe(true);
  });

  it("should attempt to refresh token on 401 and retry request", async () => {
    useAuthStore.getState().setSession("expired-token", { id: 1, username: "user" });

    // Mock refresh call on raw axios
    const mockRefreshResponse = {
      data: {
        access_token: "new-valid-token",
        user: { id: 1, username: "user" },
      },
      status: 200,
    };
    vi.mocked(axios.post).mockResolvedValue(mockRefreshResponse);

    // Mock adapter to fail first with 401, then succeed on retry
    let callCount = 0;
    mockAdapter.mockImplementation(async (config) => {
      callCount++;
      if (callCount === 1) {
        const error = new Error("Unauthorized") as Error & {
          isAxiosError: boolean;
          response: unknown;
          config: unknown;
        };
        error.isAxiosError = true;
        error.response = {
          status: 401,
          statusText: "Unauthorized",
          headers: {},
          config,
          data: { detail: "Token expired" },
        };
        error.config = config;
        throw error;
      }
      return {
        data: { success: true },
        status: 200,
        statusText: "OK",
        headers: {},
        config,
      };
    });

    const result = await apiClient.get("/test-endpoint");

    expect(axios.post).toHaveBeenCalledWith("/api/auth/refresh", {}, { baseURL: "" });
    expect(useAuthStore.getState().accessToken).toBe("new-valid-token");
    expect(result.data.success).toBe(true);
    expect(callCount).toBe(2);
  });

  it("should clear session and redirect to /login if refresh fails", async () => {
    useAuthStore.getState().setSession("expired-token", { id: 1, username: "user" });

    // Mock refresh call to fail
    vi.mocked(axios.post).mockRejectedValue(new Error("Refresh failed"));

    // Mock adapter to return 401
    mockAdapter.mockImplementation(async (config) => {
      const error = new Error("Unauthorized") as Error & {
        isAxiosError: boolean;
        response: unknown;
        config: unknown;
      };
      error.isAxiosError = true;
      error.response = {
        status: 401,
        statusText: "Unauthorized",
        headers: {},
        config,
        data: { detail: "Token expired" },
      };
      error.config = config;
      throw error;
    });

    // Mock window location
    const originalWindow = global.window;
    const mockLocation = { href: "" };
    global.window = { location: mockLocation } as unknown as Window & typeof globalThis;

    await expect(apiClient.get("/test-endpoint")).rejects.toThrow();

    expect(useAuthStore.getState().accessToken).toBeNull();
    expect(mockLocation.href).toBe("/login");

    // Restore window
    global.window = originalWindow;
  });
});
