"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { MovieCard } from "@/components/movie/MovieCard";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { GlassPanel } from "@/components/glass/GlassPanel";
import Link from "next/link";
import { Button } from "@/components/ui/Button";

import { useBookmarks } from "@/features/favorites/useBookmarks";
import { ScrollReveal } from "@/components/ui/ScrollReveal";
import { useAuthStore } from "@/store/auth";

import { MovieListResponse, MovieListItem } from "@/types/movie";

function MovieRow({
  title,
  queryKey,
  queryFn,
}: {
  title: string;
  queryKey: unknown[];
  queryFn: () => Promise<MovieListResponse>;
}) {
  const { data, isLoading } = useQuery({
    queryKey,
    queryFn,
  });
  
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  if (isLoading) {
    return (
      <div className="space-y-4 my-8">
        <h2 className="text-2xl font-bold text-white font-display">{title}</h2>
        <div className="flex gap-6 overflow-x-auto pb-4">
          {[...Array(6)].map((_, i) => (
            <ShimmerSkeleton key={i} className="min-w-[180px] w-[180px] aspect-[2/3] flex-shrink-0" />
          ))}
        </div>
      </div>
    );
  }

  const filteredItems = data?.items.filter((movie: MovieListItem) => {
    if (movie.is_adult) return false;
    if (movie.genres?.some((g) => ["adult", "для взрослых", "эротика", "erotica"].includes(g.toLowerCase()))) {
      return false;
    }
    return true;
  });

  if (!filteredItems || filteredItems.length === 0) return null;

  return (
    <div className="space-y-4 my-8">
      <h2 className="text-2xl font-bold text-white font-display">{title}</h2>
      <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {filteredItems.map((movie: MovieListItem) => (
          <div key={movie.id} className="min-w-[180px] w-[180px] flex-shrink-0">
            <MovieCard
              movie={movie}
              isBookmarked={bookmarkedIds.includes(movie.id)}
              onToggleBookmark={() => toggleBookmark(movie.id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

function GenreRow({ genreId, genreName }: { genreId: number; genreName: string }) {
  return (
    <MovieRow
      title={genreName}
      queryKey={["movies", { genre_id: genreId, limit: 10, is_adult: false }]}
      queryFn={() => moviesQueries.getMovies({ genre_id: genreId, limit: 10, is_adult: false })}
    />
  );
}

export default function HomePage() {
  const { accessToken } = useAuthStore();
  const currentYear = new Date().getFullYear();

  // Fetch genres
  const { data: genres, isLoading: genresLoading } = useQuery({
    queryKey: ["genres"],
    queryFn: moviesQueries.getGenres,
  });

  const safeGenres = genres?.filter(
    (g) =>
      g.id !== 12 &&
      !["adult", "для взрослых", "эротика", "erotica"].includes(g.name.toLowerCase())
  );

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Hero Section */}
        <GlassPanel className="flex flex-col md:flex-row items-center justify-between gap-8 py-12 md:py-16">
          <div className="space-y-4 max-w-xl text-center md:text-left">
            <h1 className="text-4xl md:text-5xl font-extrabold text-white font-display leading-tight">
              Откройте для себя мир идеального кино
            </h1>
            <p className="text-gray-400 text-lg">
              GoodFilms — ваш персональный проводник в мире кинематографа. Находите новинки, сохраняйте в закладки и отслеживайте любимых актеров.
            </p>
            <div className="flex flex-wrap justify-center md:justify-start gap-4 pt-2">
              <Link href="/movies">
                <Button size="lg">Смотреть каталог</Button>
              </Link>
              {!accessToken && (
                <Link href="/register">
                  <Button variant="secondary" size="lg">
                    Создать аккаунт
                  </Button>
                </Link>
              )}
            </div>
          </div>
          <div className="hidden md:block w-72 h-72 rounded-3xl bg-gradient-to-tr from-[#6E5CFF] to-[#33D4C8] opacity-20 blur-2xl animate-pulse" />
        </GlassPanel>

        {/* Collections */}
        <div className="space-y-6">
          {/* New Releases */}
          <ScrollReveal>
            <MovieRow
              title="Новинки кино"
              queryKey={["movies", { year_from: currentYear - 1, limit: 12, is_adult: false }]}
              queryFn={() =>
                moviesQueries.getMovies({ year_from: currentYear - 1, limit: 12, is_adult: false })
              }
            />
          </ScrollReveal>

          {/* Catalog Top */}
          <ScrollReveal>
            <MovieRow
              title="Топ каталога"
              queryKey={["movies", { limit: 12, is_adult: false }]}
              queryFn={() => moviesQueries.getMovies({ limit: 12, is_adult: false })}
            />
          </ScrollReveal>

          {/* By Genres */}
          {genresLoading ? (
            <div className="space-y-4">
              <ShimmerSkeleton className="h-8 w-48" />
              <div className="flex gap-6 overflow-x-auto pb-4">
                {[...Array(6)].map((_, i) => (
                  <ShimmerSkeleton key={i} className="min-w-[180px] w-[180px] aspect-[2/3] flex-shrink-0" />
                ))}
              </div>
            </div>
          ) : (
            safeGenres?.slice(0, 5).map((genre, idx) => (
              <ScrollReveal key={genre.id} delay={idx * 0.1}>
                <GenreRow genreId={genre.id} genreName={genre.name} />
              </ScrollReveal>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
