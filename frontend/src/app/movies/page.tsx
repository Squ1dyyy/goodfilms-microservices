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

function MoviesList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  // Helper for numeric param parsing from searchParams
  const getNumParam = (param: string): number | undefined => {
    const val = searchParams.get(param);
    if (!val || val.trim() === "" || isNaN(Number(val))) return undefined;
    return Number(val);
  };

  // Initial values from URL
  const initialSearch = searchParams.get("search") || "";
  const initialMediaType = searchParams.get("media_type") || "";
  const initialGenre = getNumParam("genre_id");
  const initialYearFrom = getNumParam("year_from");
  const initialYearTo = getNumParam("year_to");
  const initialImdbVotesFrom = getNumParam("imdb_votes_from");
  const initialImdbRatingFrom = getNumParam("imdb_rating_from");
  const initialSortBy = searchParams.get("sort_by") || "";
  const initialPage = getNumParam("page") || 1;

  // React State for 0ms synchronous UI updates
  const [search, setSearch] = useState(initialSearch);
  const [mediaType, setMediaType] = useState<string>(initialMediaType);
  const [genreId, setGenreId] = useState<number | undefined>(initialGenre);
  const [yearFrom, setYearFrom] = useState<number | undefined>(initialYearFrom);
  const [yearTo, setYearTo] = useState<number | undefined>(initialYearTo);
  const [imdbVotesFrom, setImdbVotesFrom] = useState<number | undefined>(initialImdbVotesFrom);
  const [imdbRatingFrom, setImdbRatingFrom] = useState<number | undefined>(initialImdbRatingFrom);
  const [sortBy, setSortBy] = useState<string>(initialSortBy);
  const [page, setPage] = useState<number>(initialPage);

  // Inputs for text boxes
  const [searchInput, setSearchInput] = useState(initialSearch);
  const [yearFromInput, setYearFromInput] = useState<number | "">(initialYearFrom ?? "");
  const [yearToInput, setYearToInput] = useState<number | "">(initialYearTo ?? "");
  const [imdbVotesInput, setImdbVotesInput] = useState<number | "">(initialImdbVotesFrom ?? "");
  const [imdbRatingInput, setImdbRatingInput] = useState<number | "">(initialImdbRatingFrom ?? "");

  const limit = 20;

  // Sync state with URL when browser Back/Forward is clicked
  useEffect(() => {
    const s = searchParams.get("search") || "";
    const mt = searchParams.get("media_type") || "";
    const g = getNumParam("genre_id");
    const yf = getNumParam("year_from");
    const yt = getNumParam("year_to");
    const iv = getNumParam("imdb_votes_from");
    const ir = getNumParam("imdb_rating_from");
    const sb = searchParams.get("sort_by") || "";
    const p = getNumParam("page") || 1;

    setSearch(s);
    setSearchInput(s);
    setMediaType(mt);
    setGenreId(g);
    setYearFrom(yf);
    setYearFromInput(yf ?? "");
    setYearTo(yt);
    setYearToInput(yt ?? "");
    setImdbVotesFrom(iv);
    setImdbVotesInput(iv ?? "");
    setImdbRatingFrom(ir);
    setImdbRatingInput(ir ?? "");
    setSortBy(sb);
    setPage(p);
  }, [searchParams]);

  // Fetch genres
  const { data: genres } = useQuery({
    queryKey: ["genres"],
    queryFn: moviesQueries.getGenres,
    staleTime: 24 * 60 * 60 * 1000,
  });

  // Fetch Movies / Media using React state
  const queryParams: MovieQueryParams = {
    page,
    limit,
    search: search || undefined,
    media_type: mediaType || undefined,
    genre_id: genreId,
    year_from: yearFrom,
    year_to: yearTo,
    imdb_votes_from: imdbVotesFrom,
    imdb_rating_from: imdbRatingFrom,
    sort_by: sortBy || undefined,
  };

  const { data: moviesData, isLoading, isFetching } = useQuery({
    queryKey: ["movies", queryParams],
    queryFn: () => moviesQueries.getMovies(queryParams),
  });

  const updateUrl = (updatedParams: Record<string, string | number | undefined | null>) => {
    const nextParams = new URLSearchParams(searchParams.toString());

    // Purge empty parameters
    Array.from(nextParams.keys()).forEach((k) => {
      const v = nextParams.get(k);
      if (v === "" || v === null || v === "undefined" || v === "null") {
        nextParams.delete(k);
      }
    });

    Object.entries(updatedParams).forEach(([key, val]) => {
      if (val === undefined || val === null || val === "" || Number.isNaN(val)) {
        nextParams.delete(key);
      } else {
        nextParams.set(key, String(val));
      }
    });

    const queryString = nextParams.toString();
    router.push(queryString ? `/movies?${queryString}` : "/movies");
  };

  const handleFilterChange = (key: string, value: string | number | undefined | null) => {
    setPage(1);

    if (key === "search") setSearch((value as string) || "");
    if (key === "media_type") setMediaType((value as string) || "");
    if (key === "genre_id") setGenreId(value ? Number(value) : undefined);
    if (key === "year_from") setYearFrom(value ? Number(value) : undefined);
    if (key === "year_to") setYearTo(value ? Number(value) : undefined);
    if (key === "imdb_votes_from") setImdbVotesFrom(value ? Number(value) : undefined);
    if (key === "imdb_rating_from") setImdbRatingFrom(value ? Number(value) : undefined);
    if (key === "sort_by") setSortBy((value as string) || "");

    const updated = {
      search: key === "search" ? value : search,
      media_type: key === "media_type" ? value : mediaType,
      genre_id: key === "genre_id" ? value : genreId,
      year_from: key === "year_from" ? value : yearFrom,
      year_to: key === "year_to" ? value : yearTo,
      imdb_votes_from: key === "imdb_votes_from" ? value : imdbVotesFrom,
      imdb_rating_from: key === "imdb_rating_from" ? value : imdbRatingFrom,
      sort_by: key === "sort_by" ? value : sortBy,
      page: 1,
    };
    updateUrl(updated);
  };

  const handlePageChange = (nextPage: number) => {
    setPage(nextPage);
    window.scrollTo({ top: 0, behavior: "smooth" });
    updateUrl({ page: nextPage });
  };

  const handleReset = () => {
    setSearch("");
    setSearchInput("");
    setMediaType("");
    setGenreId(undefined);
    setYearFrom(undefined);
    setYearFromInput("");
    setYearTo(undefined);
    setYearToInput("");
    setImdbVotesFrom(undefined);
    setImdbVotesInput("");
    setImdbRatingFrom(undefined);
    setImdbRatingInput("");
    setSortBy("");
    setPage(1);
    router.push("/movies");
  };

  const totalPages = moviesData ? Math.ceil(moviesData.total / limit) : 0;

  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h1 className="text-4xl font-bold text-white font-display">
            Каталог фильмов и сериалов
          </h1>

          {/* Media Type Tabs Header */}
          <div className="flex items-center gap-1.5 p-1 bg-white/5 border border-white/10 rounded-xl">
            <button
              onClick={() => handleFilterChange("media_type", undefined)}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${!mediaType
                ? "bg-[#6E5CFF] text-white shadow-lg"
                : "text-gray-400 hover:text-white"
                }`}
            >
              Все
            </button>
            <button
              onClick={() => handleFilterChange("media_type", "movie")}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${mediaType === "movie"
                ? "bg-[#01b4e4] text-white shadow-lg"
                : "text-gray-400 hover:text-white"
                }`}
            >
              🎬 Фильмы
            </button>
            <button
              onClick={() => handleFilterChange("media_type", "tv")}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${mediaType === "tv"
                ? "bg-[#6E5CFF] text-white shadow-lg"
                : "text-gray-400 hover:text-white"
                }`}
            >
              📺 Сериалы
            </button>
          </div>
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
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onBlur={() => handleFilterChange("search", searchInput)}
                  onKeyDown={(e) => e.key === "Enter" && handleFilterChange("search", searchInput)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Название фильма или сериала..."
                />
              </div>

              {/* Media Type Selector */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Тип медиа</label>
                <select
                  value={mediaType || ""}
                  onChange={(e) => handleFilterChange("media_type", e.target.value || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                >
                  <option value="" className="bg-[#0A0C14]">Все типы</option>
                  <option value="movie" className="bg-[#0A0C14]">Фильмы</option>
                  <option value="tv" className="bg-[#0A0C14]">Сериалы</option>
                </select>
              </div>

              {/* Sort By */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Сортировка</label>
                <select
                  value={sortBy || ""}
                  onChange={(e) => handleFilterChange("sort_by", e.target.value || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                >
                  <option value="" className="bg-[#0A0C14]">Случайные (По умолчанию)</option>
                  <option value="tmdb_rating" className="bg-[#0A0C14]">По рейтингу TMDb</option>
                  <option value="tmdb_votes" className="bg-[#0A0C14]">По популярности TMDb</option>
                  <option value="imdb_rating" className="bg-[#0A0C14]">По рейтингу IMDb</option>
                  <option value="imdb_votes" className="bg-[#0A0C14]">По популярности IMDb</option>
                  <option value="release_year_desc" className="bg-[#0A0C14]">Сначала новые</option>
                  <option value="release_year_asc" className="bg-[#0A0C14]">Сначала старые</option>
                  <option value="random" className="bg-[#0A0C14]">Перемешать (Случайные)</option>
                </select>
              </div>

              {/* Genre */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Жанр</label>
                <select
                  value={genreId || ""}
                  onChange={(e) => handleFilterChange("genre_id", e.target.value ? Number(e.target.value) : undefined)}
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

              {/* Year From */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Год выпуска (от)</label>
                <input
                  type="number"
                  value={yearFromInput}
                  onChange={(e) => setYearFromInput(e.target.value ? Number(e.target.value) : "")}
                  onBlur={() => handleFilterChange("year_from", yearFromInput || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Например, 2010"
                />
              </div>

              {/* Year To */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Год выпуска (до)</label>
                <input
                  type="number"
                  value={yearToInput}
                  onChange={(e) => setYearToInput(e.target.value ? Number(e.target.value) : "")}
                  onBlur={() => handleFilterChange("year_to", yearToInput || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Например, 2025"
                />
              </div>

              {/* IMDb Votes From */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Кол-во оценок IMDb (от)</label>
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={imdbVotesInput}
                  onChange={(e) => setImdbVotesInput(e.target.value ? Number(e.target.value) : "")}
                  onBlur={() => handleFilterChange("imdb_votes_from", imdbVotesInput || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Например, 10000"
                />
              </div>

              {/* IMDb Rating From */}
              <div className="space-y-1">
                <label className="text-xs font-semibold text-gray-400">Рейтинг IMDb (от)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="10"
                  value={imdbRatingInput}
                  onChange={(e) => setImdbRatingInput(e.target.value ? Number(e.target.value) : "")}
                  onBlur={() => handleFilterChange("imdb_rating_from", imdbRatingInput || undefined)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-white outline-none focus:border-[#E8B74C] transition-all text-sm"
                  placeholder="Например, 7.0"
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
            {isLoading || isFetching ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {[...Array(10)].map((_, i) => (
                  <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
                ))}
              </div>
            ) : !moviesData || moviesData.items.length === 0 ? (
              <div className="text-center py-12 text-gray-400 text-lg">
                Медиафайлы с указанными фильтрами не найдены.
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
                    <span className="text-sm text-gray-400 font-medium">
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

export default function MoviesPage() {
  return (
    <Suspense fallback={<div className="text-white text-center py-20">Загрузка каталога...</div>}>
      <MoviesList />
    </Suspense>
  );
}
