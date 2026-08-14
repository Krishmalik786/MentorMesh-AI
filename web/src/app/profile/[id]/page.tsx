"use client";

import { use, useEffect, useRef, useState } from "react";
import { AlertCircle, FileSearch, Loader2 } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { MentorChat } from "@/components/chat/mentor-chat";
import { SourceChip } from "@/components/source-chip";
import { EmptyState } from "@/components/empty-state";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SOURCE_META } from "@/lib/taxonomy";
import type { ProfileStatusResponse, SourceType, StartupProfile } from "@/lib/types";

const TERMINAL_STATUSES = new Set(["done", "failed"]);

const STAGE_PROGRESS: Record<string, number> = {
  queued: 8,
  fetching_github: 25,
  fetching_website: 40,
  fetching_pitch_deck: 55,
  fetching_social: 70,
  synthesizing: 88,
  done: 100,
};

const STAGE_LABELS: Record<string, string> = {
  queued: "Queued",
  fetching_github: "Reading your GitHub repo",
  fetching_website: "Reading your website",
  fetching_pitch_deck: "Reading your pitch deck",
  fetching_social: "Reading your social profile",
  synthesizing: "Synthesizing your profile",
};

export default function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  const [entry, setEntry] = useState<ProfileStatusResponse | null>(null);
  const [pollError, setPollError] = useState<string | null>(null);
  const pollHandle = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    async function poll() {
      const res = await fetch(`/api/profile/${id}`);
      if (!res.ok) {
        setPollError("Could not load this profile");
        if (pollHandle.current) clearInterval(pollHandle.current);
        return;
      }
      const data: ProfileStatusResponse = await res.json();
      setEntry(data);
      if (TERMINAL_STATUSES.has(data.status) && pollHandle.current) {
        clearInterval(pollHandle.current);
      }
    }

    poll();
    pollHandle.current = setInterval(poll, 2000);
    return () => {
      if (pollHandle.current) clearInterval(pollHandle.current);
    };
  }, [id]);

  if (pollError) {
    return (
      <StatusFrame>
        <Card className="border-destructive/40">
          <CardContent>
            <EmptyState
              icon={AlertCircle}
              title="Could not load this profile"
              description={pollError}
            />
          </CardContent>
        </Card>
      </StatusFrame>
    );
  }

  if (!entry) {
    return (
      <StatusFrame>
        <div className="space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-48 w-full" />
        </div>
      </StatusFrame>
    );
  }

  if (entry.status === "failed") {
    return (
      <StatusFrame>
        <Card className="border-destructive/40">
          <CardHeader>
            <CardTitle className="text-destructive">Profile build failed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="font-mono text-xs leading-6 break-words text-muted-foreground">
              {entry.error}
            </p>
          </CardContent>
        </Card>
      </StatusFrame>
    );
  }

  if (entry.status !== "done" || !entry.profile) {
    const progress = STAGE_PROGRESS[entry.status] ?? 15;
    return (
      <StatusFrame>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Loader2 className="size-4 animate-spin" />
              Building your profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Progress value={progress} />
            <p className="text-sm text-muted-foreground">
              {STAGE_LABELS[entry.status] ?? entry.status}
            </p>
            <p className="text-xs text-muted-foreground">
              This usually takes 30–60 seconds. You can leave this page open.
            </p>
          </CardContent>
        </Card>
      </StatusFrame>
    );
  }

  return <ProfileView id={id} profile={entry.profile} />;
}

function StatusFrame({ children }: { children: React.ReactNode }) {
  return (
    <AppShell>
      <main className="mx-auto w-full max-w-2xl px-6 py-10">{children}</main>
    </AppShell>
  );
}

function ProfileView({ id, profile }: { id: string; profile: StartupProfile }) {
  const sections = buildSections(profile);

  return (
    <AppShell>
      <main className="mx-auto w-full max-w-[1200px] px-6 py-10">
        <header className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-semibold">
              {profile.company_name ?? "Untitled startup"}
            </h1>
            {profile.unreachable_sources.map((s) => (
              <Badge key={s} variant="outline" className="text-muted-foreground">
                {SOURCE_META[s].label} unreachable
              </Badge>
            ))}
          </div>
          {profile.one_line_summary && (
            <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
              {profile.one_line_summary}
            </p>
          )}
          <div className="flex flex-wrap gap-1.5">
            {(Object.keys(profile.source_links ?? {}) as SourceType[]).map((s) => (
              <SourceChip key={s} source={s} href={profile.source_links[s]} />
            ))}
          </div>
        </header>

        <Separator className="my-8" />

        <div className="grid items-start gap-8 lg:grid-cols-[minmax(0,1fr)_420px]">
          <Tabs defaultValue="profile">
            <TabsList>
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="evidence">
                Evidence
                <span className="tabular ml-1.5 text-muted-foreground">
                  {profile.evidence_log.length}
                </span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="profile" className="mt-6 space-y-4">
              {sections.map((section) => (
                <Card key={section.source}>
                  <CardHeader className="flex-row items-center justify-between gap-3">
                    <CardTitle className="text-base">{section.title}</CardTitle>
                    <SourceChip
                      source={section.source}
                      href={profile.source_links?.[section.source]}
                    />
                  </CardHeader>
                  <CardContent>
                    {section.fields.length > 0 ? (
                      <dl className="grid gap-x-8 gap-y-3 sm:grid-cols-2">
                        {section.fields.map((f) => (
                          <div key={f.label} className="space-y-0.5">
                            <dt className="text-xs text-muted-foreground">{f.label}</dt>
                            <dd className="text-sm leading-6">{f.value}</dd>
                          </div>
                        ))}
                      </dl>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        Nothing was found for this source.
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </TabsContent>

            <TabsContent value="evidence" className="mt-6">
              <Card>
                <CardContent className="p-0">
                  {profile.evidence_log.length === 0 ? (
                    <EmptyState
                      icon={FileSearch}
                      title="No evidence collected"
                      description="None of the provided sources could be read."
                    />
                  ) : (
                    <ul className="divide-y">
                      {profile.evidence_log.map((ev, i) => (
                        <li key={i} className="flex items-start gap-3 px-5 py-3">
                          <SourceChip
                            source={ev.source}
                            href={profile.source_links?.[ev.source]}
                            className="mt-0.5 shrink-0"
                          />
                          <div className="min-w-0 space-y-0.5">
                            <p className="text-sm leading-6">{ev.claim}</p>
                            {ev.detail && (
                              <p className="text-xs text-muted-foreground">{ev.detail}</p>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          <div className="lg:sticky lg:top-24">
            <MentorChat profileId={id} profile={profile} />
          </div>
        </div>
      </main>
    </AppShell>
  );
}

interface Field {
  label: string;
  value: string;
}

interface Section {
  source: SourceType;
  title: string;
  fields: Field[];
}

function present(label: string, value: unknown): Field[] {
  if (value === null || value === undefined || value === "") return [];
  if (Array.isArray(value)) {
    return value.length ? [{ label, value: value.join(", ") }] : [];
  }
  if (typeof value === "boolean") return [{ label, value: value ? "Yes" : "No" }];
  return [{ label, value: String(value) }];
}

function buildSections(p: StartupProfile): Section[] {
  return [
    {
      source: "github",
      title: "From your repo",
      fields: [
        ...present("Languages", p.technical.languages),
        ...present("Frameworks", p.technical.frameworks),
        ...present("Commit activity", p.technical.commit_frequency_note),
        ...present("Contributors", p.technical.contributor_count),
        ...present("Tests", p.technical.has_tests),
        ...present("CI", p.technical.has_ci),
        ...present("README", p.technical.readme_summary),
      ],
    },
    {
      source: "website",
      title: "From your website",
      fields: [
        ...present("Value proposition", p.product.value_proposition),
        ...present("Target market", p.product.target_market),
        ...present("Key features", p.product.key_features),
        ...present("Pricing", p.product.pricing_model_note),
      ],
    },
    {
      source: "pitch_deck",
      title: "From your pitch deck",
      fields: [
        ...present("Problem", p.pitch.problem_statement),
        ...present("Solution", p.pitch.solution_summary),
        ...present("Business model", p.pitch.business_model),
        ...present("Traction", p.pitch.traction_claims),
        ...present("Funding ask", p.pitch.funding_ask),
        ...present("Team", p.pitch.team_notes),
      ],
    },
    {
      source: "social",
      title: "From your socials",
      fields: [
        ...present("Platforms", p.social.platforms),
        ...present("Posting cadence", p.social.posting_cadence_note),
        ...present("Content themes", p.social.content_themes),
        ...Object.entries(p.social.follower_counts ?? {}).map(([k, v]) => ({
          label: `${k} followers`,
          value: String(v),
        })),
      ],
    },
  ];
}
