"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { apiClient, ApiError } from "@/lib/api-client";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import Link from "next/link";

const verifyEmailSchema = z.object({
  code: z.string().regex(/^\d+$/, "Код должен состоять только из цифр").min(4, "Минимум 4 цифры"),
});

type VerifyEmailFields = z.infer<typeof verifyEmailSchema>;

function VerifyEmailForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const codeParam = searchParams.get("code");
  const { user } = useAuthStore();

  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // Cooldown & limits state
  const [cooldown, setCooldown] = useState(0);
  const [resendCount, setResendCount] = useState(0);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<VerifyEmailFields>({
    resolver: zodResolver(verifyEmailSchema),
  });

  const onSubmit = async (data: VerifyEmailFields) => {
    setIsLoading(true);
    setError(null);
    setMessage(null);
    try {
      await apiClient.post(`/auth/verify_email?code=${data.code}`);
      setMessage("Электронная почта успешно подтверждена!");
      setTimeout(() => {
        router.push("/");
      }, 2000);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setError(apiErr.detail || apiErr.message || "Неверный код подтверждения.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (codeParam) {
      setValue("code", codeParam);
      // Auto-submit if code is in URL
      Promise.resolve().then(() => {
        onSubmit({ code: codeParam });
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [codeParam]);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const handleResend = async () => {
    if (!user) {
      setError("Пожалуйста, войдите в систему, чтобы отправить код повторно.");
      return;
    }
    if (resendCount >= 3) {
      setError("Превышен дневной лимит отправки кодов (максимум 3).");
      return;
    }

    setIsLoading(true);
    setError(null);
    setMessage(null);
    try {
      await apiClient.post("/auth/send_verification");
      setMessage("Новый код подтверждения отправлен на вашу почту.");
      setResendCount((prev) => prev + 1);
      setCooldown(60); // 1 minute cooldown
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      setError(apiErr.detail || apiErr.message || "Не удалось отправить код повторно.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <LiquidBlobBackground />
      <GlassPanel className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-white mb-6 font-display">
          Подтверждение Email
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
              Код подтверждения из письма
            </label>
            <input
              type="text"
              {...register("code")}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base tracking-widest text-center"
              placeholder="123456"
            />
            {errors.code && (
              <p className="text-red-400 text-xs mt-1 text-center">{errors.code.message}</p>
            )}
          </div>
          <Button
            type="submit"
            className="w-full mt-2"
            disabled={isLoading}
          >
            {isLoading ? "Проверка..." : "Подтвердить"}
          </Button>
        </form>

        <div className="mt-6 flex flex-col items-center space-y-4">
          <button
            onClick={handleResend}
            disabled={cooldown > 0 || resendCount >= 3 || isLoading}
            className="text-sm text-[#6E5CFF] hover:text-[#5744ff] font-medium disabled:opacity-50 disabled:pointer-events-none"
          >
            {resendCount >= 3
              ? "Дневной лимит исчерпан"
              : cooldown > 0
              ? `Отправить повторно через ${cooldown} сек.`
              : "Отправить код еще раз"}
          </button>

          <Link href="/" className="text-sm text-gray-400 hover:text-white">
            На главную
          </Link>
        </div>
      </GlassPanel>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="text-white text-center">Загрузка...</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}

