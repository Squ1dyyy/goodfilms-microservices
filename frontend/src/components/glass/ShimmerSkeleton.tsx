import React from "react";

export const ShimmerSkeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className = "", ...props }) => {
  return (
    <div
      className={`relative overflow-hidden rounded-lg bg-white/5 before:absolute before:inset-0 before:-translate-x-full before\:animate-shimmer before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent ${className}`}
      {...props}
    />
  );
};
