import { Info } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { FeedCard, type FeedPost } from "@/components/feed-card";

/**
 * Preview only. There is no posts/likes/comments API yet — this page renders
 * sample data so the feed design is reviewable, and is labelled as such so it
 * can't be mistaken for live content. Swap SAMPLE_POSTS for a fetch once the
 * feed endpoints land.
 */
const SAMPLE_POSTS: FeedPost[] = [
  {
    id: "1",
    startupName: "Loopwise",
    authorName: "Ana Petrova",
    authorRole: "Co-founder",
    timestamp: "2h",
    body: "Shipped our async review queue this week — teams can now close feedback loops without a standup. Took three rewrites to get the conflict handling right.",
    likes: 24,
    comments: 5,
  },
  {
    id: "2",
    startupName: "Fernwork",
    authorName: "Dev Rao",
    authorRole: "Founder",
    timestamp: "6h",
    body: "We cut onboarding from 11 steps to 3. Activation went from 34% to 61% in two weeks. Happy to share what we removed.",
    likes: 41,
    comments: 12,
    connection: "connected",
  },
  {
    id: "3",
    startupName: "Northaven",
    authorName: "Mei Chen",
    authorRole: "CTO",
    timestamp: "1d",
    body: "Open-sourced our schema migration runner today. It's the boring infrastructure we wished existed when we started.",
    likes: 18,
    comments: 3,
    connection: "pending",
  },
];

export default function FeedPage() {
  return (
    <AppShell>
      <main className="mx-auto w-full max-w-2xl px-6 py-10">
        <div className="mb-6 space-y-1">
          <h1 className="text-2xl font-semibold">Feed</h1>
          <p className="text-muted-foreground">
            Product updates from founders building alongside you.
          </p>
        </div>

        <div className="mb-6 flex items-start gap-3 rounded-lg border border-dashed bg-muted/40 px-4 py-3">
          <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">Design preview.</span> These are
            sample posts — posting, reactions and connections aren&apos;t wired to the
            backend yet, so nothing here is saved.
          </p>
        </div>

        <div className="space-y-4">
          {SAMPLE_POSTS.map((post) => (
            <FeedCard key={post.id} post={post} />
          ))}
        </div>
      </main>
    </AppShell>
  );
}
