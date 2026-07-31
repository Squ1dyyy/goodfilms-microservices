import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth";
import { NotificationItem } from "@/types/notification";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface NotificationState {
  notifications: NotificationItem[];
  addNotifications: (items: NotificationItem[]) => void;
  markRead: (id: number) => void;
  markAllRead: () => void;
  deleteNotification: (id: number) => void;
  clear: () => void;
}

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set) => ({
      notifications: [],
      addNotifications: (items) =>
        set((state) => {
          const mergedMap = new Map(state.notifications.map((n) => [n.id, n]));
          items.forEach((item) => {
            mergedMap.set(item.id, item);
          });
          const sortedNotifications = Array.from(mergedMap.values()).sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          );
          return { notifications: sortedNotifications };
        }),
      markRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, status: "delivered" as const } : n
          ),
        })),
      markAllRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({
            ...n,
            status: "delivered" as const,
          })),
        })),
      deleteNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),
      clear: () => set({ notifications: [] }),
    }),
    {
      name: "goodfilms-notifications",
    }
  )
);

export function useNotifications() {
  const queryClient = useQueryClient();
  const { accessToken } = useAuthStore();
  const { notifications, addNotifications, markRead, markAllRead, deleteNotification } =
    useNotificationStore();

  // Query: Poll notifications every 30s
  const { refetch, isFetching } = useQuery<NotificationItem[]>({
    queryKey: ["notifications-poll"],
    queryFn: async () => {
      const res = await apiClient.get("/notification", {
        params: { page: 1, limit: 50 },
      });
      const data = res.data || [];
      if (Array.isArray(data)) {
        addNotifications(data);
      }
      return data;
    },
    enabled: !!accessToken,
    refetchInterval: 30000, // 30s
    staleTime: 0,
  });

  const markReadMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.patch(`/notification/${id}/read`);
    },
    onMutate: async (id) => {
      markRead(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-poll"] });
    },
    onError: (err, id, context) => {
      // If error (e.g. 404 already deleted/delivered), we still keep local read state
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post("/notification/read-all");
    },
    onMutate: async () => {
      markAllRead();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-poll"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/notification/${id}`);
    },
    onMutate: async (id) => {
      deleteNotification(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications-poll"] });
    },
  });

  const unreadCount = notifications.filter((n) => n.status === "pending_delivery").length;

  return {
    notifications,
    unreadCount,
    isFetching,
    refetch,
    markAsRead: (id: number) => markReadMutation.mutate(id),
    markAllAsRead: () => markAllReadMutation.mutate(),
    deleteNotification: (id: number) => deleteMutation.mutate(id),
  };
}
