"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { ShimmerSkeleton } from "@/components/glass/ShimmerSkeleton";

interface WatchProviderLink {
  providerId: string;
  name: string;
  logoUrl: string;
  brandColor: string;
  url: string;
  accessType: string;
}

interface WatchProvidersRowProps {
  movieId: number;
}

export const WatchProvidersRow: React.FC<WatchProvidersRowProps> = ({ movieId }) => {
  const { data: providers = [], isLoading } = useQuery<WatchProviderLink[]>({
    queryKey: ["watch-links", movieId],
    queryFn: async () => {
      const res = await fetch(`/watch-links/${movieId}`);
      if (!res.ok) {
        throw new Error("Failed to fetch watch links");
      }
      return res.json();
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-3 py-4">
        <ShimmerSkeleton className="h-5 w-32" />
        <div className="flex flex-wrap gap-3">
          {[...Array(3)].map((_, i) => (
            <ShimmerSkeleton key={i} className="h-10 w-28 rounded-full" />
          ))}
        </div>
      </div>
    );
  }

  if (providers.length === 0) {
    return null;
  }

  const getAccessTypeText = (type: string) => {
    switch (type) {
      case "subscription":
        return "Подписка";
      case "free":
        return "Бесплатно";
      case "purchase":
        return "Покупка";
      default:
        return "Смотреть";
    }
  };

  return (
    <div className="space-y-3 py-4 border-t border-white/10 mt-6">
      <div className="flex flex-col gap-1">
        <h4 className="text-sm font-semibold text-gray-400">Где посмотреть:</h4>
        <span className="text-[10px] text-gray-500 font-medium">Партнёрские ссылки</span>
      </div>
      <div className="flex flex-wrap gap-3">
        {providers.map((p) => (
          <a
            key={p.providerId}
            href={`/go/${p.providerId}/${movieId}`}
            target="_blank"
            rel="nofollow sponsored noopener"
            className="flex items-center gap-2.5 px-4 py-2 rounded-full glass-surface border border-white/10 hover:border-white/20 transition-all duration-200 group text-sm font-medium text-white"
            style={
              {
                "--hover-color": p.brandColor,
              } as React.CSSProperties
            }
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = p.brandColor;
              e.currentTarget.style.boxShadow = `0 0 12px ${p.brandColor}20`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.14)";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <img src={p.logoUrl} alt={p.name} className="h-5 w-5 rounded-md object-contain" />
            <div className="flex flex-col items-start leading-none gap-0.5">
              <span className="group-hover:text-[#E8B74C] transition-colors">{p.name}</span>
              <span className="text-[9px] text-gray-400 font-normal">{getAccessTypeText(p.accessType)}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
};
