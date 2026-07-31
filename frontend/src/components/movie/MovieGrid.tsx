import React from "react";
import { MovieListItem } from "@/types/movie";
import { MovieCard } from "./MovieCard";

interface MovieGridProps {
  movies: MovieListItem[];
  bookmarkedIds?: number[];
  onToggleBookmark?: (movieId: number) => void;
  className?: string;
}

import { ScrollReveal } from "../ui/ScrollReveal";

export const MovieGrid: React.FC<MovieGridProps> = ({
  movies,
  bookmarkedIds = [],
  onToggleBookmark,
  className,
}) => {
  return (
    <div className={className || "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6"}>
      {movies.map((movie, idx) => (
        <ScrollReveal key={movie.id} delay={(idx % 5) * 0.05}>
          <MovieCard
            movie={movie}
            isBookmarked={bookmarkedIds.includes(movie.id)}
            onToggleBookmark={() => onToggleBookmark?.(movie.id)}
          />
        </ScrollReveal>
      ))}
    </div>
  );
};
