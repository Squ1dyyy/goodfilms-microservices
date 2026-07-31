"use client";

import React, { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { notFound } from "next/navigation";
import { LiquidBlobBackground } from "@/components/glass/LiquidBlobBackground";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { Button } from "@/components/ui/Button";
import { MovieGrid } from "@/components/movie/MovieGrid";
import { getImageUrl } from "@/components/movie/MovieCard";
import Link from "next/link";
import { ArrowLeft, User } from "lucide-react";
import { ApiError } from "@/lib/api-client";

import { useBookmarks } from "@/features/favorites/useBookmarks";
import { useSubscriptions } from "@/features/favorites/useSubscriptions";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function PersonDetailPage({ params }: PageProps) {
  const router = useRouter();
  const unwrappedParams = use(params);
  const personId = Number(unwrappedParams.id);
  const { accessToken } = useAuthStore();
  const { bookmarkedIds, toggleBookmark } = useBookmarks();
  const { subscribedIds, toggleSubscription } = useSubscriptions();

  if (isNaN(personId)) {
    notFound();
  }

  const { data: personData, isLoading, error } = useQuery({
    queryKey: ["person", personId],
    queryFn: () => moviesQueries.getPerson(personId),
  });

  if (error) {
    const apiErr = error as ApiError;
    if (apiErr.status === 404) {
      notFound();
    }
  }

  if (isLoading || !personData) {
    return (
      <div className="relative min-h-screen p-6 md:p-12">
        <LiquidBlobBackground />
        <div className="max-w-6xl mx-auto space-y-6">
          <ShimmerSkeleton className="h-10 w-24" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <ShimmerSkeleton className="aspect-square w-full rounded-full max-w-[200px] mx-auto md:col-span-1" />
            <div className="md:col-span-2 space-y-4">
              <ShimmerSkeleton className="h-12 w-3/4" />
              <ShimmerSkeleton className="h-6 w-1/4" />
              <ShimmerSkeleton className="h-40 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  const person = personData?.person;
  const movies = personData?.movies;

  if (!person) {
    return (
      <div className="relative min-h-screen p-6 md:p-12 text-center text-gray-400">
        <LiquidBlobBackground />
        <p>Информация о персоне не найдена.</p>
      </div>
    );
  }

  const isSubscribed = subscribedIds.includes(person.id);

  const handleSubscribeToggle = () => {
    if (!accessToken) {
      router.push("/login");
      return;
    }
    toggleSubscription(person.id);
  };

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <LiquidBlobBackground />
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Back Button */}
        <div>
          <Link href="/movies">
            <Button variant="secondary" size="sm" className="gap-2">
              <ArrowLeft size={16} /> Назад в каталог
            </Button>
          </Link>
        </div>

        {/* Person Bio */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          {/* Photo */}
          <div className="md:col-span-1 flex flex-col items-center">
            <div className="h-48 w-48 rounded-full overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center shadow-lg">
              {person.photo_url ? (
                <img
                  src={getImageUrl(person.photo_url, "w300")}
                  alt={person.full_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <User size={64} className="text-gray-500" />
              )}
            </div>
            {/* Subscribe Button */}
            <Button
              variant={isSubscribed ? "secondary" : "primary"}
              className="mt-4 w-full"
              onClick={handleSubscribeToggle}
            >
              {isSubscribed ? "Отписаться" : "Подписаться"}
            </Button>
          </div>

          {/* Details */}
          <div className="md:col-span-2 space-y-4">
            <h1 className="text-4xl md:text-5xl font-extrabold text-white font-display">
              {person.full_name}
            </h1>
            {person.birth_date && (
              <p className="text-sm text-gray-400">
                Дата рождения: <span className="text-white font-medium">{person.birth_date}</span>
              </p>
            )}
          </div>
        </div>

        {/* Filmography */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-white font-display">
            Фильмография ({movies?.total ?? 0})
          </h2>
          {movies?.items && movies.items.length > 0 ? (
            <MovieGrid
              movies={movies.items}
              bookmarkedIds={bookmarkedIds}
              onToggleBookmark={toggleBookmark}
            />
          ) : (
            <p className="text-gray-400 text-sm">У этой персоны пока нет фильмов в каталоге.</p>
          )}
        </div>
      </div>
    </div>
  );
}
