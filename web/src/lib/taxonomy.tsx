import { Code2, Globe, Presentation, Megaphone, type LucideIcon } from "lucide-react";
import type { SourceType } from "@/lib/types";

/**
 * The four ingestion sources and the four specialist mentors are a 1:1 mapping
 * in the backend (src/mentorship/nodes.py SPECIALIST_CONFIG) — each mentor sees
 * exactly one source's slice of the evidence. Keeping both in one file means the
 * icon/label a source gets on the profile page is the same one its mentor gets
 * in chat, instead of the two drifting apart.
 */

export interface SourceMeta {
  label: string;
  icon: LucideIcon;
}

export const SOURCE_META: Record<SourceType, SourceMeta> = {
  github: { label: "GitHub", icon: Code2 },
  website: { label: "Website", icon: Globe },
  pitch_deck: { label: "Pitch deck", icon: Presentation },
  social: { label: "Social", icon: Megaphone },
};

export type SpecialistKey = "technical" | "product" | "pitch" | "growth";

export interface MentorMeta {
  key: SpecialistKey;
  name: string;
  specialty: string;
  source: SourceType;
  icon: LucideIcon;
}

export const MENTORS: Record<SpecialistKey, MentorMeta> = {
  technical: {
    key: "technical",
    name: "Technical mentor",
    specialty: "Code health, architecture, and engineering practice",
    source: "github",
    icon: Code2,
  },
  product: {
    key: "product",
    name: "Product mentor",
    specialty: "Positioning, value proposition, and target market",
    source: "website",
    icon: Globe,
  },
  pitch: {
    key: "pitch",
    name: "Fundraising mentor",
    specialty: "Narrative, traction evidence, and investor readiness",
    source: "pitch_deck",
    icon: Presentation,
  },
  growth: {
    key: "growth",
    name: "Growth mentor",
    specialty: "Social presence, audience, and engagement",
    source: "social",
    icon: Megaphone,
  },
};

export const MENTOR_LIST = Object.values(MENTORS);

export function mentorFor(key: string): MentorMeta | undefined {
  return MENTORS[key as SpecialistKey];
}
