"use client";

import React, { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";

export default function VerifyEmailBanner() {
  const { accessToken, user } = useAuthStore();
  const [isVerified, setIsVerified] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    if (!accessToken || !user) {
      Promise.resolve().then(() => {
        if (active) setIsVerified(null);
      });
      return;
    }

    const fetchMe = async () => {
      try {
        const response = await apiClient.get("/auth/me");
        if (active) setIsVerified(response.data.is_verified);
      } catch {
        // Safe to ignore or clear session if unauthorized
      }
    };

    fetchMe();
    return () => {
      active = false;
    };
  }, [accessToken, user]);

  if (isVerified === null || isVerified === true) {
    return null;
  }

  return (
    <div className="bg-[#E8B74C] text-[#0A0C14] text-center py-2 px-4 text-sm font-semibold flex items-center justify-center gap-2 z-40 sticky top-0">
      <span>Ваша электронная почта не подтверждена.</span>
      <Link href="/verify-email" className="underline hover:text-black">
        Подтвердить сейчас
      </Link>
    </div>
  );
}
