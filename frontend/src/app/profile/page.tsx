"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient, ApiError } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { useRouter } from "next/navigation";
import { UserDataSchema } from "@/types/auth";
import { ComingSoonState } from "@/components/ui/ComingSoonState";
import Link from "next/link";

const passwordSchema = z.object({
  current_password: z.string().min(1, "Введите текущий пароль"),
  new_password: z.string().min(6, "Новый пароль должен быть не менее 6 символов"),
  new_password_confirm: z.string().min(6, "Подтвердите новый пароль"),
}).refine((data) => data.new_password === data.new_password_confirm, {
  message: "Пароли не совпадают",
  path: ["new_password_confirm"],
});

type PasswordFields = z.infer<typeof passwordSchema>;

export default function ProfilePage() {
  const router = useRouter();
  const { accessToken, setSession, clearSession, initialized } = useAuthStore();
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);

  // Redirect if not authed
  React.useEffect(() => {
    if (initialized && !accessToken) {
      router.push("/login");
    }
  }, [initialized, accessToken, router]);

  // Fetch full user data
  const { data: profile, isLoading } = useQuery<UserDataSchema>({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await apiClient.get("/auth/me");
      return res.data;
    },
    enabled: !!accessToken,
  });

  // Password mutation
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<PasswordFields>({
    resolver: zodResolver(passwordSchema),
  });

  const changePasswordMutation = useMutation({
    mutationFn: async (data: PasswordFields) => {
      const res = await apiClient.patch("/auth/password", data);
      return res.data;
    },
    onSuccess: (data) => {
      setPasswordSuccess("Пароль успешно изменен!");
      setPasswordError(null);
      setSession(data.access_token, data.user);
      reset();
    },
    onError: (err: unknown) => {
      const apiErr = err as ApiError;
      setPasswordSuccess(null);
      setPasswordError(apiErr.detail || "Не удалось изменить пароль.");
    },
  });

  const handleLogout = async () => {
    try {
      await axios.post("/api/auth/logout", {}, { baseURL: "" });
    } catch {
      // Ignored
    } finally {
      clearSession();
      router.push("/login");
    }
  };

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
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-4xl font-bold text-white font-display">
            Профиль
          </h1>
          <Button variant="secondary" onClick={handleLogout}>
            Выйти
          </Button>
        </div>

        {isLoading || !profile ? (
          <div className="space-y-4">
            <ShimmerSkeleton className="h-40 w-full" />
            <ShimmerSkeleton className="h-60 w-full" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Left side: user data */}
            <div className="md:col-span-1 space-y-6">
              <GlassPanel className="space-y-4">
                <div className="h-20 w-20 rounded-full bg-[#6E5CFF]/20 flex items-center justify-center text-white text-3xl font-bold font-display border border-[#6E5CFF]/40 mx-auto">
                  {profile.username.substring(0, 2).toUpperCase()}
                </div>
                <div className="text-center">
                  <h2 className="text-xl font-bold text-white">
                    {profile.username}
                  </h2>
                  <p className="text-sm text-gray-400">{profile.email}</p>
                </div>
                <div className="border-t border-white/10 pt-4 space-y-2 text-sm text-gray-400">
                  <div className="flex justify-between">
                    <span>Статус почты:</span>
                    <span className={profile.is_verified ? "text-green-400" : "text-[#E8B74C]"}>
                      {profile.is_verified ? "Подтверждена" : "Не подтверждена"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Роль:</span>
                    <span className="text-white capitalize">{profile.role}</span>
                  </div>
                </div>
                <Link href="/profile/sessions" className="block mt-4">
                  <Button variant="glass" className="w-full">
                    Активные сессии
                  </Button>
                </Link>
              </GlassPanel>
            </div>

            {/* Right side: settings */}
            <div className="md:col-span-2 space-y-6">
              {/* Password change form */}
              <GlassPanel className="space-y-6">
                <h3 className="text-xl font-bold text-white font-display">
                  Изменение пароля
                </h3>
                {passwordError && (
                  <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg">
                    {passwordError}
                  </div>
                )}
                {passwordSuccess && (
                  <div className="bg-green-500/10 border border-green-500/20 text-green-400 text-sm p-3 rounded-lg">
                    {passwordSuccess}
                  </div>
                )}
                <form
                  onSubmit={handleSubmit((data) => changePasswordMutation.mutate(data))}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Текущий пароль
                    </label>
                    <input
                      type="password"
                      {...register("current_password")}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
                      placeholder="••••••••"
                    />
                    {errors.current_password && (
                      <p className="text-red-400 text-xs mt-1">
                        {errors.current_password.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Новый пароль
                    </label>
                    <input
                      type="password"
                      {...register("new_password")}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
                      placeholder="••••••••"
                    />
                    {errors.new_password && (
                      <p className="text-red-400 text-xs mt-1">
                        {errors.new_password.message}
                      </p>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Подтверждение нового пароля
                    </label>
                    <input
                      type="password"
                      {...register("new_password_confirm")}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
                      placeholder="••••••••"
                    />
                    {errors.new_password_confirm && (
                      <p className="text-red-400 text-xs mt-1">
                        {errors.new_password_confirm.message}
                      </p>
                    )}
                  </div>
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "Сохранение..." : "Обновить пароль"}
                  </Button>
                </form>
              </GlassPanel>

              {/* History / Bookmarks coming soon placeholder */}
              <GlassPanel className="space-y-4">
                <h3 className="text-xl font-bold text-white font-display">
                  История просмотров
                </h3>
                <ComingSoonState label="История просмотров" />
              </GlassPanel>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Add an inline placeholder for axios if not imported
import axios from "axios";
