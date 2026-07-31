import { apiClient } from "@/lib/api-client";
import {
  MovieListResponse,
  MovieDetail,
  Person,
  PersonDetailResponse,
  RefItem,
  ReviewItem,
  RatingsSummary,
  MovieListItem,
} from "@/types/movie";

export interface MovieQueryParams {
  page?: number;
  limit?: number;
  genre_id?: number;
  media_type?: string;
  is_adult?: boolean;
  year_from?: number;
  year_to?: number;
  imdb_rating_from?: number;
  imdb_rating_to?: number;
  imdb_votes_from?: number;
  tmdb_rating_from?: number;
  tmdb_rating_to?: number;
  tmdb_votes_from?: number;
  search?: string;
  sort_by?: string;
}

export const moviesQueries = {
  getMovies: async (params: MovieQueryParams = {}): Promise<MovieListResponse> => {
    // Only pass keys that have non-undefined values
    const queryParams: Record<string, string | number | boolean> = {};
    const validKeys: (keyof MovieQueryParams)[] = [
      "page",
      "limit",
      "genre_id",
      "media_type",
      "is_adult",
      "year_from",
      "year_to",
      "imdb_rating_from",
      "imdb_rating_to",
      "imdb_votes_from",
      "tmdb_rating_from",
      "tmdb_rating_to",
      "tmdb_votes_from",
      "search",
      "sort_by",
    ];

    validKeys.forEach((key) => {
      const val = params[key];
      if (val !== undefined && val !== null && val !== "" && !Number.isNaN(val)) {
        queryParams[key] = val as string | number | boolean;
      }
    });

    const res = await apiClient.get("/movies", { params: queryParams });
    return res.data;
  },

  getMovie: async (id: number): Promise<MovieDetail> => {
    const res = await apiClient.get(`/movies/${id}`);
    return res.data;
  },

  getPersons: async (search?: string, page: number = 1, limit: number = 20): Promise<{ items: Person[]; total: number }> => {
    const params: Record<string, string | number> = { page, limit };
    if (search) params.search = search;
    const res = await apiClient.get("/persons", { params });
    return res.data;
  },

  getPerson: async (id: number): Promise<PersonDetailResponse> => {
    // The `/persons/{id}/movies` endpoint returns the combined
    // { person, movies } shape (PersonDetailResponse). The bare
    // `/persons/{id}` endpoint returns only the flat person object, which
    // would leave `person`/`movies` undefined and crash the detail page.
    const res = await apiClient.get(`/persons/${id}/movies`);
    return res.data;
  },

  getGenres: async (): Promise<RefItem[]> => {
    const res = await apiClient.get("/genres");
    return res.data;
  },

  getStudios: async (): Promise<RefItem[]> => {
    const res = await apiClient.get("/studios");
    return res.data;
  },

  getCountries: async (): Promise<RefItem[]> => {
    const res = await apiClient.get("/countries");
    return res.data;
  },

  getSimilarMovies: async (id: number): Promise<MovieListResponse> => {
    const res = await apiClient.get(`/recommendations/movies/${id}/similar`);
    if (Array.isArray(res.data)) {
      return {
        items: res.data,
        total: res.data.length,
        page: 1,
        limit: res.data.length,
      };
    }
    return res.data;
  },

  getCustomRecommendations: async (body: {
    movie_ids: number[];
    genres: string[];
    release_year?: number;
    release_year_from?: number;
    release_year_to?: number;
    imdb_rating_from?: number;
    media_type?: string;
    custom_description?: string;
    limit?: number;
  }): Promise<MovieListItem[]> => {
    const res = await apiClient.post("/recommendations/custom", {
      limit: 12,
      ...body,
    });
    return res.data;
  },

  getMovieReviews: async (id: number): Promise<{ items: ReviewItem[] }> => {
    const res = await apiClient.get(`/reviews/movies/${id}`);
    return res.data;
  },

  getMovieRatings: async (id: number): Promise<RatingsSummary> => {
    const res = await apiClient.get(`/reviews/movies/${id}/ratings`);
    return res.data;
  },
};
