"use client";

import React, { useState, useEffect } from "react";
import { useNotifications } from "@/features/notifications/useNotifications";
import { getNotificationMapping } from "@/lib/notification-mapping";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { Button } from "@/components/ui/Button";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { Check, Trash2, ArrowLeft, ArrowRight, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function NotificationsPage() {
  const router = useRouter();
  const { accessToken, initialized } = useAuthStore();
  const { notifications, markAsRead, markAllAsRead, deleteNotification } = useNotifications();

  const [mounted, setMounted] = useState(false);
  const [page, setPage] = useState(1);
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  const limit = 10;

  useEffect(() => {
    let active = true;
    Promise.resolve().then(() => {
      if (active) setMounted(true);
    });
    if (initialized && !accessToken) {
      router.push("/login");
    }
    return () => {
      active = false;
    };
  }, [initialized, accessToken, router]);

  if (!initialized || !mounted) {
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

  const unreadCount = notifications.filter((n) => n.status === "pending_delivery").length;

  // Local Pagination
  const totalPages = Math.ceil(notifications.length / limit);
  const paginatedNotifications = notifications.slice((page - 1) * limit, page * limit);

  const handlePageChange = (nextPage: number) => {
    setPage(nextPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const getToneClasses = (tone: string) => {
    switch (tone) {
      case "success":
        return "bg-green-500/10 border-green-500/30 text-green-400";
      case "warning":
        return "bg-[#E8B74C]/10 border-[#E8B74C]/30 text-[#E8B74C]";
      case "error":
        return "bg-red-500/10 border-red-500/30 text-red-400";
      default:
        return "bg-blue-500/10 border-blue-500/30 text-blue-400";
    }
  };

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <LiquidBlobBackground />
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-4xl font-bold text-white font-display">
              Центр уведомлений
            </h1>
            <p className="text-sm text-gray-400">
              У вас {unreadCount} непрочитанных уведомлений
            </p>
          </div>
          {unreadCount > 0 && (
            <Button onClick={markAllAsRead} variant="secondary" className="gap-2">
              <Check size={16} /> Прочитать все
            </Button>
          )}
        </div>

        {notifications.length === 0 ? (
          <GlassPanel className="py-20 text-center space-y-4">
            <p className="text-gray-400 text-lg">У вас пока нет уведомлений.</p>
            <Link href="/movies">
              <Button>Перейти в каталог</Button>
            </Link>
          </GlassPanel>
        ) : (
          <div className="space-y-4">
            {paginatedNotifications.map((notif) => {
              const mapping = getNotificationMapping(notif.type);
              const Icon = mapping.icon;
              const isUnread = notif.status === "pending_delivery";
              const isConfirmingDelete = deleteConfirmId === notif.id;

              return (
                <GlassPanel
                  key={notif.id}
                  className={`p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border transition-all ${
                    notif.url_link ? "cursor-pointer hover:bg-white/[0.06] hover:border-white/30" : ""
                  } ${
                    isUnread
                      ? "bg-white/[0.04] border-white/20 shadow-md"
                      : "bg-white/[0.01] border-white/10 opacity-70"
                  }`}
                  onClick={() => {
                    if (notif.url_link) {
                      if (isUnread) {
                        markAsRead(notif.id);
                      }
                      router.push(notif.url_link);
                    }
                  }}
                >
                  <div className="flex items-start gap-4 flex-grow min-w-0">
                    <div
                      className={`h-12 w-12 rounded-xl border flex items-center justify-center shrink-0 ${getToneClasses(
                        mapping.tone
                      )}`}
                    >
                      <Icon size={22} />
                    </div>
                    <div className="space-y-1 flex-grow min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">
                          {new Date(notif.created_at).toLocaleString()}
                        </span>
                        {isUnread && (
                          <span className="px-2 py-0.5 rounded-full bg-[#E8B74C]/10 border border-[#E8B74C]/30 text-[#E8B74C] text-[9px] font-bold">
                            Новое
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-semibold text-white leading-relaxed">
                        {mapping.defaultText}
                      </p>
                      {notif.url_link && (
                        <span
                          className="inline-flex items-center gap-1 text-xs text-[#6E5CFF] hover:underline pt-1 font-medium"
                        >
                          Перейти к источнику <ExternalLink size={12} />
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 self-end md:self-center">
                    {isConfirmingDelete ? (
                      <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-lg p-1.5 transition-all animate-in fade-in zoom-in-95 duration-150">
                        <span className="text-xs text-red-400 px-2 font-medium">Точно удалить?</span>
                        <Button
                          variant="danger"
                          size="sm"
                          className="h-7 text-xs px-2.5"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notif.id);
                            setDeleteConfirmId(null);
                          }}
                        >
                          Да
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          className="h-7 text-xs px-2.5"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirmId(null);
                          }}
                        >
                          Нет
                        </Button>
                      </div>
                    ) : (
                      <>
                        {isUnread && (
                          <Button
                            variant="secondary"
                            size="sm"
                            className="gap-1.5 h-9"
                            onClick={(e) => {
                              e.stopPropagation();
                              markAsRead(notif.id);
                            }}
                          >
                            <Check size={14} /> Прочитать
                          </Button>
                        )}
                        <Button
                          variant="glass"
                          size="sm"
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/15 border-white/5 h-9 w-9 p-0 flex items-center justify-center"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirmId(notif.id);
                          }}
                          aria-label="Удалить уведомление"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </>
                    )}
                  </div>
                </GlassPanel>
              );
            })}
          </div>
        )}

        {/* Local Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-4 pt-4">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handlePageChange(page - 1)}
              disabled={page <= 1}
              className="gap-1"
            >
              <ArrowLeft size={16} /> Назад
            </Button>
            <span className="text-sm text-gray-400 font-medium">
              Страница {page} из {totalPages}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
              className="gap-1"
            >
              Вперед <ArrowRight size={16} />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
