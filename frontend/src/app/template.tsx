"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { usePathname } from "next/navigation";

export default function Template({ children }: { children: React.ReactNode }) {
  const isReduced = useReducedMotion();
  const pathname = usePathname();

  // Animation settings based on user reduced motion preference
  const transition = isReduced
    ? {
        duration: 0.15,
        ease: "linear",
      }
    : {
        duration: 0.25,
        ease: [0.4, 0, 0.2, 1], // cubic-bezier(0.4,0,0.2,1)
      };

  const variants = isReduced
    ? {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
      }
    : {
        initial: { opacity: 0, filter: "blur(12px)" },
        animate: { opacity: 1, filter: "blur(0px)" },
        exit: { opacity: 0, filter: "blur(12px)" },
      };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial="initial"
        animate="animate"
        exit="exit"
        variants={variants}
        transition={transition as unknown as object}
        className="flex-grow flex flex-col"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
