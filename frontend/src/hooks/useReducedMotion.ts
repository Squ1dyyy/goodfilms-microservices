"use client";

import { useEffect, useState } from "react";

export function useReducedMotion() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const initialMatches = mediaQuery.matches;
    let active = true;
    Promise.resolve().then(() => {
      if (active) setReducedMotion(initialMatches);
    });

    const listener = (event: MediaQueryListEvent) => {
      if (active) setReducedMotion(event.matches);
    };

    mediaQuery.addEventListener("change", listener);
    return () => {
      active = false;
      mediaQuery.removeEventListener("change", listener);
    };
  }, []);

  return reducedMotion;
}
