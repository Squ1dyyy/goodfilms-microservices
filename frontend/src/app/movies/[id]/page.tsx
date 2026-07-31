import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { moviesQueries } from "@/features/movies/queries";
import MovieDetailClient from "./MovieDetailClient";
import React from "react";
import { CastMember } from "@/types/movie";
import { ApiError } from "@/lib/api-client";

interface PageProps {
  params: Promise<{ id: string }>;
}

const MOCK_MOVIE = {
  id: 1,
  title: "Тестовый Фильм",
  release_year: 2024,
  poster_url: "https://example.com/poster.jpg",
  genres: ["Боевик"],
  description: "Это тестовое описание фильма.",
  studios: ["Warner Bros."],
  cast: [],
  directors: [],
  writers: [],
  producers: [],
};

// Generate dynamic SEO metadata on the server
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const unwrappedParams = await params;
  const movieId = Number(unwrappedParams.id);

  if (isNaN(movieId)) {
    return {
      title: "Фильм не найден",
    };
  }

  try {
    const movie = process.env.PLAYWRIGHT_MOCK === "true"
      ? MOCK_MOVIE
      : await moviesQueries.getMovie(movieId);
      
    const description = movie.description
      ? movie.description.slice(0, 160)
      : `Смотреть фильм ${movie.title} на GoodFilms.`;

    return {
      title: `${movie.title} (${movie.release_year}) — GoodFilms`,
      description,
      openGraph: {
        title: movie.title,
        description,
        images: movie.poster_url ? [{ url: movie.poster_url }] : [],
        type: "video.movie",
      },
    };
  } catch {
    return {
      title: "Фильм не найден — GoodFilms",
    };
  }
}

export default async function MovieDetailPage({ params }: PageProps) {
  const unwrappedParams = await params;
  const movieId = Number(unwrappedParams.id);

  if (isNaN(movieId)) {
    notFound();
  }

  let movie;
  try {
    movie = process.env.PLAYWRIGHT_MOCK === "true"
      ? MOCK_MOVIE
      : await moviesQueries.getMovie(movieId);
  } catch (error: unknown) {
    const apiErr = error as ApiError;
    if (apiErr.status === 404) {
      notFound();
    }
    throw error;
  }

  // JSON-LD structured data for schema.org/Movie representation
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Movie",
    "name": movie.title,
    "image": movie.poster_url || undefined,
    "description": movie.description || undefined,
    "datePublished": movie.release_year.toString(),
    "genre": movie.genres || [],
    "director": movie.directors?.map((d: CastMember) => ({
      "@type": "Person",
      "name": d.full_name,
    })) || [],
    "actor": movie.cast?.map((c: CastMember) => ({
      "@type": "Person",
      "name": c.full_name,
    })) || [],
  };

  return (
    <>
      {/* Inject Structured Search Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <MovieDetailClient movie={movie} />
    </>
  );
}
