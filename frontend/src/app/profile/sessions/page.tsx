"use client";

import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { useRouter } from "next/navigation";
import { SessionSchema } from "@/types/auth";
import Link from "next/link";

export default function SessionsPage() {
  const queryClient = useQueryClient();
  const router = useRouter();
  const { accessToken, user, initialized } = useAuthStore();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (initialized && !accessToken) {
      router.push("/login");
    }
  }, [initialized, accessToken, router]);

  // Fetch active sessions
  const { data: sessions, isLoading, error } = useQuery<SessionSchema[]>({
    queryKey: ["sessions"],
    queryFn: async () => {
      const res = await apiClient.get("/auth/sessions");
      return res.data;
    },
    enabled: !!accessToken,
  });

  // Terminate a single session
  const deleteSessionMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/auth/sessions/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });

  // Terminate all sessions except current
  const deleteAllSessionsMutation = useMutation({
    mutationFn: async () => {
      await apiClient.delete("/auth/sessions/all");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });

  if (!initialized) {
    return (
      <div className="relative min-h-screen p-6 md:p-12">
        <LiquidBlobBackground />
        <div className="max-w-4xl mx-auto space-y-6">
          <ShimmerSkeleton className="h-10 w-48" />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <ShimmerSkeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!accessToken) {
    return null;
  }

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <LiquidBlobBackground />
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-white font-display">
            Активные сессии
          </h1>
          <Link href="/profile">
            <Button variant="secondary">Назад в профиль</Button>
          </Link>
        </div>

        {sessions && sessions.length > 1 && (
          <GlassPanel className="flex justify-between items-center border border-red-500/20 bg-red-500/5">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Завершить другие сессии
              </h2>
              <p className="text-sm text-gray-400">
                Это закроет доступ ко всем устройствам, кроме этого.
              </p>
            </div>
            <Button
              variant="danger"
              onClick={() => deleteAllSessionsMutation.mutate()}
              disabled={deleteAllSessionsMutation.isPending}
            >
              {deleteAllSessionsMutation.isPending ? "Выход..." : "Выйти на всех устройствах"}
            </Button>
          </GlassPanel>
        )}

        {isLoading ? (
          <div className="space-y-4">
            <ShimmerSkeleton className="h-20 w-full" />
            <ShimmerSkeleton className="h-20 w-full" />
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-lg">
            Не удалось загрузить список сессий.
          </div>
        ) : (
          <div className="space-y-4">
            {sessions?.map((session) => (
              <GlassPanel
                key={session.id}
                className="flex justify-between items-center hover:bg-white/[0.08] transition-all"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-semibold text-white">
                      {session.device_name || "Неизвестное устройство"}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-gray-300">
                      {session.device_type || "Browser"}
                    </span>
                  </div>
                  <div className="text-sm text-gray-400 space-y-0.5">
                    <p>IP: {session.ip_address || "Скрыт"}</p>
                    <p>Страна: {session.country || "Неопределена"}</p>
                    {session.user_agent && (
                      <p className="text-xs text-gray-500 max-w-md truncate">
                        UA: {session.user_agent}
                      </p>
                    )}
                  </div>
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => deleteSessionMutation.mutate(session.id)}
                  disabled={deleteSessionMutation.isPending}
                >
                  Завершить
                </Button>
              </GlassPanel>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
