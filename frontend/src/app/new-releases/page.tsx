"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries, MovieQueryParams } from "@/features/movies/queries";
import { MovieGrid } from "@/components/movie/MovieGrid";
import { Button } from "@/components/ui/Button";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { useRouter, useSearchParams } from "next/navigation";
import { useBookmarks } from "@/features/favorites/useBookmarks";

function NewReleasesList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  const currentYear = new Date().getFullYear();
  const targetYearFrom = currentYear - 1; // e.g. 2025 for 2026

  // Read initial values from URL
  const initialSearch = searchParams.get("search") || "";
  const initialGenre = searchParams.get("genre_id") ? Number(searchParams.get("genre_id")) : "";
  const initialImdbVotesFrom = searchParams.get("imdb_votes_from") ? Number(searchParams.get("imdb_votes_from")) : "";
  const initialPage = searchParams.get("page") ? Number(searchParams.get("page")) : 1;

  // Filter States
  const [search, setSearch] = useState(initialSearch);
  const [genreId, setGenreId] = useState<number | "">(initialGenre);
  const [imdbVotesFrom, setImdbVotesFrom] = useState<number | "">(initialImdbVotesFrom);
  const [page, setPage] = useState(initialPage);
  const limit = 20;

  // Sync state with query changes
  useEffect(() => {
    let active = true;
    const searchVal = searchParams.get("search") || "";
    const genreVal = searchParams.get("genre_id") ? Number(searchParams.get("genre_id")) : "";
    const imdbVotesFromVal = searchParams.get("imdb_votes_from") ? Number(searchParams.get("imdb_votes_from")) : "";
    const pageVal = searchParams.get("page") ? Number(searchParams.get("page")) : 1;

    Promise.resolve().then(() => {
      if (active) {
        setSearch(searchVal);
        setGenreId(genreVal);
        setImdbVotesFrom(imdbVotesFromVal);
        setPage(pageVal);
      }
    });

    return () => {
      active = false;
    };
  }, [searchParams]);

  // Fetch справочники
  const { data: genres } = useQuery({
    queryKey: ["genres"],
    queryFn: moviesQueries.getGenres,
    staleTime: 24 * 60 * 60 * 1000,
  });

  // Fetch Movies
  const queryParams: MovieQueryParams = {
    page,
    limit,
    search: search || undefined,
    genre_id: genreId || undefined,
    year_from: targetYearFrom,
    imdb_votes_from: imdbVotesFrom || undefined,
  };

  const { data: moviesData, isLoading } = useQuery({
    queryKey: ["new-releases", queryParams],
    queryFn: () => moviesQueries.getMovies(queryParams),
  });

  const updateUrl = (updatedParams: Record<string, string | number | undefined | null>) => {
    const nextParams = new URLSearchParams(searchParams.toString());
    Object.entries(updatedParams).forEach(([key, val]) => {
      if (val === undefined || val === null || val === "") {
        nextParams.delete(key);
      } else {
        nextParams.set(key, String(val));
      }
    });
    router.push(`/new-releases?${nextParams.toString()}`);
  };

  const handleFilterChange = (key: string, value: string | number) => {
    const updated = {
      search: key === "search" ? (value as string) : search,
      genre_id: key === "genre_id" ? (value as number) : genreId,
      imdb_votes_from: key === "imdb_votes_from" ? (value as number) : imdbVotesFrom,
      page: 1, // reset page on filter change
    };
    updateUrl(updated);
  };

  const handlePageChange = (nextPage: number) => {
    updateUrl({ page: nextPage });
  };

  const handleReset = () => {
    setSearch("");
    setGenreId("");
    setImdbVotesFrom("");
    setPage(1);
    router.push("/new-releases");
  };

  const totalPages = moviesData ? Math.ceil(moviesData.total / limit) : 0;

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-white font-display">
            Новинки кино
          </h1>
          <p className="text-sm text-gray-400">
            Самые свежие поступления фильмов за {targetYearFrom}–{currentYear} годы.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
          {/* Left Column: Filter Panel */}
          <div className="lg:col-span-1">
            <GlassPanel className="flex flex-col gap-4 p-6">
              {/* Search */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Поиск</label>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onBlur={() => handleFilterChange("search", search)}
                  onKeyDown={(e) => e.key === "Enter" && handleFilterChange("search", search)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Название фильма..."
                />
              </div>

              {/* Genre */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Жанр</label>
                <select
                  value={genreId}
                  onChange={(e) => handleFilterChange("genre_id", e.target.value ? Number(e.target.value) : "")}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                >
                  <option value="" className="bg-[#0A0C14]">Все жанры</option>
                  {genres?.map((g) => (
                    <option key={g.id} value={g.id} className="bg-[#0A0C14]">
                      {g.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* IMDb Votes From */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Голосов IMDb (от)</label>
                <input
                  type="number"
                  min="0"
                  value={imdbVotesFrom}
                  onChange={(e) => setImdbVotesFrom(e.target.value ? Number(e.target.value) : "")}
                  onBlur={() => handleFilterChange("imdb_votes_from", imdbVotesFrom)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Например, 1000"
                />
              </div>

              {/* Reset Buttons */}
              <div className="flex items-end justify-end gap-2 mt-2">
                <Button variant="secondary" onClick={handleReset} className="w-full">
                  Сбросить фильтры
                </Button>
              </div>
            </GlassPanel>
          </div>

          {/* Right Column: Results Area */}
          <div className="lg:col-span-3">
            {isLoading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {[...Array(10)].map((_, i) => (
                  <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
                ))}
              </div>
            ) : !moviesData || moviesData.items.length === 0 ? (
              <div className="text-center py-12 text-gray-400 text-lg">
                Новинки кино с указанными фильтрами не найдены.
              </div>
            ) : (
              <div className="space-y-8">
                <MovieGrid
                  movies={moviesData.items}
                  bookmarkedIds={bookmarkedIds}
                  onToggleBookmark={toggleBookmark}
                />

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-4 pt-4">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange(page - 1)}
                      disabled={page <= 1}
                    >
                      Назад
                    </Button>
                    <span className="text-sm text-gray-400">
                      Страница {page} из {totalPages}
                    </span>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange(page + 1)}
                      disabled={page >= totalPages}
                    >
                      Вперед
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function NewReleasesPage() {
  return (
    <Suspense fallback={<div className="text-white text-center py-20">Загрузка новинок...</div>}>
      <NewReleasesList />
    </Suspense>
  );
}
