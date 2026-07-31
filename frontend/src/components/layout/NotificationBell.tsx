"use client";

import React, { useState, useEffect } from "react";
import { Bell, Check, ExternalLink } from "lucide-react";
import { useNotifications } from "@/features/notifications/useNotifications";
import { getNotificationMapping } from "@/lib/notification-mapping";
import { useAuthStore } from "@/store/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/DropdownMenu";
import { Button } from "@/components/ui/Button";

export default function NotificationBell() {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.resolve().then(() => {
      if (active) setMounted(true);
    });
    return () => {
      active = false;
    };
  }, []);

  if (!accessToken) {
    return null;
  }

  // Fallback for SSR/Hydration
  if (!mounted) {
    return (
      <div className="relative p-2 rounded-full text-gray-400">
        <Bell size={20} />
      </div>
    );
  }

  const latestNotifications = notifications.slice(0, 5);

  const getToneColor = (tone: string) => {
    switch (tone) {
      case "success":
        return "text-green-400";
      case "warning":
        return "text-[#E8B74C]";
      case "error":
        return "text-red-400";
      default:
        return "text-blue-400";
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="relative p-2 rounded-full text-gray-400 hover:text-white transition-all outline-none focus-visible:ring-2 focus-visible:ring-[#E8B74C]">
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-[#E8B74C] text-[10px] font-bold text-[#0A0C14]">
              {unreadCount}
            </span>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-80 p-2 border border-white/10" align="end">
        <div className="flex items-center justify-between px-2 py-1.5 border-b border-white/5">
          <span className="text-sm font-semibold text-white font-display">Уведомления</span>
          {unreadCount > 0 && (
            <button
              onClick={markAllAsRead}
              className="text-xs text-[#E8B74C] hover:underline flex items-center gap-1 font-medium transition-all"
            >
              <Check size={12} /> Прочитать все
            </button>
          )}
        </div>

        <div className="max-h-64 overflow-y-auto py-1 scrollbar-thin scrollbar-thumb-white/10">
          {latestNotifications.length === 0 ? (
            <div className="py-6 text-center text-xs text-gray-400">Нет новых уведомлений</div>
          ) : (
            latestNotifications.map((notif) => {
              const mapping = getNotificationMapping(notif.type);
              const Icon = mapping.icon;
              const isUnread = notif.status === "pending_delivery";

              return (
                <DropdownMenuItem
                  key={notif.id}
                  className={`flex flex-col items-start gap-1 p-2 transition-all rounded-md cursor-pointer ${
                    isUnread ? "bg-white/[0.03] border-l-2 border-l-[#E8B74C]" : ""
                  }`}
                  onClick={() => {
                    if (isUnread) {
                      markAsRead(notif.id);
                    }
                    if (notif.url_link) {
                      router.push(notif.url_link);
                    }
                  }}
                >
                  <div className="flex items-start gap-2.5 w-full">
                    <Icon size={16} className={`mt-0.5 shrink-0 ${getToneColor(mapping.tone)}`} />
                    <div className="flex-grow min-w-0">
                      <p className="text-xs text-white leading-relaxed">
                        {mapping.defaultText}
                      </p>
                      {notif.url_link && (
                        <span className="text-[10px] text-[#6E5CFF] hover:underline flex items-center gap-0.5 mt-1 font-medium">
                          Открыть ссылку <ExternalLink size={8} />
                        </span>
                      )}
                    </div>
                    {isUnread && (
                      <span className="h-1.5 w-1.5 rounded-full bg-[#E8B74C] shrink-0 mt-1.5" />
                    )}
                  </div>
                  <span className="text-[9px] text-gray-500 self-end mt-1">
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </DropdownMenuItem>
              );
            })
          )}
        </div>

        <div className="border-t border-white/5 pt-1.5 flex justify-center">
          <Link href="/notifications" className="w-full">
            <Button variant="glass" size="sm" className="w-full text-xs py-1">
              Показать все
            </Button>
          </Link>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
