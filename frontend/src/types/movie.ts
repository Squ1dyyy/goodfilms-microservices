export interface MovieListItem {
  id: number;
  title: string;
  original_title?: string | null;
  release_year: number;
  poster_url: string;
  backdrop_url?: string | null;
  media_type?: string | null;
  is_adult?: boolean | null;
  genres: string[];
  imdb_id?: string | null;
  imdb_rating?: number | null;
  imdb_votes?: number | null;
  tmdb_id?: number | null;
  tmdb_rating?: number | null;
  tmdb_votes?: number | null;
  trailer_url?: string | null;
  // Legacy compatibility fields
  kinopoisk_id?: number | null;
  kinopoisk_rating?: number | null;
  kinopoisk_votes?: number | null;
}

export type MediaListItem = MovieListItem;

export interface MovieListResponse {
  items: MovieListItem[];
  total: number;
  page: number;
  limit: number;
}

export interface CastMember {
  person_id: number;
  full_name: string;
  photo_url: string;
  character_name: string;
  billing_order: number;
}

export interface MovieDetail {
  id: number;
  title: string;
  original_title?: string | null;
  release_year: number;
  poster_url: string;
  backdrop_url?: string | null;
  media_type?: string | null;
  is_adult?: boolean | null;
  description: string;
  genres: string[];
  studios: string[];
  cast: CastMember[];
  directors: CastMember[];
  writers: CastMember[];
  producers: CastMember[];
  imdb_id?: string | null;
  imdb_rating?: number | null;
  imdb_votes?: number | null;
  tmdb_id?: number | null;
  tmdb_rating?: number | null;
  tmdb_votes?: number | null;
  trailer_url?: string | null;
  // Legacy compatibility fields
  kinopoisk_id?: number | null;
  kinopoisk_rating?: number | null;
  kinopoisk_votes?: number | null;
}

export type MediaDetail = MovieDetail;

export interface Person {
  id: number;
  full_name: string;
  birth_date: string;
  photo_url: string;
}

export interface PersonDetailResponse {
  person: Person;
  movies: MovieListResponse;
}

export interface RefItem {
  id: number;
  name: string;
}

export interface ReviewItem {
  id: number;
  movie_id: number;
  user_id: number;
  username?: string;
  review: string;
}

export interface RatingsSummary {
  average_rating: number;
  total_ratings: number;
  distribution: Record<number, number>;
}
