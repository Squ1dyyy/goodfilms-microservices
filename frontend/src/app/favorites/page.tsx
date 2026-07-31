"use client";

import React, { useEffect } from "react";
import { useBookmarks } from "@/features/favorites/useBookmarks";
import { useAuthStore } from "@/store/auth";
import { MovieGrid } from "@/components/movie/MovieGrid";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { Button } from "@/components/ui/Button";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function FavoritesPage() {
  const router = useRouter();
  const { accessToken, initialized } = useAuthStore();
  const { bookmarkedMovies, bookmarkedIds, toggleBookmark, isLoading } = useBookmarks();

  useEffect(() => {
    if (initialized && !accessToken) {
      router.push("/login");
    }
  }, [initialized, accessToken, router]);

  if (!initialized) {
    return (
      <div className="relative min-h-screen p-6 md:p-12">
        <LiquidBlobBackground />
        <div className="max-w-7xl mx-auto space-y-6">
          <ShimmerSkeleton className="h-10 w-48" />
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
              {[...Array(5)].map((_, i) => (
                <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
              ))}
            </div>
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
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-white font-display">
          Мои закладки
        </h1>

        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {[...Array(5)].map((_, i) => (
              <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
            ))}
          </div>
        ) : bookmarkedMovies.length === 0 ? (
          <div className="text-center py-20 space-y-4">
            <p className="text-gray-400 text-lg">Ваш список закладок пока пуст.</p>
            <Link href="/movies">
              <Button>Перейти в каталог</Button>
            </Link>
          </div>
        ) : (
          <MovieGrid
            movies={bookmarkedMovies}
            bookmarkedIds={bookmarkedIds}
            onToggleBookmark={toggleBookmark}
          />
        )}
      </div>
    </div>
  );
}
