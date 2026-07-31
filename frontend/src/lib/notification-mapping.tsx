import React from "react";
import { Mail, Key, Sparkles, Film, Bell, LucideIcon } from "lucide-react";
import { NotificationItem } from "@/types/notification";

export interface NotificationMapping {
  icon: LucideIcon;
  defaultText: string;
  tone: "info" | "success" | "warning" | "error";
}

const mappings: Record<string, NotificationMapping> = {
  welcome: {
    icon: Sparkles,
    defaultText: "Добро пожаловать в GoodFilms!",
    tone: "success",
  },
  email_verification: {
    icon: Mail,
    defaultText: "Пожалуйста, подтвердите ваш адрес электронной почты.",
    tone: "warning",
  },
  password_reset: {
    icon: Key,
    defaultText: "Запрос на сброс пароля получен.",
    tone: "warning",
  },
  new_movie: {
    icon: Film,
    defaultText: "В каталоге появился новый фильм!",
    tone: "success",
  },
};

const defaultMapping: NotificationMapping = {
  icon: Bell,
  defaultText: "Новое уведомление",
  tone: "info",
};

export function getNotificationMapping(type: string): NotificationMapping {
  return mappings[type] || defaultMapping;
}
