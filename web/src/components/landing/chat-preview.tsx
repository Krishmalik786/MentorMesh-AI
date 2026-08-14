import { User } from "lucide-react";
import { MentorAvatar } from "@/components/mentor-avatar";
import { SourceChip } from "@/components/source-chip";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * The hero's visual anchor: a still of the chat with a mentor reply that
 * visibly cites its source. This is the differentiator, so it's worth showing
 * rather than describing.
 */
export function ChatPreview({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "rounded-xl border bg-card p-5 shadow-lg",
        className
      )}
    >
      <div className="flex items-center gap-2 border-b pb-3">
        <span className="size-2 rounded-full bg-muted-foreground/25" />
        <span className="size-2 rounded-full bg-muted-foreground/25" />
        <span className="size-2 rounded-full bg-muted-foreground/25" />
        <p className="ml-2 text-xs text-muted-foreground">Loopwise · mentor chat</p>
      </div>

      <div className="space-y-5 pt-5">
        <div className="flex flex-row-reverse items-start gap-3">
          <span className="inline-flex size-9 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <User className="size-4" />
          </span>
          <p className="rounded-lg rounded-tr-sm bg-primary px-3 py-2 text-sm text-primary-foreground">
            Are we ready to raise a seed round?
          </p>
        </div>

        <div className="flex items-start gap-3">
          <MentorAvatar specialist="pitch" />
          <div className="min-w-0 space-y-2">
            <Badge variant="secondary" className="text-xs">
              Fundraising mentor
            </Badge>
            <div className="rounded-lg rounded-tl-sm bg-muted px-3 py-2 text-sm leading-6">
              Your deck claims $12k MRR and 340 GitHub stars, but names no
              co-founder — investors at this stage will press on team before
              traction. Fix that slide first.
            </div>
            <div className="flex flex-wrap gap-1.5">
              <SourceChip source="pitch_deck" detail="slide 4" />
              <SourceChip source="github" detail="340 stars" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
