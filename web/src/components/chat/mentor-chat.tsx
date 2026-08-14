"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ArrowUp, MessagesSquare, TriangleAlert, User } from "lucide-react";
import { MentorAvatar } from "@/components/mentor-avatar";
import { SourceChip } from "@/components/source-chip";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { mentorFor } from "@/lib/taxonomy";
import type { ChatResponse, SourceType, StartupProfile } from "@/lib/types";

interface ChatMessage {
  role: "user" | "mentor";
  text: string;
  specialists?: string[];
  groundingIssues?: string[];
}

const SUGGESTIONS = [
  "What's the weakest part of my pitch?",
  "Is my repo investor-ready?",
  "Who is my product actually for?",
];

export function MentorChat({
  profileId,
  profile,
}: {
  profileId: string;
  profile: StartupProfile;
}) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [asking, setAsking] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, asking]);

  // Auto-resize the composer up to a ceiling, so long questions stay readable.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [question]);

  async function send(text: string) {
    const asked = text.trim();
    if (!asked || asking) return;

    setMessages((prev) => [...prev, { role: "user", text: asked }]);
    setQuestion("");
    setAsking(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile_id: profileId, question: asked }),
    });
    const data: ChatResponse & { error?: string; detail?: string } = await res.json();
    setAsking(false);

    if (!res.ok) {
      toast.error(data.error ?? data.detail ?? "Something went wrong answering that.");
      setMessages((prev) => prev.slice(0, -1));
      return;
    }

    setMessages((prev) => [
      ...prev,
      {
        role: "mentor",
        text: data.reply,
        specialists: data.specialists_used,
        groundingIssues: data.remaining_grounding_issues,
      },
    ]);
  }

  return (
    <Card className="flex h-[640px] flex-col gap-0 overflow-hidden py-0">
      <CardHeader className="border-b px-5 py-4">
        <CardTitle className="text-base">Ask your mentors</CardTitle>
      </CardHeader>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5">
        {messages.length === 0 && !asking ? (
          <EmptyState
            icon={MessagesSquare}
            title="No questions yet"
            description="Ask about your code, product, pitch or growth — answers are grounded in the evidence on this page."
            action={
              <div className="flex flex-wrap justify-center gap-2 pt-1">
                {SUGGESTIONS.map((s) => (
                  <Button key={s} variant="outline" size="sm" onClick={() => send(s)}>
                    {s}
                  </Button>
                ))}
              </div>
            }
          />
        ) : (
          <div className="space-y-6">
            {messages.map((m, i) =>
              m.role === "user" ? (
                <UserBubble key={i} text={m.text} />
              ) : (
                <MentorBubble key={i} message={m} profile={profile} />
              )
            )}
            {asking && <ThinkingIndicator />}
          </div>
        )}
      </div>

      <CardContent className="border-t p-3">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(question);
          }}
          className="flex items-end gap-2"
        >
          <Textarea
            ref={textareaRef}
            rows={1}
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(question);
              }
            }}
            className="max-h-40 min-h-10 resize-none"
          />
          <Button
            type="submit"
            size="icon"
            disabled={asking || !question.trim()}
            aria-label="Send"
          >
            <ArrowUp className="size-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex flex-row-reverse items-start gap-3">
      <span className="inline-flex size-9 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <User className="size-4" />
      </span>
      <p className="max-w-[80%] rounded-lg rounded-tr-sm bg-primary px-3 py-2 text-sm leading-6 text-primary-foreground">
        {text}
      </p>
    </div>
  );
}

function MentorBubble({
  message,
  profile,
}: {
  message: ChatMessage;
  profile: StartupProfile;
}) {
  const specialists = message.specialists ?? [];
  const lead = specialists.length === 1 ? specialists[0] : undefined;
  const mentors = specialists.map(mentorFor).filter(Boolean);

  return (
    <div className="flex items-start gap-3">
      <MentorAvatar specialist={lead} />
      <div className="min-w-0 max-w-[85%] space-y-2">
        {mentors.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {mentors.map((m) => (
              <Badge key={m!.key} variant="secondary" className="text-xs">
                {m!.name}
              </Badge>
            ))}
          </div>
        )}

        <div className="rounded-lg rounded-tl-sm bg-muted px-3 py-2 text-sm leading-6 whitespace-pre-wrap">
          {message.text}
        </div>

        {mentors.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {mentors.map((m) => (
              <SourceChip
                key={m!.source}
                source={m!.source}
                href={profile.source_links?.[m!.source as SourceType]}
              />
            ))}
          </div>
        )}

        {message.groundingIssues && message.groundingIssues.length > 0 && (
          <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-muted-foreground">
            <TriangleAlert className="mt-0.5 size-3.5 shrink-0 text-destructive" />
            <div>
              <p className="font-medium text-destructive">Unverified figures</p>
              <p>
                These couldn&apos;t be matched back to the evidence log:{" "}
                {message.groundingIssues.join("; ")}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <MentorAvatar />
      <div className="flex items-center gap-1.5 rounded-lg rounded-tl-sm bg-muted px-3 py-3">
        {[0, 150, 300].map((delay) => (
          <span
            key={delay}
            className="size-1.5 animate-bounce rounded-full bg-muted-foreground/50"
            style={{ animationDelay: `${delay}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
