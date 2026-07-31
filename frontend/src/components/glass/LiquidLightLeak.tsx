"use client";

import React, { useEffect, useRef } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export const LiquidLightLeak: React.FC = () => {
  const glowRef = useRef<HTMLDivElement>(null);
  const isReduced = useReducedMotion();

  useEffect(() => {
    const glow = glowRef.current;
    if (!glow) return;

    if (isReduced) {
      // Static, centered-ish layout — no cursor tracking.
      glow.style.transform = "translate3d(-50%, -50%, 0) translate3d(50vw, 30vh, 0)";
      return;
    }

    // Target / current are in VIEWPORT coordinates (clientX/clientY), which is the
    // correct space for a position:fixed element — it stays under the cursor
    // regardless of scroll.
    let targetX = window.innerWidth / 2;
    let targetY = window.innerHeight / 3;
    let currentX = targetX;
    let currentY = targetY;
    let frameId = 0;
    let running = true;

    const handlePointerMove = (e: PointerEvent) => {
      targetX = e.clientX;
      targetY = e.clientY;
    };

    // While the user scrolls with the wheel the cursor doesn't move, so no
    // pointermove fires. The fixed glow should simply stay under the cursor —
    // there's nothing to recompute — but kicking the rAF loop back on guarantees
    // we keep painting smoothly instead of appearing to stall.
    const handleScroll = () => {
      if (!running) {
        running = true;
        frameId = requestAnimationFrame(update);
      }
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    window.addEventListener("scroll", handleScroll, { passive: true });

    const update = () => {
      // Lerp toward the target. 0.18 is snappy enough to not feel laggy while
      // still smoothing out raw pointer jitter.
      currentX += (targetX - currentX) * 0.18;
      currentY += (targetY - currentY) * 0.18;

      glow.style.transform =
        `translate3d(-50%, -50%, 0) translate3d(${currentX}px, ${currentY}px, 0)`;

      // Once we've essentially reached the target, idle the loop until the next
      // pointer move / scroll instead of burning a frame every tick.
      if (Math.abs(targetX - currentX) < 0.5 && Math.abs(targetY - currentY) < 0.5) {
        running = false;
        return;
      }
      frameId = requestAnimationFrame(update);
    };

    frameId = requestAnimationFrame(update);

    return () => {
      running = false;
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("scroll", handleScroll);
      cancelAnimationFrame(frameId);
    };
  }, [isReduced]);

  return (
    <div
      ref={glowRef}
      aria-hidden
      className="fixed left-0 top-0 w-[480px] h-[480px] rounded-full blur-[60px] opacity-25 will-change-transform pointer-events-none -z-40"
      style={{
        background:
          "radial-gradient(circle, var(--bg-blob-violet) 0%, var(--bg-blob-cyan) 50%, transparent 100%)",
        transform: "translate3d(-50%, -50%, 0) translate3d(50vw, 30vh, 0)",
      }}
    />
  );
};
