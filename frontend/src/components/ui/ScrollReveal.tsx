"use client";

import React, { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface ScrollRevealProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  className = "",
  delay = 0,
}) => {
  const isReduced = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  const [forceShow, setForceShow] = useState(false);

  // Fail-safe: never leave content stuck invisible. On back/forward navigation
  // the route subtree is restored under the page transition and the
  // IntersectionObserver may not fire for elements already in the viewport,
  // which would keep cards at opacity:0. This timer guarantees they reveal.
  useEffect(() => {
    const t = setTimeout(() => setForceShow(true), 400);
    return () => clearTimeout(t);
  }, []);

  if (isReduced) {
    return <div className={className}>{children}</div>;
  }

  const visible = inView || forceShow;

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={visible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{
        duration: 0.5,
        ease: [0.25, 0.1, 0.25, 1],
        delay,
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
