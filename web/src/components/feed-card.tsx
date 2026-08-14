"use client";

import { useState } from "react";
import { Heart, MessageCircle, Check, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

/**
 * Presentational only, for now.
 *
 * The backend has no posts/likes/comments/connections tables or endpoints yet —
 * that's the feed phase of the roadmap. This component renders the card shape so
 * the landing page can preview the networking layer honestly, and so the feed
 * page has something to mount the moment those endpoints land. Like/connect
 * state is local: nothing is persisted.
 */

export type ConnectionState = "none" | "pending" | "connected";

export interface FeedPost {
  id: string;
  startupName: string;
  authorName: string;
  authorRole: string;
  timestamp: string;
  body: string;
  likes: number;
  comments: number;
  connection?: ConnectionState;
}

function initials(name: string): string {
  return name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export function FeedCard({ post, className }: { post: FeedPost; className?: string }) {
  const [liked, setLiked] = useState(false);
  const [connection, setConnection] = useState<ConnectionState>(post.connection ?? "none");

  const likeCount = post.likes + (liked ? 1 : 0);

  return (
    <Card className={cn("gap-0 overflow-hidden py-0", className)}>
      <CardHeader className="flex-row items-center gap-3 px-5 py-4">
        <Avatar className="size-10">
          <AvatarFallback className="text-xs font-medium">
            {initials(post.startupName)}
          </AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{post.startupName}</p>
          <p className="truncate text-xs text-muted-foreground">
            {post.authorName} · {post.authorRole} · {post.timestamp}
          </p>
        </div>
        <ConnectButton state={connection} onChange={setConnection} />
      </CardHeader>

      <CardContent className="px-5 pb-4">
        <p className="text-sm leading-6 text-foreground/90">{post.body}</p>
      </CardContent>

      <Separator />

      <CardFooter className="gap-1 px-3 py-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setLiked((v) => !v)}
          className={cn(liked && "text-primary")}
        >
          <Heart className={cn("size-4 transition-transform", liked && "scale-110 fill-current")} />
          <span className="tabular">{likeCount}</span>
        </Button>
        <Button variant="ghost" size="sm">
          <MessageCircle className="size-4" />
          <span className="tabular">{post.comments}</span>
        </Button>
      </CardFooter>
    </Card>
  );
}

function ConnectButton({
  state,
  onChange,
}: {
  state: ConnectionState;
  onChange: (next: ConnectionState) => void;
}) {
  if (state === "connected") {
    return (
      <Button variant="ghost" size="sm" disabled>
        <Check className="size-4" />
        Connected
      </Button>
    );
  }

  if (state === "pending") {
    return (
      <Button variant="ghost" size="sm" onClick={() => onChange("none")}>
        <Clock className="size-4" />
        Pending
      </Button>
    );
  }

  return (
    <Button variant="outline" size="sm" onClick={() => onChange("pending")}>
      Connect
    </Button>
  );
}
