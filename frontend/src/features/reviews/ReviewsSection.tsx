"use client";

import React, { useState, useEffect } from "react";
import { useReviews } from "./useReviews";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { Button } from "@/components/ui/Button";
import { Star, Trash2, Send, MessageSquare, MailWarning, CheckCircle2, ShieldAlert } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { ReviewItem } from "@/types/movie";

interface ReviewsSectionProps {
  movieId: number;
}

export function ReviewsSection({ movieId }: ReviewsSectionProps) {
  const router = useRouter();
  const { user, accessToken } = useAuthStore();
  const {
    reviews,
    isLoading,
    addReview,
    isAddingReview,
    deleteReview,
    isDeletingReview,
  } = useReviews(movieId);

  const [reviewText, setReviewText] = useState("");
  const [userVerified, setUserVerified] = useState<boolean | null>(user?.is_verified ?? null);
  const [userEmail, setUserEmail] = useState<string>(user?.email || "");

  useEffect(() => {
    if (!accessToken) return;
    let active = true;
    apiClient.get("/auth/me").then((res) => {
      if (active && res.data) {
        setUserVerified(res.data.is_verified);
        if (res.data.email) setUserEmail(res.data.email);
        if (user) {
          useAuthStore.getState().setSession(accessToken, {
            ...user,
            is_verified: res.data.is_verified,
            email: res.data.email,
          });
        }
      }
    }).catch(() => {});
    return () => {
      active = false;
    };
  }, [accessToken]);

  const isVerified = userVerified === true || user?.is_verified === true;

  const handleAddReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken) {
      router.push("/login");
      return;
    }
    if (!isVerified) {
      router.push("/verify-email");
      return;
    }
    if (!reviewText.trim()) return;

    try {
      await addReview(reviewText.trim(), user?.username);
      setReviewText("");
    } catch (err: any) {
      const errorMessage =
        err?.response?.data?.detail ||
        err?.message ||
        "Добавлять отзывы могут только пользователи с подтверждённой почтой.";
      alert(errorMessage);
    }
  };

  const handleDeleteReview = async (reviewId: number) => {
    try {
      await deleteReview(reviewId);
    } catch (err) {
      console.error("Failed to delete review", err);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-2xl font-bold text-white font-display">Отзывы</h3>
        <ShimmerSkeleton className="h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h3 className="text-3xl font-extrabold text-white font-display tracking-tight">
        Отзывы
      </h3>

      <div className="space-y-6">
          {/* Write a Review */}
          <GlassPanel className="p-6 relative overflow-hidden border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-bold text-white font-display">
                Оставить отзыв
              </h4>
              {accessToken && !isVerified && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  <MailWarning size={14} /> Требуется подтверждение почты
                </span>
              )}
            </div>

            {!accessToken ? (
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center space-y-3">
                <p className="text-sm text-gray-400">
                  Войдите в свой аккаунт, чтобы делиться мнением о фильмах.
                </p>
                <Button onClick={() => router.push("/login")} variant="primary" size="sm">
                  Войти в аккаунт
                </Button>
              </div>
            ) : !isVerified ? (
              <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-500/20 space-y-4">
                <div className="flex items-start gap-3">
                  <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                    <ShieldAlert size={22} />
                  </div>
                  <div className="space-y-1">
                    <h5 className="text-sm font-bold text-white">
                      Почему я не могу написать отзыв?
                    </h5>
                    <p className="text-xs text-amber-200/80 leading-relaxed">
                      Публикация комментариев доступна только пользователям с подтверждённой почтой{" "}
                      {userEmail && <span className="text-amber-300 font-semibold">{userEmail}</span>}. Это необходимо для защиты сообщества от спама и накруток.
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3 pt-1">
                  <Button
                    onClick={() => router.push("/verify-email")}
                    variant="primary"
                    size="sm"
                    className="gap-2 bg-amber-500 hover:bg-amber-400 text-black font-semibold border-none"
                  >
                    <CheckCircle2 size={15} /> Подтвердить Email сейчас
                  </Button>
                  <Button
                    onClick={() => router.push("/profile")}
                    variant="secondary"
                    size="sm"
                    className="text-xs"
                  >
                    Перейти в профиль
                  </Button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleAddReview} className="space-y-4">
                <div className="relative">
                  <textarea
                    rows={4}
                    value={reviewText}
                    onChange={(e) => setReviewText(e.target.value)}
                    placeholder="Поделитесь вашим мнением о фильме..."
                    disabled={isAddingReview}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-white/20 text-sm leading-relaxed resize-none disabled:opacity-50"
                  />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-500">
                    Автор: <span className="text-white font-medium">{user?.username}</span>
                  </span>
                  <Button
                    type="submit"
                    variant="primary"
                    size="sm"
                    className="gap-2"
                    disabled={isAddingReview || !reviewText.trim()}
                  >
                    <Send size={14} /> Отправить
                  </Button>
                </div>
              </form>
            )}
          </GlassPanel>

          {/* Reviews List */}
          <div className="space-y-4">
            <h4 className="text-xl font-bold text-white font-display flex items-center gap-2">
              <MessageSquare size={20} className="text-gray-400" />
              Отзывы пользователей ({reviews.length})
            </h4>

            {reviews.length === 0 ? (
              <div className="text-gray-500 text-sm py-8 text-center bg-white/5 rounded-xl border border-white/5">
                У этого фильма пока нет отзывов. Будьте первыми!
              </div>
            ) : (
              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                <AnimatePresence>
                  {reviews.map((rev: ReviewItem) => (
                    <motion.div
                      key={rev.id}
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -15 }}
                      transition={{ duration: 0.3 }}
                    >
                      <GlassPanel className="p-5 space-y-3 relative group">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-white text-sm">
                              {rev.user_id === user?.id && user
                                ? user.username.slice(0, 2).toUpperCase()
                                : rev.username
                                ? rev.username.slice(0, 2).toUpperCase()
                                : `U${rev.user_id}`}
                            </div>
                            <div>
                              <p className="text-sm font-bold text-white">
                                {rev.user_id === user?.id && user
                                  ? `${user.username} (Вы)`
                                  : rev.username || `Пользователь #${rev.user_id}`}
                              </p>
                              <p className="text-xs text-gray-500">
                                Опубликовано в GoodFilms
                              </p>
                            </div>
                          </div>

                          {/* Delete Action */}
                          {rev.user_id === user?.id && (
                            <button
                              onClick={() => handleDeleteReview(rev.id)}
                              disabled={isDeletingReview}
                              className="text-gray-500 hover:text-red-500 p-1.5 rounded-lg hover:bg-white/5 transition-colors"
                            >
                              <Trash2 size={16} />
                            </button>
                          )}
                        </div>
                        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line pl-12">
                          {rev.review}
                        </p>
                      </GlassPanel>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      </div>
  );
}
