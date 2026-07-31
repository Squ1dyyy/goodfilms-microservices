"use client";

import React, { useEffect } from "react";
import axios from "axios";
import { useAuthStore } from "@/store/auth";

interface AuthInitializerProps {
  children: React.ReactNode;
}

export default function AuthInitializer({ children }: AuthInitializerProps) {
  const { accessToken, setSession, clearSession, setInitialized } = useAuthStore();

  useEffect(() => {
    const restoreSession = async () => {
      // Only attempt to restore if we don't already have an access token in memory
      if (!accessToken) {
        try {
          const response = await axios.post("/api/auth/refresh", {}, { baseURL: "" });
          const { access_token, user } = response.data;
          setSession(access_token, user);
        } catch (error) {
          // If refresh fails (e.g. no token, expired), ensure session is cleared
          clearSession();
        } finally {
          setInitialized(true);
        }
      } else {
        setInitialized(true);
      }
    };

    restoreSession();
  }, [accessToken, setSession, clearSession, setInitialized]);

  return <>{children}</>;
}
