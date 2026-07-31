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

function ComingSoonList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  const currentYear = new Date().getFullYear();
  const targetYearFrom = currentYear + 1; // e.g. 2027 for 2026

  // Read initial values from URL
  const initialSearch = searchParams.get("search") || "";
  const initialGenre = searchParams.get("genre_id") ? Number(searchParams.get("genre_id")) : "";
  const initialPage = searchParams.get("page") ? Number(searchParams.get("page")) : 1;

  // Filter States
  const [search, setSearch] = useState(initialSearch);
  const [genreId, setGenreId] = useState<number | "">(initialGenre);
  const [page, setPage] = useState(initialPage);
  const limit = 20;

  // Sync state with query changes
  useEffect(() => {
    let active = true;
    const searchVal = searchParams.get("search") || "";
    const genreVal = searchParams.get("genre_id") ? Number(searchParams.get("genre_id")) : "";
    const pageVal = searchParams.get("page") ? Number(searchParams.get("page")) : 1;

    Promise.resolve().then(() => {
      if (active) {
        setSearch(searchVal);
        setGenreId(genreVal);
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
  };

  const { data: moviesData, isLoading } = useQuery({
    queryKey: ["coming-soon", queryParams],
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
    router.push(`/coming-soon?${nextParams.toString()}`);
  };

  const handleFilterChange = (key: string, value: string | number) => {
    const updated = {
      search: key === "search" ? (value as string) : search,
      genre_id: key === "genre_id" ? (value as number) : genreId,
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
    setPage(1);
    router.push("/coming-soon");
  };

  const totalPages = moviesData ? Math.ceil(moviesData.total / limit) : 0;

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold text-white font-display">
            Ожидаемые премьеры
          </h1>
          <p className="text-sm text-gray-400">
            Фильмы, которые выйдут в {targetYearFrom} году и позже. Добавляйте в закладки, чтобы не пропустить!
          </p>
        </div>

        {/* Filter Panel */}
        <GlassPanel className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-6">
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

          {/* Reset Buttons */}
          <div className="flex items-end justify-end">
            <Button variant="secondary" onClick={handleReset} className="w-full sm:w-auto">
              Сбросить фильтры
            </Button>
          </div>
        </GlassPanel>

        {/* Results Area */}
        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {[...Array(10)].map((_, i) => (
              <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
            ))}
          </div>
        ) : !moviesData || moviesData.items.length === 0 ? (
          <div className="text-center py-12 text-gray-400 text-lg">
            Ожидаемые премьеры с указанными фильтрами не найдены.
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
  );
}

export default function ComingSoonPage() {
  return (
    <Suspense fallback={<div className="text-white text-center py-20">Загрузка премьер...</div>}>
      <ComingSoonList />
    </Suspense>
  );
}
