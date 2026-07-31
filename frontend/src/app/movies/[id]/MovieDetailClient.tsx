"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useQuery } from "@tanstack/react-query";
import { moviesQueries } from "@/features/movies/queries";
import { GlassPanel } from "@/components/glass/GlassPanel";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";
import { Button } from "@/components/ui/Button";
import Link from "next/link";
import { useBookmarks } from "@/features/favorites/useBookmarks";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "next/navigation";
import { ArrowLeft, User, Star, Play } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { WatchProvidersRow } from "@/components/movie/WatchProvidersRow";
import { FEATURE_RECOMMENDATIONS } from "@/lib/feature-flags";
import { ComingSoonState } from "@/components/ui/ComingSoonState";
import { MovieCard, getImageUrl } from "@/components/movie/MovieCard";
import { MovieDetail, MovieListItem, CastMember } from "@/types/movie";
import { ApiError } from "@/lib/api-client";
import { ReviewsSection } from "@/features/reviews/ReviewsSection";
import { useReviews } from "@/features/reviews/useReviews";

interface MovieDetailClientProps {
  movie: MovieDetail;
}

function getYouTubeVideoId(input?: string | null): string | null {
  if (!input) return null;
  const str = input.trim();
  if (/^[A-Za-z0-9_-]{11}$/.test(str)) {
    return str;
  }
  const match = str.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([\w-]{11})/);
  return match ? match[1] : null;
}

export default function MovieDetailClient({ movie }: MovieDetailClientProps) {
  const router = useRouter();
  const { accessToken } = useAuthStore();
  const { bookmarkedIds, toggleBookmark } = useBookmarks();
  
  const [hoverRating, setHoverRating] = useState<number | null>(null);
  const [showTrailerModal, setShowTrailerModal] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);
  
  const { rateMovie, isRating } = useReviews(movie.id);

  // Image & Video URLs
  const posterUrl = getImageUrl(movie.poster_url, "w500");
  const backdropUrl = getImageUrl(movie.backdrop_url, "original");
  const youtubeId = getYouTubeVideoId(movie.trailer_url);

  // Lock body scroll when popup modal is open
  useEffect(() => {
    if (showTrailerModal) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [showTrailerModal]);

  // Fetch local ratings summary
  const { data: ratingsData, isLoading: ratingsLoading } = useQuery({
    queryKey: ["movie-ratings", movie.id],
    queryFn: () => moviesQueries.getMovieRatings(movie.id),
  });

  const isBookmarked = bookmarkedIds.includes(movie.id);

  const handleBookmarkToggle = () => {
    if (!accessToken) {
      router.push("/login");
      return;
    }
    toggleBookmark(movie.id);
  };

  const handleRate = async (value: number) => {
    if (!accessToken) {
      router.push("/login");
      return;
    }
    try {
      await rateMovie(value);
    } catch (err) {
      console.error("Failed to submit rating", err);
    }
  };

  // Ratings
  const imdbRating = movie.imdb_rating;
  const imdbVotes = movie.imdb_votes;
  const tmdbRating = movie.tmdb_rating ?? movie.kinopoisk_rating;
  const tmdbVotes = movie.tmdb_votes ?? movie.kinopoisk_votes;

  const imdbRatingStr = imdbRating !== undefined && imdbRating !== null ? imdbRating.toFixed(1) : "—";
  const imdbVotesStr = imdbVotes !== undefined && imdbVotes !== null ? imdbVotes.toLocaleString("ru-RU") : "0";
  const tmdbRatingStr = tmdbRating !== undefined && tmdbRating !== null ? tmdbRating.toFixed(1) : "—";
  const tmdbVotesStr = tmdbVotes !== undefined && tmdbVotes !== null ? tmdbVotes.toLocaleString("ru-RU") : "0";

  const imdbUrl = movie.imdb_id
    ? `https://www.imdb.com/title/${movie.imdb_id}/`
    : `https://www.imdb.com/find?q=${encodeURIComponent(movie.title)}`;

  const isTv = movie.media_type === "tv";
  const tmdbUrl = movie.tmdb_id
    ? `https://www.themoviedb.org/${isTv ? "tv" : "movie"}/${movie.tmdb_id}`
    : `https://www.themoviedb.org/search?query=${encodeURIComponent(movie.title)}`;

  return (
    <div className="relative min-h-screen p-6 md:p-12 overflow-hidden">
      {/* Full-Screen Ambient Backdrop Image */}
      {backdropUrl && (
        <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden select-none">
          <motion.div
            animate={{
              opacity: [0.35, 0.55, 0.35],
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 12,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
            }}
            className="absolute top-0 left-0 right-0 h-[750px] bg-cover bg-center blur-sm"
            style={{
              backgroundImage: `url(${backdropUrl})`,
              maskImage: "linear-gradient(to bottom, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%)",
              WebkitMaskImage: "linear-gradient(to bottom, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%)",
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0A0C14]/30 to-transparent" />
        </div>
      )}

      <div className="relative z-10 max-w-6xl mx-auto space-y-8">
        {/* Back Button */}
        <div>
          <Link href="/movies">
            <Button variant="secondary" size="sm" className="gap-2">
              <ArrowLeft size={16} /> Назад в каталог
            </Button>
          </Link>
        </div>

        {/* Movie Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Poster Container */}
          <div className="md:col-span-1">
            <div className="glass-surface rounded-2xl overflow-hidden aspect-[2/3] w-full bg-white/5 flex items-center justify-center relative shadow-2xl">
              {posterUrl ? (
                <motion.img
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4 }}
                  src={posterUrl}
                  alt={movie.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span className="text-gray-500 font-bold">Нет постера</span>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="md:col-span-2 space-y-6">
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <h1 className="text-4xl md:text-5xl font-extrabold text-white font-display">
                      {movie.title}
                    </h1>
                    {/* Media Type Badge */}
                    {isTv ? (
                      <span className="px-3 py-1 text-xs font-bold rounded-lg bg-[#6E5CFF]/90 text-white border border-[#6E5CFF]/40 shadow-lg">
                        Сериал
                      </span>
                    ) : (
                      <span className="px-3 py-1 text-xs font-bold rounded-lg bg-[#01b4e4]/90 text-white border border-[#01b4e4]/40 shadow-lg">
                        Фильм
                      </span>
                    )}
                  </div>

                  {/* Original Title right below main title */}
                  {movie.original_title && (
                    <p className="text-lg md:text-xl text-gray-400 font-medium italic">
                      {movie.original_title}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-3 shrink-0 self-start">
                  {youtubeId && (
                    <Button
                      variant="primary"
                      size="sm"
                      className="gap-2 bg-red-600 hover:bg-red-500 text-white font-semibold border-none shadow-lg shadow-red-600/20 cursor-pointer"
                      onClick={() => setShowTrailerModal(true)}
                    >
                      <Play size={16} className="fill-white text-white" /> Трейлер со звуком
                    </Button>
                  )}
                  <Button
                    variant={isBookmarked ? "secondary" : "primary"}
                    size="sm"
                    className="gap-2"
                    onClick={handleBookmarkToggle}
                  >
                    <Star size={16} className={isBookmarked ? "fill-[#E8B74C] text-[#E8B74C]" : "text-white"} />
                    {isBookmarked ? "В закладках" : "В закладки"}
                  </Button>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-400">
                <span>{movie.release_year} год</span>
                <span>•</span>
                <div className="flex gap-1.5">
                  {movie.genres?.map((g) => (
                    <span
                      key={g}
                      className="px-2.5 py-0.5 rounded-full bg-white/10 text-white font-medium text-xs"
                    >
                      {g}
                    </span>
                  ))}
                </div>
              </div>

              {/* Ratings Badges Row */}
              <div className="flex flex-wrap items-center gap-3 pt-2 text-sm">
                {/* Platform */}
                <div className="flex items-center gap-1.5 text-white bg-white/5 border border-white/10 px-3 py-1.5 rounded-xl">
                  <Star className="fill-[#E8B74C] text-[#E8B74C]" size={14} />
                  <span className="font-semibold text-gray-300">
                    <span className="text-[#6E5CFF]">G</span>F:
                  </span>
                  <span className="font-bold text-[#E8B74C]">
                    {ratingsLoading ? "..." : (ratingsData?.average_rating ? ratingsData.average_rating.toFixed(1) : "0.0")}
                  </span>
                  {!ratingsLoading && ratingsData?.total_ratings !== undefined && (
                    <span className="text-gray-500 text-xs">
                      ({ratingsData.total_ratings})
                    </span>
                  )}
                </div>

                {/* IMDb */}
                <a
                  href={imdbUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-white bg-white/5 hover:bg-white/10 border border-white/10 hover:border-[#F5C518]/50 px-3 py-1.5 rounded-xl transition-all cursor-pointer hover:text-[#F5C518]"
                  title="Открыть на IMDb"
                >
                  <span className="px-1.5 py-0.2 text-[9px] font-extrabold rounded bg-[#F5C518] text-black select-none leading-normal">
                    IMDb
                  </span>
                  <span className="font-bold text-gray-200">{imdbRatingStr}</span>
                  <span className="text-gray-500 text-xs">/ 10</span>
                  {imdbVotes && imdbVotes > 0 ? (
                    <span className="text-gray-500 text-xs">({imdbVotesStr})</span>
                  ) : null}
                </a>

                {/* TMDb */}
                <a
                  href={tmdbUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-white bg-white/5 hover:bg-white/10 border border-white/10 hover:border-[#01b4e4]/50 px-3 py-1.5 rounded-xl transition-all cursor-pointer hover:text-[#01b4e4]"
                  title="Открыть на TMDb"
                >
                  <span className="px-1.5 py-0.2 text-[9px] font-extrabold rounded bg-[#01b4e4] text-white select-none leading-normal">
                    TMDb
                  </span>
                  <span className="font-bold text-gray-200">{tmdbRatingStr}</span>
                  <span className="text-gray-500 text-xs">/ 10</span>
                  {tmdbVotes && tmdbVotes > 0 ? (
                    <span className="text-gray-500 text-xs">({tmdbVotesStr})</span>
                  ) : null}
                </a>
              </div>
            </div>

            <GlassPanel className="space-y-4">
              <h3 className="text-lg font-bold text-white font-display">Описание</h3>
              <p className="text-gray-300 leading-relaxed">{movie.description || "Описание отсутствует."}</p>
            </GlassPanel>

            {movie.studios && movie.studios.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-gray-400">Студии производства:</h4>
                <div className="flex flex-wrap gap-2">
                  {movie.studios.map((s) => (
                    <span
                      key={s}
                      className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-sm text-white"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Full-width Rating Input Panel */}
        <GlassPanel className="p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <span className="text-base font-bold text-white font-display">Ваша оценка фильма</span>
            <span className="text-xs font-bold text-[#E8B74C] bg-[#E8B74C]/10 border border-[#E8B74C]/20 px-2.5 py-1 rounded-lg">
              {hoverRating ? `Оценить: ${hoverRating} / 10` : "Наведите на звёзды, чтобы поставить свою оценку"}
            </span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pt-2">
            {/* Stars */}
            <div className="flex items-center gap-1.5 flex-grow justify-between">
              {Array.from({ length: 10 }, (_, i) => {
                const starVal = i + 1;
                const displayRating = hoverRating !== null ? hoverRating : (ratingsData?.average_rating || 0);
                const isActive = starVal <= Math.round(displayRating);
                
                return (
                  <motion.button
                    key={starVal}
                    whileHover={{ scale: 1.3 }}
                    whileTap={{ scale: 0.85 }}
                    onMouseEnter={() => setHoverRating(starVal)}
                    onMouseLeave={() => setHoverRating(null)}
                    onClick={() => handleRate(starVal)}
                    disabled={isRating}
                    className="p-1 focus:outline-none flex-grow flex justify-center cursor-pointer"
                  >
                    <Star
                      size={24}
                      className={`transition-colors duration-150 ${
                        isActive
                          ? "fill-[#E8B74C] text-[#E8B74C]"
                          : "text-gray-700 hover:text-[#E8B74C]"
                      }`}
                    />
                  </motion.button>
                );
              })}
            </div>

            {/* Score display to the right of the stars */}
            <div className="flex items-baseline gap-1.5 text-white shrink-0 pl-6 border-t md:border-t-0 md:border-l border-white/10 pt-4 md:pt-0 justify-center">
              <span className="text-3xl font-black text-[#E8B74C] font-display leading-none">
                {ratingsLoading ? "..." : (ratingsData?.average_rating ? ratingsData.average_rating.toFixed(1) : "0.0")}
              </span>
              <span className="text-gray-500 text-xs">/ 10</span>
              {!ratingsLoading && ratingsData?.total_ratings !== undefined && (
                <span className="text-xs text-gray-400 font-medium ml-1">
                  ({ratingsData.total_ratings} {ratingsData.total_ratings === 1 ? "оценка" : ratingsData.total_ratings > 1 && ratingsData.total_ratings < 5 ? "оценки" : "оценок"})
                </span>
              )}
            </div>
          </div>
        </GlassPanel>

        {/* Watch Providers Slot */}
        <WatchProvidersRow movieId={movie.id} />

        {/* Cast & Crew: 2 Rows with Horizontal Scroll */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white font-display">Актеры и съемочная группа</h2>
          
          <div className="overflow-x-auto pb-4 pt-1 scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
            <div className="grid grid-rows-2 grid-flow-col gap-4 auto-cols-[160px] md:auto-cols-[180px]">
              {movie.cast?.map((member) => (
                <Link key={member.person_id} href={`/persons/${member.person_id}`} className="h-full">
                  <GlassPanel className="p-3 flex flex-col items-center text-center space-y-2 hover:bg-white/[0.08] transition-all cursor-pointer h-full justify-between group">
                    <div className="h-14 w-14 rounded-full overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
                      {member.photo_url ? (
                        <img
                          src={getImageUrl(member.photo_url, "w300")}
                          alt={member.full_name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-200"
                        />
                      ) : (
                        <User size={22} className="text-gray-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-xs font-bold text-white line-clamp-1 group-hover:text-[#E8B74C] transition-colors">
                        {member.full_name}
                      </p>
                      <p className="text-[11px] text-gray-400 line-clamp-1">
                        {member.character_name || "Актер"}
                      </p>
                    </div>
                  </GlassPanel>
                </Link>
              ))}

              {movie.directors?.map((director: CastMember) => (
                <Link key={`dir-${director.person_id}`} href={`/persons/${director.person_id}`} className="h-full">
                  <GlassPanel className="p-3 flex flex-col items-center text-center space-y-2 hover:bg-white/[0.08] transition-all cursor-pointer h-full justify-between group">
                    <div className="h-14 w-14 rounded-full overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
                      {director.photo_url ? (
                        <img
                          src={getImageUrl(director.photo_url, "w300")}
                          alt={director.full_name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-200"
                        />
                      ) : (
                        <User size={22} className="text-gray-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-xs font-bold text-white line-clamp-1 group-hover:text-[#E8B74C] transition-colors">
                        {director.full_name}
                      </p>
                      <p className="text-[11px] text-gray-400">Режиссер</p>
                    </div>
                  </GlassPanel>
                </Link>
              ))}

              {movie.writers?.map((writer: CastMember) => (
                <Link key={`wri-${writer.person_id}`} href={`/persons/${writer.person_id}`} className="h-full">
                  <GlassPanel className="p-3 flex flex-col items-center text-center space-y-2 hover:bg-white/[0.08] transition-all cursor-pointer h-full justify-between group">
                    <div className="h-14 w-14 rounded-full overflow-hidden bg-white/5 border border-white/10 flex items-center justify-center shrink-0">
                      {writer.photo_url ? (
                        <img
                          src={getImageUrl(writer.photo_url, "w300")}
                          alt={writer.full_name}
                          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-200"
                        />
                      ) : (
                        <User size={22} className="text-gray-500" />
                      )}
                    </div>
                    <div>
                      <p className="text-xs font-bold text-white line-clamp-1 group-hover:text-[#E8B74C] transition-colors">
                        {writer.full_name}
                      </p>
                      <p className="text-[11px] text-gray-400">Сценарист</p>
                    </div>
                  </GlassPanel>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Similar movies & reviews */}
        <div className="space-y-12 pt-6">
          <SimilarMoviesSection movieId={movie.id} />
          <ReviewsSection movieId={movie.id} />
        </div>
      </div>

      {/* Popup Video Modal Portal */}
      {mounted && showTrailerModal && youtubeId && createPortal(
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[9999] bg-black/90 backdrop-blur-md flex items-center justify-center p-4 md:p-8"
            onClick={() => setShowTrailerModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative w-full max-w-4xl aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl border border-white/20"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setShowTrailerModal(false)}
                className="absolute top-4 right-4 z-50 p-2 rounded-full bg-black/70 hover:bg-black text-white transition-all cursor-pointer text-sm font-bold w-10 h-10 flex items-center justify-center border border-white/30 hover:scale-110 shadow-lg"
                title="Закрыть"
              >
                ✕
              </button>
              <iframe
                src={`https://www.youtube.com/embed/${youtubeId}?autoplay=1&controls=1&rel=0`}
                title={`${movie.title} - Трейлер`}
                className="w-full h-full border-none"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </motion.div>
          </motion.div>
        </AnimatePresence>,
        document.body
      )}
    </div>
  );
}

function SimilarMoviesSection({ movieId }: { movieId: number }) {
  const { bookmarkedIds, toggleBookmark } = useBookmarks();

  const { data, isLoading, error } = useQuery({
    queryKey: ["movie-similar", movieId],
    queryFn: () => moviesQueries.getSimilarMovies(movieId),
    enabled: Boolean(movieId),
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-2xl font-bold text-white font-display">Похожие медиа</h3>
        <div className="flex gap-6 overflow-x-auto pb-4">
          {[...Array(4)].map((_, i) => (
            <ShimmerSkeleton key={i} className="min-w-[180px] w-[180px] aspect-[2/3] flex-shrink-0" />
          ))}
        </div>
      </div>
    );
  }

  if (error || !data || !data.items || data.items.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-2xl font-bold text-white font-display">Похожие медиа</h3>
      <div className="flex gap-6 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {data.items.map((movie: MovieListItem) => (
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
