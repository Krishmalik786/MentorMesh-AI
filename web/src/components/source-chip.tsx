import Link from "next/link";
import { cn } from "@/lib/utils";
import { SOURCE_META } from "@/lib/taxonomy";
import type { SourceType } from "@/lib/types";

/**
 * The citation pill. This is the product's trust story made visible — wherever a
 * claim appears, this chip says which fetched source it came from, and links out
 * to it when we have the URL.
 */
export function SourceChip({
  source,
  href,
  detail,
  className,
}: {
  source: SourceType;
  href?: string;
  detail?: string;
  className?: string;
}) {
  const meta = SOURCE_META[source];
  const Icon = meta.icon;

  const body = (
    <>
      <Icon className="size-3" />
      {meta.label}
      {detail && <span className="text-muted-foreground/80">· {detail}</span>}
    </>
  );

  const classes = cn(
    "inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/60 px-2 py-0.5 text-xs font-medium text-muted-foreground",
    href && "transition-colors hover:border-primary/40 hover:bg-accent hover:text-accent-foreground",
    className
  );

  if (href) {
    return (
      <Link href={href} target="_blank" rel="noopener noreferrer" className={classes}>
        {body}
      </Link>
    );
  }

  return <span className={classes}>{body}</span>;
}
