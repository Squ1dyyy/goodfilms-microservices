"use client";

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { apiClient, ApiError } from "@/lib/api-client";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import Link from "next/link";

const forgotPasswordSchema = z.object({
  email: z.string().email("Некорректный email"),
});

type ForgotPasswordFields = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFields>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const onSubmit = async (data: ForgotPasswordFields) => {
    setIsLoading(true);
    setError(null);
    setMessage(null);
    try {
      await apiClient.post("/auth/forgot_password", data);
      setMessage("Ссылка для сброса пароля отправлена на вашу почту.");
      setCooldown(60); // 60 seconds cooldown
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setError(apiErr.detail || apiErr.message || "Ошибка при запросе сброса пароля.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <LiquidBlobBackground />
      <GlassPanel className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-white mb-6 font-display">
          Восстановление доступа
        </h1>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        {message && (
          <div className="bg-green-500/10 border border-green-500/20 text-green-400 text-sm p-3 rounded-lg mb-4">
            {message}
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Электронная почта
            </label>
            <input
              type="email"
              {...register("email")}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
              placeholder="example@mail.com"
            />
            {errors.email && (
              <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
            )}
          </div>
          <Button
            type="submit"
            className="w-full mt-2"
            disabled={isLoading || cooldown > 0}
          >
            {cooldown > 0
              ? `Отправить повторно через ${cooldown} сек.`
              : isLoading
              ? "Отправка..."
              : "Сбросить пароль"}
          </Button>
        </form>
        <p className="text-center text-sm text-gray-400 mt-6">
          Вспомнили пароль?{" "}
          <Link href="/login" className="text-[#6E5CFF] hover:text-[#5744ff] font-medium">
            Войти
          </Link>
        </p>
      </GlassPanel>
    </div>
  );
}
