import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth";

export function useSubscriptions() {
  const queryClient = useQueryClient();
  const { accessToken } = useAuthStore();

  const { data: subscribedIds = [], isLoading } = useQuery<number[]>({
    queryKey: ["subscriptions"],
    queryFn: async () => {
      const res = await apiClient.get("/users/subscribe/person");
      return res.data;
    },
    enabled: !!accessToken,
  });

  const toggleSubscriptionMutation = useMutation({
    mutationFn: async ({ personId, isSubscribed }: { personId: number; isSubscribed: boolean }) => {
      if (isSubscribed) {
        await apiClient.delete(`/users/subscribe/person/${personId}`);
      } else {
        await apiClient.post(`/users/subscribe/person/${personId}`);
      }
    },
    // Optimistic Update
    onMutate: async ({ personId, isSubscribed }) => {
      await queryClient.cancelQueries({ queryKey: ["subscriptions"] });
      const previousIds = queryClient.getQueryData<number[]>(["subscriptions"]) || [];

      const nextIds = isSubscribed
        ? previousIds.filter((id) => id !== personId)
        : [...previousIds, personId];

      queryClient.setQueryData(["subscriptions"], nextIds);

      return { previousIds };
    },
    onError: (err, variables, context) => {
      if (context?.previousIds) {
        queryClient.setQueryData(["subscriptions"], context.previousIds);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["subscriptions"] });
    },
  });

  return {
    subscribedIds,
    isLoading,
    toggleSubscription: (personId: number) => {
      const isSubscribed = subscribedIds.includes(personId);
      toggleSubscriptionMutation.mutate({ personId, isSubscribed });
    },
  };
}
