"use client";

import React, { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { MovieGrid } from "@/components/movie/MovieGrid";
import { getImageUrl } from "@/components/movie/MovieCard";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { Button } from "@/components/ui/Button";
import { useBookmarks } from "@/features/favorites/useBookmarks";
import { Search, Film, X, Calendar, Plus, Sparkles, Filter } from "lucide-react";
import { MovieListItem } from "@/types/movie";

export default function CustomRecommendationsPage() {
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  // Selected movies for seed
  const [selectedMovies, setSelectedMovies] = useState<MovieListItem[]>([]);

  // Search state for autocomplete
  const [movieSearch, setMovieSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filters and Custom description text
  const [customDescription, setCustomDescription] = useState("");
  const [mediaType, setMediaType] = useState<string>("");
  const [releaseYear, setReleaseYear] = useState("");
  const [releaseYearFrom, setReleaseYearFrom] = useState("");
  const [releaseYearTo, setReleaseYearTo] = useState("");
  const [imdbRatingFrom, setImdbRatingFrom] = useState("");
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);

  // Request trigger state
  const [payload, setPayload] = useState<any>(null);

  // Debounce movie search input
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(movieSearch);
    }, 300);
    return () => clearTimeout(handler);
  }, [movieSearch]);

  // Click outside listener for search autocomplete dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsSearchDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch search suggestions
  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ["recommendation-movie-search", debouncedSearch],
    queryFn: () => moviesQueries.getMovies({ search: debouncedSearch, limit: 6 }),
    enabled: debouncedSearch.trim().length > 1,
  });

  // Fetch genres
  const { data: genres } = useQuery({
    queryKey: ["recommendation-genres"],
    queryFn: moviesQueries.getGenres,
    staleTime: 24 * 60 * 60 * 1000,
  });

  // Fetch recommendations
  const { data: recommendations, isLoading: isFetchingRecommendations, error } = useQuery({
    queryKey: ["custom-recommendations", payload],
    queryFn: () => moviesQueries.getCustomRecommendations(payload),
    enabled: payload !== null,
  });

  const handleSelectMovie = (movie: MovieListItem) => {
    if (!selectedMovies.some((m) => m.id === movie.id)) {
      setSelectedMovies([...selectedMovies, movie]);
    }
    setMovieSearch("");
    setIsSearchDropdownOpen(false);
  };

  const handleRemoveMovie = (id: number) => {
    setSelectedMovies(selectedMovies.filter((m) => m.id !== id));
  };

  const handleToggleGenre = (genreName: string) => {
    if (selectedGenres.includes(genreName)) {
      setSelectedGenres(selectedGenres.filter((g) => g !== genreName));
    } else {
      setSelectedGenres([...selectedGenres, genreName]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedMovies.length === 0 && !customDescription.trim()) {
      return;
    }
    setPayload({
      movie_ids: selectedMovies.map((m) => m.id),
      genres: selectedGenres,
      release_year: releaseYear ? parseInt(releaseYear, 10) : undefined,
      release_year_from: releaseYearFrom ? parseInt(releaseYearFrom, 10) : undefined,
      release_year_to: releaseYearTo ? parseInt(releaseYearTo, 10) : undefined,
      imdb_rating_from: imdbRatingFrom ? parseFloat(imdbRatingFrom) : undefined,
      media_type: mediaType || undefined,
      custom_description: customDescription.trim() || undefined,
      limit: 12,
    });
  };

  const handleReset = () => {
    setSelectedMovies([]);
    setCustomDescription("");
    setMediaType("");
    setReleaseYear("");
    setReleaseYearFrom("");
    setReleaseYearTo("");
    setImdbRatingFrom("");
    setSelectedGenres([]);
    setPayload(null);
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Page Header */}
      <div className="space-y-3">
        <h1 className="text-4xl font-extrabold text-white font-display flex items-center gap-3">
          <Sparkles className="text-[#6E5CFF] animate-pulse" size={32} />
          Умный подбор фильмов
        </h1>
        <p className="text-gray-400 max-w-3xl text-base leading-relaxed">
          Выберите несколько любимых фильмов, укажите жанры, год выпуска или опишите свои пожелания своими словами. Наша нейросеть проанализирует семантическое сходство описаний и подберет для вас наиболее подходящие картины.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Panel: Filters Form */}
        <div className="lg:col-span-5">
          <GlassPanel className="p-6 space-y-6">
            <h2 className="text-xl font-bold text-white font-display flex items-center gap-2 border-b border-white/5 pb-3">
              <Filter size={18} className="text-[#6E5CFF]" /> Параметры подбора
            </h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* 1. Movie Search Autocomplete */}
              <div className="space-y-2 relative" ref={dropdownRef}>
                <label className="block text-sm font-semibold text-gray-300">
                  Любимые фильмы (ориентиры)
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={movieSearch}
                    onChange={(e) => {
                      setMovieSearch(e.target.value);
                      setIsSearchDropdownOpen(true);
                    }}
                    onFocus={() => setIsSearchDropdownOpen(true)}
                    placeholder="Начните вводить название фильма..."
                    className="w-full pl-10 pr-4 py-2.5 bg-black/40 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-[#6E5CFF] focus:ring-1 focus:ring-[#6E5CFF]/30 transition-all text-sm"
                  />
                  <Search className="absolute left-3 top-3 text-gray-500" size={16} />
                </div>

                {isSearchDropdownOpen && movieSearch.trim().length > 1 && (
                  <div className="absolute z-50 w-full mt-1.5 bg-[#0F111A]/95 border border-white/15 rounded-xl shadow-2xl backdrop-blur-xl overflow-hidden max-h-60 overflow-y-auto">
                    {isSearching ? (
                      <div className="p-3 text-sm text-gray-400">Поиск вариантов...</div>
                    ) : searchResults && searchResults.items.length > 0 ? (
                      searchResults.items.map((m) => (
                        <button
                          key={m.id}
                          type="button"
                          onClick={() => handleSelectMovie(m)}
                          className="w-full text-left px-4 py-2.5 hover:bg-white/5 transition-all flex items-center justify-between text-sm"
                        >
                          <div className="flex items-center gap-3">
                            {m.poster_url ? (
                              <img src={getImageUrl(m.poster_url, "w300")} alt="" className="w-8 h-12 object-cover rounded-md flex-shrink-0" />
                            ) : (
                              <div className="w-8 h-12 bg-white/5 rounded-md flex-shrink-0 flex items-center justify-center"><Film size={12} /></div>
                            )}
                            <div>
                              <div className="font-medium text-white">{m.title}</div>
                              <div className="text-xs text-gray-500">{m.release_year}</div>
                            </div>
                          </div>
                          <Plus size={14} className="text-[#6E5CFF]" />
                        </button>
                      ))
                    ) : (
                      <div className="p-3 text-sm text-gray-400">Фильмы не найдены</div>
                    )}
                  </div>
                )}

                {/* Selected Movies List */}
                {selectedMovies.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {selectedMovies.map((movie) => (
                      <div
                        key={movie.id}
                        className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-full pl-3 pr-2 py-1 text-xs text-white"
                      >
                        <span className="truncate max-w-[150px]">{movie.title}</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveMovie(movie.id)}
                          className="text-gray-400 hover:text-white transition-colors"
                        >
                          <X size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 2. Media Type Selection */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-300">
                  Тип медиа
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setMediaType("")}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all ${mediaType === ""
                      ? "bg-[#6E5CFF] border-[#6E5CFF] text-white shadow-lg"
                      : "bg-black/40 border-white/10 text-gray-400 hover:text-white"
                      }`}
                  >
                    Все
                  </button>
                  <button
                    type="button"
                    onClick={() => setMediaType("movie")}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all ${mediaType === "movie"
                      ? "bg-[#01b4e4] border-[#01b4e4] text-white shadow-lg"
                      : "bg-black/40 border-white/10 text-gray-400 hover:text-white"
                      }`}
                  >
                    🎬 Фильмы
                  </button>
                  <button
                    type="button"
                    onClick={() => setMediaType("tv")}
                    className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all ${mediaType === "tv"
                      ? "bg-[#6E5CFF] border-[#6E5CFF] text-white shadow-lg"
                      : "bg-black/40 border-white/10 text-gray-400 hover:text-white"
                      }`}
                  >
                    📺 Сериалы
                  </button>
                </div>
              </div>

              {/* 3. Custom text description */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-300">
                  Пожелания / Сюжетные детали
                </label>
                <textarea
                  value={customDescription}
                  onChange={(e) => setCustomDescription(e.target.value)}
                  placeholder="Например: фильм про космические путешествия, чужие миры, искусственный интеллект, роботов или выживание в космосе"
                  rows={4}
                  className="w-full px-4 py-2.5 bg-black/40 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-[#6E5CFF] focus:ring-1 focus:ring-[#6E5CFF]/30 transition-all text-sm resize-none"
                />
              </div>

              {/* 4. Year Range inputs (From / To) */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-300">
                  Год выпуска (интервал)
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <div className="relative">
                    <input
                      type="number"
                      value={releaseYearFrom}
                      onChange={(e) => setReleaseYearFrom(e.target.value)}
                      placeholder="Год от (2010)"
                      min="1890"
                      max={new Date().getFullYear()}
                      className="w-full pl-9 pr-3 py-2 bg-black/40 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-[#6E5CFF] text-xs"
                    />
                    <Calendar className="absolute left-3 top-2.5 text-gray-500" size={14} />
                  </div>
                  <div className="relative">
                    <input
                      type="number"
                      value={releaseYearTo}
                      onChange={(e) => setReleaseYearTo(e.target.value)}
                      placeholder="Год до (2028)"
                      min="1890"
                      max={new Date().getFullYear() + 3}
                      className="w-full pl-9 pr-3 py-2 bg-black/40 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-[#6E5CFF] text-xs"
                    />
                    <Calendar className="absolute left-3 top-2.5 text-gray-500" size={14} />
                  </div>
                </div>
              </div>

              {/* 5. IMDb Rating input */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-300">
                  Рейтинг IMDb (от)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="10"
                  value={imdbRatingFrom}
                  onChange={(e) => setImdbRatingFrom(e.target.value)}
                  placeholder="Например: 7.0"
                  className="w-full px-4 py-2.5 bg-black/40 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-[#6E5CFF] focus:ring-1 focus:ring-[#6E5CFF]/30 transition-all text-sm"
                />
              </div>

              {/* 4. Genres selection */}
              {genres && genres.length > 0 && (
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-300">
                    Жанры
                  </label>
                  <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/5 scrollbar-track-transparent">
                    {genres.map((genre) => {
                      const isSelected = selectedGenres.includes(genre.name);
                      return (
                        <button
                          key={genre.id}
                          type="button"
                          onClick={() => handleToggleGenre(genre.name)}
                          className={`px-3 py-1.5 rounded-lg border text-left text-xs font-medium transition-all ${isSelected
                            ? "bg-[#6E5CFF]/15 border-[#6E5CFF] text-[#8C7EFF]"
                            : "bg-white/5 border-white/5 text-gray-400 hover:bg-white/10"
                            }`}
                        >
                          {genre.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4 border-t border-white/5">
                <Button
                  type="submit"
                  disabled={selectedMovies.length === 0 && !customDescription.trim()}
                  className="flex-grow bg-gradient-to-r from-[#6E5CFF] to-[#8C7EFF] hover:from-[#5C4EE5] hover:to-[#7B6CE5] text-white py-2.5"
                >
                  Подобрать кино
                </Button>
                {(selectedMovies.length > 0 || customDescription.trim() || releaseYear || selectedGenres.length > 0) && (
                  <Button
                    type="button"
                    onClick={handleReset}
                    className="border border-white/10 hover:bg-white/5 text-gray-300 py-2.5"
                  >
                    Сбросить
                  </Button>
                )}
              </div>
            </form>
          </GlassPanel>
        </div>

        {/* Right Panel: Results Grid */}
        <div className="lg:col-span-7">
          {isFetchingRecommendations ? (
            <div className="space-y-4">
              <ShimmerSkeleton className="h-8 w-48" />
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <ShimmerSkeleton key={i} className="aspect-[2/3] w-full" />
                ))}
              </div>
            </div>
          ) : recommendations ? (
            recommendations.length > 0 ? (
              <div className="space-y-4">
                <h3 className="text-2xl font-bold text-white font-display flex items-center gap-2">
                  <Film size={20} className="text-[#6E5CFF]" /> Мы подобрали для вас ({recommendations.length})
                </h3>
                <MovieGrid
                  movies={recommendations}
                  bookmarkedIds={bookmarkedIds}
                  onToggleBookmark={toggleBookmark}
                  className="grid grid-cols-2 sm:grid-cols-3 gap-6"
                />
              </div>
            ) : (
              <GlassPanel className="p-12 text-center space-y-4">
                <div className="text-gray-400 text-lg">По вашему запросу ничего не найдено.</div>
                <div className="text-gray-500 text-sm max-w-md mx-auto">
                  Попробуйте расширить критерии поиска: добавьте больше фильмов-ориентиров, сократите жанры или сделайте текстовое описание более общим.
                </div>
              </GlassPanel>
            )
          ) : (
            <GlassPanel className="p-16 text-center space-y-5">
              <div className="w-16 h-16 bg-[#6E5CFF]/10 text-[#6E5CFF] rounded-full flex items-center justify-center mx-auto">
                <Sparkles size={32} />
              </div>
              <div className="text-white font-bold text-xl font-display">Начните подбор</div>
              <div className="text-gray-400 text-sm max-w-sm mx-auto">
                Выберите один или несколько фильмов-ориентиров слева, при желании добавьте текстовое описание и нажмите кнопку «Подобрать кино».
              </div>
            </GlassPanel>
          )}
        </div>
      </div>
    </div>
  );
}
