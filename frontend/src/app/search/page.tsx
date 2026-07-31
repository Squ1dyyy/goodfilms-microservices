"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { MovieGrid } from "@/components/movie/MovieGrid";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { Film, User } from "lucide-react";
import { Button } from "@/components/ui/Button";

import { getImageUrl } from "@/components/movie/MovieCard";
import { useBookmarks } from "@/features/favorites/useBookmarks";

function SearchResults() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  const mpage = Number(searchParams.get("mpage")) || 1;
  const ppage = Number(searchParams.get("ppage")) || 1;
  const moviesLimit = 15;
  const personsLimit = 12;

  const { data: movies, isLoading: moviesLoading } = useQuery({
    queryKey: ["search-movies", query, mpage],
    queryFn: () => moviesQueries.getMovies({ search: query, page: mpage, limit: moviesLimit }),
    enabled: query.trim().length > 0,
  });

  const { data: persons, isLoading: personsLoading } = useQuery({
    queryKey: ["search-persons", query, ppage],
    queryFn: () => moviesQueries.getPersons(query, ppage, personsLimit),
    enabled: query.trim().length > 0,
  });

  if (!query.trim()) {
    return (
      <div className="text-center py-20 text-gray-400 text-lg">
        Введите поисковый запрос, чтобы начать поиск.
      </div>
    );
  }

  const isAnyLoading = moviesLoading || personsLoading;

  const totalMovies = movies?.total || 0;
  const totalMoviesPages = Math.ceil(totalMovies / moviesLimit);

  const totalPersons = persons?.total || 0;
  const totalPersonsPages = Math.ceil(totalPersons / personsLimit);

  const handlePageChange = (type: "movies" | "persons", nextPage: number) => {
    const nextParams = new URLSearchParams(searchParams.toString());
    if (type === "movies") {
      nextParams.set("mpage", String(nextPage));
    } else {
      nextParams.set("ppage", String(nextPage));
    }
    router.push(`${pathname}?${nextParams.toString()}`);
  };

  return (
    <div className="space-y-8">
      <h2 className="text-lg text-gray-400">
        Результаты поиска для: <span className="text-white font-bold font-display">&ldquo;{query}&rdquo;</span>
      </h2>

      {isAnyLoading ? (
        <div className="space-y-8">
          <div className="space-y-4">
            <ShimmerSkeleton className="h-8 w-48" />
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
              {[...Array(6)].map((_, i) => (
                <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-12">
          {/* Movies Result */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white font-display flex items-center gap-2">
              <Film size={20} className="text-[#6E5CFF]" /> Фильмы ({totalMovies})
            </h3>
            {movies && movies.items.length > 0 ? (
              <div className="space-y-6">
                <MovieGrid
                  movies={movies.items}
                  bookmarkedIds={bookmarkedIds}
                  onToggleBookmark={toggleBookmark}
                />
                
                {/* Movies Pagination Controls */}
                {totalMoviesPages > 1 && (
                  <div className="flex items-center justify-center gap-4 pt-4">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange("movies", mpage - 1)}
                      disabled={mpage <= 1}
                    >
                      Назад
                    </Button>
                    <span className="text-sm text-gray-400">
                      Страница {mpage} из {totalMoviesPages}
                    </span>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange("movies", mpage + 1)}
                      disabled={mpage >= totalMoviesPages}
                    >
                      Вперед
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Фильмы не найдены.</p>
            )}
          </div>

          {/* Persons Result */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-white font-display flex items-center gap-2">
              <User size={20} className="text-[#33D4C8]" /> Персоны ({totalPersons})
            </h3>
            {persons && persons.items.length > 0 ? (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
                  {persons.items.map((person) => (
                    <Link key={person.id} href={`/persons/${person.id}`}>
                      <GlassPanel className="p-4 flex flex-col items-center text-center space-y-3 hover:bg-white/[0.08] transition-all cursor-pointer h-full justify-between">
                        <div className="h-20 w-20 rounded-full overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center">
                          {person.photo_url ? (
                            <img
                              src={getImageUrl(person.photo_url, "w300")}
                              alt={person.full_name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <User size={32} className="text-gray-500" />
                          )}
                        </div>
                        <p className="text-sm font-bold text-white line-clamp-2">{person.full_name}</p>
                      </GlassPanel>
                    </Link>
                  ))}
                </div>

                {/* Persons Pagination Controls */}
                {totalPersonsPages > 1 && (
                  <div className="flex items-center justify-center gap-4 pt-4">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange("persons", ppage - 1)}
                      disabled={ppage <= 1}
                    >
                      Назад
                    </Button>
                    <span className="text-sm text-gray-400">
                      Страница {ppage} из {totalPersonsPages}
                    </span>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handlePageChange("persons", ppage + 1)}
                      disabled={ppage >= totalPersonsPages}
                    >
                      Вперед
                    </Button>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">Персоны не найдены.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <div className="relative min-h-screen p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-white font-display">Поиск</h1>
        <Suspense fallback={<div className="text-white text-center py-20">Выполнение поиска...</div>}>
          <SearchResults />
        </Suspense>
      </div>
    </div>
  );
}
