"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import axios, { AxiosError } from "axios";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import Link from "next/link";

const loginSchema = z.object({
  email: z.string().email("Некорректный email"),
  password: z.string().min(6, "Пароль должен быть не менее 6 символов"),
});

type LoginFields = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const setSession = useAuthStore((state) => state.setSession);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFields>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFields) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post("/api/auth/login", data);
      const { access_token, user } = response.data;
      setSession(access_token, user);
      router.push("/");
    } catch (err: unknown) {
      const axiosErr = err as AxiosError<{ detail?: string }>;
      setError(axiosErr.response?.data?.detail || "Ошибка входа. Попробуйте еще раз.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center p-4">
      <LiquidBlobBackground />
      <GlassPanel className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-white mb-6 font-display">
          Вход в GoodFilms
        </h1>
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-3 rounded-lg mb-4">
            {error}
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
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-sm font-medium text-gray-300">
                Пароль
              </label>
              <Link
                href="/forgot-password"
                className="text-xs text-gray-400 hover:text-[#E8B74C]"
              >
                Забыли пароль?
              </Link>
            </div>
            <input
              type="password"
              {...register("password")}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-[#E8B74C] transition-all text-base"
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
            )}
          </div>
          <Button
            type="submit"
            className="w-full mt-2"
            disabled={isLoading}
          >
            {isLoading ? "Вход..." : "Войти"}
          </Button>
        </form>
        <p className="text-center text-sm text-gray-400 mt-6">
          Нет аккаунта?{" "}
          <Link href="/register" className="text-[#6E5CFF] hover:text-[#5744ff] font-medium">
            Зарегистрироваться
          </Link>
        </p>
      </GlassPanel>
    </div>
  );
}
