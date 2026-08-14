import { redirect } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Link2, FileSearch, MessagesSquare, Quote } from "lucide-react";
import { getSessionToken } from "@/lib/session";
import { MarketingNav } from "@/components/landing/marketing-nav";
import { SiteFooter } from "@/components/landing/site-footer";
import { ChatPreview } from "@/components/landing/chat-preview";
import { FeedCard, type FeedPost } from "@/components/feed-card";
import { SourceChip } from "@/components/source-chip";
import { MentorAvatar } from "@/components/mentor-avatar";
import { Reveal } from "@/components/reveal";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { MENTOR_LIST } from "@/lib/taxonomy";

const STEPS = [
  {
    icon: Link2,
    title: "Drop your four links",
    body: "GitHub repo, website, pitch deck, social profile. Any subset works — we only claim what we can reach.",
  },
  {
    icon: FileSearch,
    title: "We build an evidence profile",
    body: "Each source is fetched and read. Hard numbers are copied straight from the source, never generated.",
  },
  {
    icon: MessagesSquare,
    title: "Chat with specialist mentors",
    body: "Your question is routed to the mentors who actually hold the relevant evidence.",
  },
  {
    icon: Quote,
    title: "Every answer cites its source",
    body: "Figures are checked back against the evidence log before you see them. Unbacked claims get rewritten.",
  },
];

const SAMPLE_QUOTES: Record<string, string> = {
  technical:
    "Your README promises a v2 API, but the last commit to that module was 4 months ago.",
  product:
    "Your homepage sells to enterprise teams; your pricing page tops out at $29/mo. Pick one.",
  pitch: "The deck claims $12k MRR but never says whether that's recurring or cumulative.",
  growth: "You post twice a month, all launch announcements — no wonder replies are flat.",
};

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
];

export default async function Home() {
  const token = await getSessionToken();
  if (token) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen flex-col">
      <MarketingNav />

      <main className="flex-1">
        {/* Hero */}
        <section className="mx-auto w-full max-w-[1200px] px-6 py-24">
          <div className="grid items-center gap-14 lg:grid-cols-2">
            <Reveal immediate className="space-y-6">
              <Badge variant="secondary">Evidence-based startup mentorship</Badge>
              <h1 className="text-4xl font-semibold text-balance sm:text-5xl">
                Mentorship grounded in what you actually built
              </h1>
              <p className="max-w-lg text-lg leading-8 text-muted-foreground">
                Drop in four links. MentorMesh reads your repo, site, deck and socials,
                builds a profile from real evidence, then puts you in front of specialist
                mentors who cite their sources instead of guessing.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="lg" render={<Link href="/signup">Get your profile</Link>} />
                <Button
                  size="lg"
                  variant="ghost"
                  render={
                    <Link href="#how-it-works">
                      See how it works
                      <ArrowRight className="size-4" />
                    </Link>
                  }
                />
              </div>
              <p className="text-sm text-muted-foreground">
                No credit card required · Try it with a demo profile first
              </p>
            </Reveal>

            <Reveal delay={0.08}>
              <ChatPreview />
            </Reveal>
          </div>
        </section>

        {/* Logo strip */}
        <section className="border-y bg-muted/30">
          <div className="mx-auto w-full max-w-[1200px] px-6 py-10">
            <p className="text-center text-xs font-medium tracking-wide text-muted-foreground uppercase">
              Built by founders from
            </p>
            <div className="mt-6 flex flex-wrap items-center justify-center gap-x-12 gap-y-4 opacity-60 grayscale">
              {["Loopwise", "Fernwork", "Northaven", "Baseplate", "Kettle"].map((name) => (
                <span key={name} className="text-lg font-semibold tracking-[-0.02em]">
                  {name}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* How it works */}
        <section id="how-it-works" className="mx-auto w-full max-w-[1200px] px-6 py-24">
          <Reveal className="max-w-2xl space-y-4">
            <Badge variant="secondary">How it works</Badge>
            <h2 className="text-3xl font-semibold text-balance sm:text-4xl">
              Four links in. Evidence you can point at, out.
            </h2>
            <p className="text-lg leading-8 text-muted-foreground">
              Most AI advice sounds plausible because nothing checks it. Every step here
              is built to fail honestly instead of guessing.
            </p>
          </Reveal>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((step, i) => (
              <Reveal key={step.title} delay={i * 0.06}>
                <Card className="h-full">
                  <CardContent className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="inline-flex size-9 items-center justify-center rounded-md bg-accent text-accent-foreground">
                        <step.icon className="size-4" />
                      </span>
                      <span className="tabular text-sm font-medium text-muted-foreground">
                        0{i + 1}
                      </span>
                    </div>
                    <p className="font-medium">{step.title}</p>
                    <p className="text-sm leading-6 text-muted-foreground">{step.body}</p>
                  </CardContent>
                </Card>
              </Reveal>
            ))}
          </div>
        </section>

        {/* Mentors */}
        <section id="mentors" className="border-y bg-muted/30">
          <div className="mx-auto w-full max-w-[1200px] px-6 py-24">
            <Reveal className="max-w-2xl space-y-4">
              <Badge variant="secondary">Specialist mentors</Badge>
              <h2 className="text-3xl font-semibold text-balance sm:text-4xl">
                Four mentors, each reading a different source
              </h2>
              <p className="text-lg leading-8 text-muted-foreground">
                No single generalist bot. Each mentor only sees the evidence from its own
                source, so it can&apos;t wander into territory it has nothing on.
              </p>
            </Reveal>

            <div className="mt-14 grid gap-6 sm:grid-cols-2">
              {MENTOR_LIST.map((mentor, i) => (
                <Reveal key={mentor.key} delay={i * 0.06}>
                  <Card className="h-full">
                    <CardContent className="space-y-4">
                      <div className="flex items-start gap-3">
                        <MentorAvatar specialist={mentor.key} size="lg" />
                        <div className="min-w-0 flex-1 space-y-1">
                          <p className="font-medium">{mentor.name}</p>
                          <p className="text-sm text-muted-foreground">{mentor.specialty}</p>
                        </div>
                        <SourceChip source={mentor.source} />
                      </div>
                      <blockquote className="border-l-2 border-primary/30 pl-4 text-sm leading-6 text-foreground/80 italic">
                        “{SAMPLE_QUOTES[mentor.key]}”
                      </blockquote>
                    </CardContent>
                  </Card>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* Community */}
        <section id="community" className="mx-auto w-full max-w-[1200px] px-6 py-24">
          <div className="grid items-start gap-14 lg:grid-cols-2">
            <Reveal className="space-y-4 lg:sticky lg:top-24">
              <Badge variant="secondary">Community</Badge>
              <h2 className="text-3xl font-semibold text-balance sm:text-4xl">
                Post what you shipped. Meet the founders who get it.
              </h2>
              <p className="text-lg leading-8 text-muted-foreground">
                Share product updates with founders working on the same problems, react to
                what they ship, and connect with the people behind the profiles.
              </p>
              <Button render={<Link href="/signup">Join the feed</Link>} />
            </Reveal>

            <Reveal delay={0.08} className="space-y-4">
              {SAMPLE_POSTS.map((post) => (
                <FeedCard key={post.id} post={post} />
              ))}
            </Reveal>
          </div>
        </section>

        {/* Final CTA */}
        <section className="bg-primary text-primary-foreground">
          <div className="mx-auto w-full max-w-[1200px] px-6 py-24 text-center">
            <Reveal className="mx-auto max-w-2xl space-y-6">
              <h2 className="text-3xl font-semibold text-balance sm:text-4xl">
                Find out what your own evidence says
              </h2>
              <p className="text-lg leading-8 opacity-80">
                It takes four links and about a minute. You can start with a demo profile
                if you&apos;d rather see it work first.
              </p>
              <Button
                size="lg"
                variant="secondary"
                render={<Link href="/signup">Get your profile</Link>}
              />
            </Reveal>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
