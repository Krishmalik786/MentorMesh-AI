"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";

/**
 * Entrance transition: short, ease-out, no spring. Motion here is meant to
 * direct attention as sections come into view, not to perform.
 *
 * Above-the-fold content should pass `immediate` — a viewport-triggered variant
 * starts at opacity 0, so anything that's the LCP element risks rendering blank
 * until the IntersectionObserver fires.
 */
export function Reveal({
  children,
  delay = 0,
  immediate = false,
  className,
}: {
  children: React.ReactNode;
  delay?: number;
  immediate?: boolean;
  className?: string;
}) {
  const transition = { duration: 0.25, ease: "easeOut", delay } as const;

  if (immediate) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={transition}
        className={cn(className)}
      >
        {children}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={transition}
      className={cn(className)}
    >
      {children}
    </motion.div>
  );
}
