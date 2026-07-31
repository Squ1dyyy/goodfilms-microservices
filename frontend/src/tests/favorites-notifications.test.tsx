import React from "react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useBookmarks } from "../features/favorites/useBookmarks";
import { useNotifications, useNotificationStore } from "../features/notifications/useNotifications";
import { apiClient } from "../lib/api-client";
import { useAuthStore } from "../store/auth";

// A wrapper component to provide QueryClient
const createQueryClientWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  Wrapper.displayName = "QueryClientWrapper";
  return Wrapper;
};

describe("Favorites and Notifications hooks", () => {
  const originalAdapter = apiClient.defaults.adapter;
  const mockAdapter = vi.fn();

  beforeEach(() => {
    // Set mock adapter
    apiClient.defaults.adapter = mockAdapter;
    vi.clearAllMocks();

    // Authenticate user in store so hooks query works
    useAuthStore.getState().setSession("test-access-token", { id: 1, username: "testuser" });
    useNotificationStore.getState().clear();
  });

  afterEach(() => {
    apiClient.defaults.adapter = originalAdapter;
  });

  describe("useBookmarks", () => {
    it("should fetch bookmark IDs on mount", async () => {
      mockAdapter.mockResolvedValue({
        data: [123, 456],
        status: 200,
        statusText: "OK",
        headers: {},
        config: {},
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useBookmarks(), { wrapper });

      await waitFor(() => {
        expect(result.current.bookmarkedIds).toEqual([123, 456]);
      });
      expect(mockAdapter).toHaveBeenCalledWith(
        expect.objectContaining({
          url: "/users/me/bookmarks",
          method: "get",
        })
      );
    });

    it("should optimistically add bookmark on toggle", async () => {
      const currentBookmarks: number[] = [];

      mockAdapter.mockImplementation(async (config) => {
        if (config.url === "/users/me/bookmarks" && config.method === "get") {
          return {
            data: currentBookmarks,
            status: 200,
            statusText: "OK",
            headers: {},
            config,
          };
        }
        if (config.url?.startsWith("/users/me/bookmarks/") && config.method === "post") {
          const parts = config.url.split("/");
          const id = Number(parts[parts.length - 1]);
          currentBookmarks.push(id);
          return {
            data: { success: true },
            status: 200,
            statusText: "OK",
            headers: {},
            config,
          };
        }
        return { data: null, status: 404, statusText: "Not Found", headers: {}, config };
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useBookmarks(), { wrapper });

      // Wait for initial fetch
      await waitFor(() => {
        expect(result.current.bookmarkedIds).toEqual([]);
      });

      act(() => {
        result.current.toggleBookmark(789);
      });

      // Check optimistic update with waitFor since state updates are asynchronous
      await waitFor(() => {
        expect(result.current.bookmarkedIds).toContain(789);
      });
    });

    it("should rollback optimistic bookmark update on error", async () => {
      const currentBookmarks: number[] = [123];
      let shouldFail = false;

      mockAdapter.mockImplementation(async (config) => {
        if (config.url === "/users/me/bookmarks" && config.method === "get") {
          return {
            data: currentBookmarks,
            status: 200,
            statusText: "OK",
            headers: {},
            config,
          };
        }
        if (config.url?.startsWith("/users/me/bookmarks/") && config.method === "post") {
          if (shouldFail) {
            // Introduce a short delay to allow the optimistic update to be observed
            await new Promise((resolve) => setTimeout(resolve, 50));
            const error = new Error("Network Error") as Error & {
              status?: number;
              response?: unknown;
            };
            error.status = 500;
            error.response = { status: 500, data: { detail: "Internal Server Error" } };
            throw error;
          }
          return {
            data: { success: true },
            status: 200,
            statusText: "OK",
            headers: {},
            config,
          };
        }
        return { data: null, status: 404, statusText: "Not Found", headers: {}, config };
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useBookmarks(), { wrapper });

      await waitFor(() => {
        expect(result.current.bookmarkedIds).toEqual([123]);
      });

      shouldFail = true;

      act(() => {
        result.current.toggleBookmark(456); // Toggle add
      });

      // Optimistic check with waitFor
      await waitFor(() => {
        expect(result.current.bookmarkedIds).toEqual([123, 456]);
      });

      // Wait for error handling rollback
      await waitFor(() => {
        expect(result.current.bookmarkedIds).toEqual([123]);
      });
    });
  });

  describe("useNotifications", () => {
    it("should fetch new notifications and calculate unread count", async () => {
      const mockNotifications = [
        {
          id: 1,
          type: "welcome" as const,
          url_link: "/",
          status: "pending_delivery" as const,
          created_at: "2026-06-25T12:00:00Z",
        },
        {
          id: 2,
          type: "new_movie" as const,
          url_link: "/movies/1",
          status: "delivered" as const,
          created_at: "2026-06-25T11:00:00Z",
        },
      ];

      mockAdapter.mockResolvedValue({
        data: mockNotifications,
        status: 200,
        statusText: "OK",
        headers: {},
        config: {},
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useNotifications(), { wrapper });

      await waitFor(() => {
        expect(result.current.notifications.length).toBe(2);
      });

      expect(result.current.unreadCount).toBe(1); // Only 1 is pending_delivery
    });

    it("should mark notification as read and decrement unreadCount", async () => {
      // Seed notifications in Zustand store directly to simulate pre-loaded state
      act(() => {
        useNotificationStore.getState().addNotifications([
          {
            id: 1,
            type: "welcome",
            url_link: "/",
            status: "pending_delivery",
            created_at: "2026-06-25T12:00:00Z",
          },
        ]);
      });

      mockAdapter.mockResolvedValue({
        data: { success: true },
        status: 200,
        statusText: "OK",
        headers: {},
        config: {},
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useNotifications(), { wrapper });

      expect(result.current.unreadCount).toBe(1);

      act(() => {
        result.current.markAsRead(1);
      });

      await waitFor(() => {
        expect(result.current.unreadCount).toBe(0);
        expect(result.current.notifications[0].status).toBe("delivered");
        expect(mockAdapter).toHaveBeenCalledWith(
          expect.objectContaining({
            url: "/notification/1/read",
            method: "patch",
          })
        );
      });
    });

    it("should delete notification and remove it from store", async () => {
      act(() => {
        useNotificationStore.getState().addNotifications([
          {
            id: 1,
            type: "welcome",
            url_link: "/",
            status: "pending_delivery",
            created_at: "2026-06-25T12:00:00Z",
          },
        ]);
      });

      mockAdapter.mockResolvedValue({
        data: null,
        status: 204,
        statusText: "No Content",
        headers: {},
        config: {},
      });

      const wrapper = createQueryClientWrapper();
      const { result } = renderHook(() => useNotifications(), { wrapper });

      expect(result.current.notifications.length).toBe(1);

      act(() => {
        result.current.deleteNotification(1);
      });

      await waitFor(() => {
        expect(result.current.notifications.length).toBe(0);
        expect(mockAdapter).toHaveBeenCalledWith(
          expect.objectContaining({
            url: "/notification/1",
            method: "delete",
          })
        );
      });
    });
  });
});
