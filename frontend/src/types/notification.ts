export interface NotificationItem {
  id: number;
  type: "email_verification" | "password_reset" | "welcome" | "new_movie";
  url_link: string;
  status: "pending_movie" | "pending_delivery" | "delivered";
  created_at: string;
}
