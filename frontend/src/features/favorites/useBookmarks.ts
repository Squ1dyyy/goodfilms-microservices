import { useQuery, useMutation, useQueries, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { moviesQueries } from "../movies/queries";
import { useAuthStore } from "@/store/auth";

export function useBookmarks() {
  const queryClient = useQueryClient();
  const { accessToken } = useAuthStore();

  // Query: Get all bookmarked movie IDs
  const { data: bookmarkedIds = [], isLoading: idsLoading } = useQuery<number[]>({
    queryKey: ["bookmarks"],
    queryFn: async () => {
      const res = await apiClient.get("/users/me/bookmarks");
      return res.data;
    },
    enabled: !!accessToken,
  });

  // Fetch full details of each bookmarked movie in parallel
  const moviesQueriesResult = useQueries({
    queries: bookmarkedIds.map((id) => ({
      queryKey: ["movie", id],
      queryFn: () => moviesQueries.getMovie(id),
      staleTime: 5 * 60 * 1000, // 5 min cache
    })),
  });

  const bookmarkedMovies = moviesQueriesResult
    .filter((q) => q.isSuccess && q.data)
    .map((q) => q.data!);

  const moviesLoading = moviesQueriesResult.some((q) => q.isLoading);

  // Mutation: Add or remove from bookmarks
  const toggleBookmarkMutation = useMutation({
    mutationFn: async ({ movieId, isBookmarked }: { movieId: number; isBookmarked: boolean }) => {
      if (isBookmarked) {
        await apiClient.delete(`/users/me/bookmarks/${movieId}`);
      } else {
        await apiClient.post(`/users/me/bookmarks/${movieId}`);
      }
    },
    // Optimistic Update
    onMutate: async ({ movieId, isBookmarked }) => {
      await queryClient.cancelQueries({ queryKey: ["bookmarks"] });
      const previousIds = queryClient.getQueryData<number[]>(["bookmarks"]) || [];

      // Optimistically update the list of ids
      const nextIds = isBookmarked
        ? previousIds.filter((id) => id !== movieId)
        : [...previousIds, movieId];

      queryClient.setQueryData(["bookmarks"], nextIds);

      return { previousIds };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousIds) {
        queryClient.setQueryData(["bookmarks"], context.previousIds);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
    },
  });

  return {
    bookmarkedIds,
    bookmarkedMovies,
    isLoading: idsLoading || moviesLoading,
    toggleBookmark: (movieId: number) => {
      const isBookmarked = bookmarkedIds.includes(movieId);
      toggleBookmarkMutation.mutate({ movieId, isBookmarked });
    },
  };
}
