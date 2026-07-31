"use client";

import React, { useRef, useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { MovieListItem } from "@/types/movie";
import Link from "next/link";
import { Star, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { moviesQueries } from "@/features/movies/queries";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";

interface MovieCardProps {
  movie: MovieListItem;
  isBookmarked?: boolean;
  onToggleBookmark?: (e: React.MouseEvent) => void;
}

export const getImageUrl = (path?: string | null, size: "w500" | "original" | "w300" = "w500"): string => {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `https://image.tmdb.org/t/p/${size}${path.startsWith("/") ? "" : "/"}${path}`;
};

export const MovieCard: React.FC<MovieCardProps> = ({
  movie,
  isBookmarked = false,
  onToggleBookmark,
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [mounted, setMounted] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<{
    description: string;
    averageRating: number;
    totalRatings: number;
    imdbRating?: number | null;
    imdbVotes?: number | null;
    tmdbRating?: number | null;
    tmdbVotes?: number | null;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [coords, setCoords] = useState<{
    top: number;
    left: number;
    width: number;
    height: number;
  } | null>(null);

  // Ratings
  const imdbRating = previewData?.imdbRating !== undefined ? previewData.imdbRating : movie.imdb_rating;
  const imdbVotes = previewData?.imdbVotes !== undefined ? previewData.imdbVotes : movie.imdb_votes;
  const tmdbRating = previewData?.tmdbRating !== undefined ? previewData.tmdbRating : (movie.tmdb_rating ?? movie.kinopoisk_rating);
  const tmdbVotes = previewData?.tmdbVotes !== undefined ? previewData.tmdbVotes : (movie.tmdb_votes ?? movie.kinopoisk_votes);

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

  const posterSrc = getImageUrl(movie.poster_url, "w500");

  const handleLinkClick = (url: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const handleLinkKeyDown = (url: string) => (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      e.stopPropagation();
      window.open(url, "_blank", "noopener,noreferrer");
    }
  };

  const openTimer = useRef<NodeJS.Timeout | null>(null);
  const closeTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    let active = true;
    Promise.resolve().then(() => {
      if (active) setMounted(true);
    });
    return () => {
      active = false;
      setMounted(false);
      if (openTimer.current) clearTimeout(openTimer.current);
      if (closeTimer.current) clearTimeout(closeTimer.current);
    };
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const card = cardRef.current;
    const box = card.getBoundingClientRect();
    const x = e.clientX - box.left - box.width / 2;
    const y = e.clientY - box.top - box.height / 2;

    const rotateX = -(y / (box.height / 2)) * 6;
    const rotateY = (x / (box.width / 2)) * 6;

    setTilt({ x: rotateX, y: rotateY });
  };

  const handleMouseEnter = (fromInfoButton = false) => {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }

    if (cardRef.current) {
      const rect = cardRef.current.getBoundingClientRect();
      setCoords({
        top: rect.top + window.scrollY,
        left: rect.left + window.scrollX,
        width: rect.width,
        height: rect.height,
      });
    }

    if (fromInfoButton || showPreview) {
      if (!openTimer.current && !showPreview) {
        openTimer.current = setTimeout(async () => {
          setShowPreview(true);
          openTimer.current = null;

          if (!previewData) {
            setLoading(true);
            try {
              const [movieDetail, ratingsSummary] = await Promise.all([
                moviesQueries.getMovie(movie.id),
                moviesQueries.getMovieRatings(movie.id).catch(() => ({
                  average_rating: 0,
                  total_ratings: 0,
                })),
              ]);
              setPreviewData({
                description: movieDetail.description || "",
                averageRating: ratingsSummary.average_rating || 0,
                totalRatings: ratingsSummary.total_ratings || 0,
                imdbRating: movieDetail.imdb_rating,
                imdbVotes: movieDetail.imdb_votes,
                tmdbRating: movieDetail.tmdb_rating,
                tmdbVotes: movieDetail.tmdb_votes,
              });
            } catch (err) {
              console.error("Error loading hover preview data:", err);
            } finally {
              setLoading(false);
            }
          }
        }, 200);
      }
    }
  };

  const handleMouseLeave = () => {
    if (openTimer.current) {
      clearTimeout(openTimer.current);
      openTimer.current = null;
    }

    closeTimer.current = setTimeout(() => {
      setShowPreview(false);
      closeTimer.current = null;
    }, 200);

    setTilt({ x: 0, y: 0 });
  };

  const handleInfoMouseLeave = () => {
    if (openTimer.current) {
      clearTimeout(openTimer.current);
      openTimer.current = null;
    }
  };

  let adjustedLeft = 0;
  let expandRight = true;
  const previewPosterWidth = coords ? Math.round(coords.height * (2 / 3)) : 220;
  if (coords) {
    expandRight = coords.left + previewPosterWidth + 240 < window.innerWidth - 16;
    if (expandRight) {
      adjustedLeft = coords.left;
      if (adjustedLeft + previewPosterWidth + 240 > window.innerWidth - 16) {
        adjustedLeft = window.innerWidth - (previewPosterWidth + 240) - 16;
      }
    } else {
      adjustedLeft = coords.left - 240;
      if (adjustedLeft < 16) {
        adjustedLeft = 16;
      }
    }
  }

    return (
      <>
        <div
          ref={cardRef}
          onMouseMove={handleMouseMove}
          onMouseEnter={() => handleMouseEnter(false)}
          onMouseLeave={handleMouseLeave}
          className="glass-surface rounded-xl overflow-hidden group cursor-pointer transition-all duration-200 ease-out flex flex-col h-full relative"
          style={{
            transform:
              tilt.x === 0 && tilt.y === 0
                ? undefined
                : `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          }}
        >
          {/* Info & Media Type Badges */}
          <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5">
            <div
              onMouseEnter={() => handleMouseEnter(true)}
              onMouseLeave={handleInfoMouseLeave}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
              className="p-1.5 rounded-full bg-black/50 border border-white/10 hover:bg-[#6E5CFF] hover:border-[#6E5CFF]/30 transition-all text-white outline-none cursor-help shadow-md backdrop-blur-md"
              title="Справка о медиа"
            >
              <Info size={14} />
            </div>

            {/* Media Type Badge */}
            {movie.media_type === "tv" ? (
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-[#6E5CFF]/90 backdrop-blur-md text-white border border-[#6E5CFF]/40 shadow-md">
                Сериал
              </span>
            ) : (
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-[#01b4e4]/90 backdrop-blur-md text-white border border-[#01b4e4]/40 shadow-md">
                Фильм
              </span>
            )}
          </div>

          {/* Bookmark Button */}
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onToggleBookmark?.(e);
            }}
            className="absolute top-3 right-3 z-10 p-2 rounded-full bg-black/40 border border-white/10 hover:bg-black/60 transition-all text-white outline-none focus-visible:ring-2 focus-visible:ring-[#E8B74C]"
            aria-label={isBookmarked ? "Remove from bookmarks" : "Add to bookmarks"}
          >
            <Star
              size={16}
              className={isBookmarked ? "fill-[#E8B74C] text-[#E8B74C]" : "text-white"}
            />
          </button>

          <Link href={`/movies/${movie.id}`} className="flex flex-col h-full">
            {/* Poster Wrapper */}
            <div className="relative aspect-[2/3] w-full overflow-hidden bg-white/5 flex items-center justify-center text-center">
              {posterSrc ? (
                <img
                  src={posterSrc}
                  alt={movie.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  loading="eager"
                  decoding="async"
                />
              ) : (
                <div className="p-4 text-gray-500 font-semibold select-none text-sm">
                  {movie.title}
                </div>
              )}
            </div>

            {/* Info Area */}
            <div
              className="p-4 flex-grow flex flex-col justify-end"
              style={{
                background: "linear-gradient(to top, rgba(10, 12, 20, 0.95), transparent)",
              }}
            >
              <span className="text-xs text-gray-400 font-semibold mb-1">
                {movie.release_year}
              </span>
              <h3 className="text-base font-bold text-white line-clamp-1 group-hover:text-[#E8B74C] transition-colors">
                {movie.title}
              </h3>
              {movie.original_title && (
                <p className="text-xs text-gray-400 font-normal line-clamp-1 italic mb-2">
                  {movie.original_title}
                </p>
              )}
              <div className="flex flex-wrap gap-1 mt-auto">
                {movie.genres?.slice(0, 2).map((genre) => (
                  <span
                    key={genre}
                    className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 text-gray-300 font-medium"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            </div>
          </Link>
        </div>

        {/* Floating Preview Portal */}
        {mounted &&
          createPortal(
            <AnimatePresence>
              {showPreview && coords && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ duration: 0.2, ease: "easeOut" }}
                  onMouseEnter={() => handleMouseEnter(false)}
                  onMouseMove={() => handleMouseEnter(false)}
                  onMouseLeave={handleMouseLeave}
                  style={{
                    position: "absolute",
                    top: coords.top,
                    left: adjustedLeft,
                    width: previewPosterWidth + 240,
                    height: coords.height,
                    zIndex: 9999,
                  }}
                  className={`bg-[#0c0e17]/95 border border-white/10 rounded-xl overflow-hidden shadow-2xl shadow-black/80 flex backdrop-blur-md ${expandRight ? "flex-row" : "flex-row-reverse"
                    }`}
                >
                  {/* Poster in Preview */}
                  <div style={{ width: previewPosterWidth, height: coords.height }} className="relative flex-shrink-0 bg-black/40 overflow-hidden">
                    <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5">
                      <div className="p-1.5 rounded-full bg-[#6E5CFF] border border-[#6E5CFF]/30 text-white outline-none">
                        <Info size={14} />
                      </div>
                      {isTv ? (
                        <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-[#6E5CFF] text-white">
                          Сериал
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-[#01b4e4] text-white">
                          Фильм
                        </span>
                      )}
                    </div>
                    {posterSrc ? (
                      <img
                        src={posterSrc}
                        alt={movie.title}
                        className="w-full h-full object-cover object-top"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center p-4 text-gray-500 font-semibold text-sm text-center">
                        {movie.title}
                      </div>
                    )}
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        onToggleBookmark?.(e);
                      }}
                      className="absolute top-3 right-3 z-10 p-2 rounded-full bg-black/40 border border-white/10 hover:bg-black/60 transition-all text-white outline-none"
                    >
                      <Star
                        size={16}
                        className={isBookmarked ? "fill-[#E8B74C] text-[#E8B74C]" : "text-white"}
                      />
                    </button>
                  </div>

                  {/* Details Panel */}
                  <div
                    className={`w-[240px] flex-shrink-0 p-4 flex flex-col h-full overflow-y-auto scrollbar-none ${expandRight ? "border-l border-white/10" : "border-r border-white/10"
                      }`}
                  >
                    <Link href={`/movies/${movie.id}`} className="flex flex-col gap-3 h-full w-full justify-start">
                      {/* Header Details */}
                      <div className="space-y-2 flex-shrink-0">
                        <div>
                          <span className="text-[10px] text-gray-400 font-semibold">{movie.release_year}</span>
                          <h3 className="text-sm font-bold leading-snug line-clamp-2 mt-0.5 hover:text-[#E8B74C] transition-colors">
                            {movie.title}
                          </h3>
                          {movie.original_title && (
                            <p className="text-xs text-gray-400 font-normal line-clamp-1 italic">
                              {movie.original_title}
                            </p>
                          )}
                        </div>

                        {/* Ratings Section */}
                        {loading ? (
                          <div className="space-y-1.5 flex-shrink-0">
                            <ShimmerSkeleton className="h-4 w-28" />
                            <ShimmerSkeleton className="h-4 w-20" />
                            <ShimmerSkeleton className="h-4 w-20" />
                          </div>
                        ) : (
                          <div className="space-y-1.5 text-[11px] flex-shrink-0">
                            {/* Local Rating */}
                            <div className="flex items-center gap-1.5 text-white">
                              <Star className="fill-[#E8B74C] text-[#E8B74C]" size={12} />
                              <span className="font-semibold text-gray-300">
                                <span className="text-[#6E5CFF]">G</span>F:
                              </span>
                              <span className="font-bold text-[#E8B74C]">
                                {previewData?.averageRating ? previewData.averageRating.toFixed(1) : "0.0"}
                              </span>
                              {previewData?.totalRatings !== undefined && (
                                <span className="text-gray-500 text-[10px]">
                                  ({previewData.totalRatings})
                                </span>
                              )}
                            </div>

                            {/* IMDb Rating */}
                            <span
                              role="link"
                              tabIndex={0}
                              onClick={handleLinkClick(imdbUrl)}
                              onKeyDown={handleLinkKeyDown(imdbUrl)}
                              className="flex items-center gap-1.5 text-white hover:text-[#F5C518] transition-colors cursor-pointer select-none"
                              title="Открыть на IMDb"
                            >
                              <span className="px-1.5 py-0.2 text-[8px] font-extrabold rounded bg-[#F5C518] text-black leading-normal">
                                IMDb
                              </span>
                              <span className="font-bold text-gray-200">
                                {imdbRatingStr}
                              </span>
                              <span className="text-gray-500 text-[10px]">/ 10</span>
                              {imdbVotes && imdbVotes > 0 ? (
                                <span className="text-gray-500 text-[9px] ml-0.5">({imdbVotesStr})</span>
                              ) : null}
                            </span>

                            {/* TMDb Rating */}
                            <span
                              role="link"
                              tabIndex={0}
                              onClick={handleLinkClick(tmdbUrl)}
                              onKeyDown={handleLinkKeyDown(tmdbUrl)}
                              className="flex items-center gap-1.5 text-white hover:text-[#01b4e4] transition-colors cursor-pointer select-none"
                              title="Открыть на TMDb"
                            >
                              <span className="px-1.5 py-0.2 text-[8px] font-extrabold rounded bg-[#01b4e4] text-white leading-normal">
                                TMDb
                              </span>
                              <span className="font-bold text-gray-200">
                                {tmdbRatingStr}
                              </span>
                              <span className="text-gray-500 text-[10px]">/ 10</span>
                              {tmdbVotes && tmdbVotes > 0 ? (
                                <span className="text-gray-500 text-[9px] ml-0.5">({tmdbVotesStr})</span>
                              ) : null}
                            </span>
                          </div>
                        )}

                        {/* Genres */}
                        <div className="flex flex-wrap gap-1">
                          {movie.genres?.slice(0, 3).map((genre) => (
                            <span
                              key={genre}
                              className="text-[9px] px-1.5 py-0.5 rounded bg-white/10 text-gray-300 font-medium"
                            >
                              {genre}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="h-[1px] bg-white/10 flex-shrink-0" />

                      {/* Description */}
                      <div className="flex-grow overflow-hidden">
                        {loading ? (
                          <div className="space-y-2">
                            <ShimmerSkeleton className="h-3 w-full" />
                            <ShimmerSkeleton className="h-3 w-full" />
                            <ShimmerSkeleton className="h-3 w-4/5" />
                          </div>
                        ) : (
                          <p className="text-[11px] text-gray-300 leading-relaxed font-normal line-clamp-[10]">
                            {previewData?.description || "Описание отсутствует."}
                          </p>
                        )}
                      </div>
                    </Link>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>,
            document.body
          )}
      </>
    );
  };
