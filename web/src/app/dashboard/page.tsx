"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Loader2, Sparkles, ArrowRight } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { SOURCE_META } from "@/lib/taxonomy";
import type { SourceType } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const FIELDS: {
  source: SourceType;
  key: "github_url" | "website_url" | "pitch_deck_url" | "social_url";
  placeholder: string;
  hint: string;
}[] = [
  {
    source: "github",
    key: "github_url",
    placeholder: "https://github.com/you/repo",
    hint: "Public repo — we read languages, commits, tests and CI.",
  },
  {
    source: "website",
    key: "website_url",
    placeholder: "https://yourstartup.com",
    hint: "Your landing page — positioning, features, pricing.",
  },
  {
    source: "pitch_deck",
    key: "pitch_deck_url",
    placeholder: "https://.../deck.pdf",
    hint: "Direct PDF link only — DocSend and Slides aren't supported yet.",
  },
  {
    source: "social",
    key: "social_url",
    placeholder: "https://x.com/yourstartup",
    hint: "Public profile — we read open metadata, never log in.",
  },
];

type FormState = Record<string, string>;

export default function DashboardPage() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>({});
  const [submitting, setSubmitting] = useState(false);

  const filledCount = FIELDS.filter((f) => form[f.key]?.trim()).length;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (filledCount === 0) {
      toast.error("Add at least one link to get started");
      return;
    }

    setSubmitting(true);
    const res = await fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        github_url: form.github_url || null,
        website_url: form.website_url || null,
        pitch_deck_url: form.pitch_deck_url || null,
        social_url: form.social_url || null,
      }),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      setSubmitting(false);
      toast.error(data.error ?? data.detail ?? "Could not start building the profile");
      return;
    }

    router.push(`/profile/${data.profile_id}`);
  }

  return (
    <AppShell>
      <main className="mx-auto w-full max-w-2xl px-6 py-10">
        <div className="mb-8 space-y-1">
          <h1 className="text-2xl font-semibold">Build a startup profile</h1>
          <p className="text-muted-foreground">
            Add whichever links you have. Sources you skip are reported as unreachable
            rather than guessed at.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Your sources</CardTitle>
            <CardDescription className="tabular">
              {filledCount} of {FIELDS.length} added
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-6">
              {FIELDS.map((field) => {
                const meta = SOURCE_META[field.source];
                const Icon = meta.icon;
                return (
                  <div key={field.key} className="space-y-2">
                    <Label htmlFor={field.key} className="gap-2">
                      <Icon className="size-4 text-muted-foreground" />
                      {meta.label}
                    </Label>
                    <Input
                      id={field.key}
                      type="url"
                      inputMode="url"
                      placeholder={field.placeholder}
                      className="h-11"
                      value={form[field.key] ?? ""}
                      onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                    />
                    <p className="text-xs text-muted-foreground">{field.hint}</p>
                  </div>
                );
              })}

              <Separator />

              <Button type="submit" size="lg" className="h-11 w-full" disabled={submitting}>
                {submitting && <Loader2 className="size-4 animate-spin" />}
                {submitting ? "Starting..." : "Build my profile"}
                {!submitting && <ArrowRight className="size-4" />}
              </Button>
            </CardContent>
          </form>
        </Card>

        <div className="my-6 flex items-center gap-3">
          <Separator className="flex-1" />
          <span className="text-xs text-muted-foreground">or</span>
          <Separator className="flex-1" />
        </div>

        <Card>
          <CardContent className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1">
              <p className="font-medium">Try the demo profile</p>
              <p className="text-sm text-muted-foreground">
                A fully-built fictional startup — skip the wait and go straight to chat.
              </p>
            </div>
            <Button variant="outline" onClick={() => router.push("/profile/demo")}>
              <Sparkles className="size-4" />
              Load demo
            </Button>
          </CardContent>
        </Card>
      </main>
    </AppShell>
  );
}
