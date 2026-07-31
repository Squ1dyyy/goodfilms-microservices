"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { apiClient, ApiError } from "@/lib/api-client";
import { useSearchParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import Link from "next/link";

const resetPasswordSchema = z.object({
  new_password: z.string().min(6, "Пароль должен быть не менее 6 символов"),
  new_password_confirm: z.string().min(6, "Пароль должен быть не менее 6 символов"),
}).refine((data) => data.new_password === data.new_password_confirm, {
  message: "Пароли не совпадают",
  path: ["new_password_confirm"],
});

type ResetPasswordFields = z.infer<typeof resetPasswordSchema>;

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token");

  const [isValidating, setIsValidating] = useState(true);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFields>({
    resolver: zodResolver(resetPasswordSchema),
  });

  useEffect(() => {
    let active = true;
    if (!token) {
      Promise.resolve().then(() => {
        if (active) {
          setTokenError("Токен сброса пароля отсутствует в ссылке.");
          setIsValidating(false);
        }
      });
      return;
    }

    const validateToken = async () => {
      try {
        await apiClient.get(`/auth/reset_password?token=${token}`);
        if (active) setIsValidating(false);
      } catch (err: unknown) {
        const apiErr = err as ApiError;
        if (active) {
          setTokenError(apiErr.detail || "Ссылка устарела или недействительна.");
          setIsValidating(false);
        }
      }
    };

    validateToken();
    return () => {
      active = false;
    };
  }, [token]);

  const onSubmit = async (data: ResetPasswordFields) => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      await apiClient.post(`/auth/reset_password?token=${token}`, {
        new_password: data.new_password,
      });
      setSuccess(true);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setError(apiErr.detail || apiErr.message || "Ошибка при смене пароля.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <LiquidBlobBackground />
      <GlassPanel className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-white mb-6 font-display">
          Сброс пароля
        </h1>

        {isValidating ? (
          <div className="space-y-4">
            <ShimmerSkeleton className="h-6 w-3/4 mx-auto" />
            <ShimmerSkeleton className="h-10 w-full" />
            <ShimmerSkeleton className="h-10 w-full" />
          </div>
        ) : tokenError ? (
          <div className="text-center space-y-4">
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg">
              {tokenError}
            </div>
            <Link href="/forgot-password">
              <Button className="w-full mt-4">Запросить ссылку снова</Button>
            </Link>
          </div>
        ) : success ? (
          <div className="text-center space-y-4">
            <div className="bg-green-500/10 border border-green-500/20 text-green-400 text-sm p-3 rounded-lg">
              Пароль успешно изменен! Теперь вы можете войти с новым паролем.
            </div>
            <Link href="/login">
              <Button className="w-full mt-4">Войти в систему</Button>
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg">
                {error}
              </div>
            )}
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
                <p className="text-red-400 text-xs mt-1">{errors.new_password.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Подтверждение пароля
              </label>
              <input
                type="password"
                {...register("new_password_confirm")}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
                placeholder="••••••••"
              />
              {errors.new_password_confirm && (
                <p className="text-red-400 text-xs mt-1">{errors.new_password_confirm.message}</p>
              )}
            </div>
            <Button
              type="submit"
              className="w-full mt-2"
              disabled={isLoading}
            >
              {isLoading ? "Сохранение..." : "Изменить пароль"}
            </Button>
          </form>
        )}
      </GlassPanel>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="text-white text-center">Загрузка...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}

