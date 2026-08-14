import { cn } from "@/lib/utils";

/**
 * The mesh mark: four nodes (the four sources) tied to one center.
 */
export function LogoMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" aria-hidden className={cn("size-6", className)}>
      <path
        d="M12 12 5 5M12 12l7-7M12 12l-7 7M12 12l7 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.45"
      />
      <circle cx="5" cy="5" r="2" fill="currentColor" opacity="0.7" />
      <circle cx="19" cy="5" r="2" fill="currentColor" opacity="0.7" />
      <circle cx="5" cy="19" r="2" fill="currentColor" opacity="0.7" />
      <circle cx="19" cy="19" r="2" fill="currentColor" opacity="0.7" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  );
}

export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2 font-semibold tracking-[-0.02em]", className)}>
      <LogoMark className="size-5 text-primary" />
      MentorMesh
    </span>
  );
}
