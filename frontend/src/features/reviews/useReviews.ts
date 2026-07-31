import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { moviesQueries } from "../movies/queries";

import { ReviewItem, RatingsSummary } from "@/types/movie";

export function useReviews(movieId: number) {
  const queryClient = useQueryClient();

  // 1. Fetch reviews
  const { data: reviewsData, isLoading: reviewsLoading, error: reviewsError } = useQuery<{ items: ReviewItem[] }>({
    queryKey: ["movie-reviews", movieId],
    queryFn: () => moviesQueries.getMovieReviews(movieId),
  });

  // 2. Fetch ratings summary
  const { data: ratingsData, isLoading: ratingsLoading, error: ratingsError } = useQuery<RatingsSummary>({
    queryKey: ["movie-ratings", movieId],
    queryFn: () => moviesQueries.getMovieRatings(movieId),
  });

  // 3. Mutation: Add/Update rating
  const rateMutation = useMutation({
    mutationFn: async (rating: number) => {
      await apiClient.put(`/reviews/movies/${movieId}/rating`, {
        rating,
        movie_id: movieId,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movie-ratings", movieId] });
    },
  });

  // 4. Mutation: Add review
  const addReviewMutation = useMutation({
    mutationFn: async ({ reviewText, username }: { reviewText: string; username?: string }) => {
      await apiClient.post(`/reviews/movies/${movieId}`, {
        review: reviewText,
        username: username,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movie-reviews", movieId] });
    },
  });

  // 5. Mutation: Delete review
  const deleteReviewMutation = useMutation({
    mutationFn: async (reviewId: number) => {
      await apiClient.delete(`/reviews/${reviewId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movie-reviews", movieId] });
    },
  });

  return {
    reviews: reviewsData?.items || [],
    ratings: ratingsData || null,
    isLoading: reviewsLoading || ratingsLoading,
    error: reviewsError || ratingsError,
    rateMovie: rateMutation.mutateAsync,
    isRating: rateMutation.isPending,
    addReview: (reviewText: string, username?: string) =>
      addReviewMutation.mutateAsync({ reviewText, username }),
    isAddingReview: addReviewMutation.isPending,
    deleteReview: deleteReviewMutation.mutateAsync,
    isDeletingReview: deleteReviewMutation.isPending,
  };
}
