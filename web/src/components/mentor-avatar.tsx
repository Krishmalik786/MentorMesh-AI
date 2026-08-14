import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { mentorFor } from "@/lib/taxonomy";

const SIZES = {
  sm: "size-7 [&_svg]:size-3.5",
  md: "size-9 [&_svg]:size-4",
  lg: "size-11 [&_svg]:size-5",
} as const;

/**
 * Identifies which specialist is speaking. Falls back to the generic mesh mark
 * when a reply came from the synthesizer blending several mentors together.
 */
export function MentorAvatar({
  specialist,
  size = "md",
  className,
}: {
  specialist?: string;
  size?: keyof typeof SIZES;
  className?: string;
}) {
  const mentor = specialist ? mentorFor(specialist) : undefined;
  const Icon = mentor?.icon ?? Sparkles;

  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full border border-primary/15 bg-accent text-accent-foreground",
        SIZES[size],
        className
      )}
    >
      <Icon />
    </span>
  );
}
