export type SourceType = "github" | "website" | "pitch_deck" | "social";

export interface Evidence {
  source: SourceType;
  claim: string;
  detail?: string | null;
}

export interface TechnicalProfile {
  languages: string[];
  frameworks: string[];
  last_commit_date?: string | null;
  commit_frequency_note?: string | null;
  contributor_count?: number | null;
  has_tests?: boolean | null;
  has_ci?: boolean | null;
  readme_summary?: string | null;
}

export interface ProductProfile {
  value_proposition?: string | null;
  target_market?: string | null;
  key_features: string[];
  pricing_model_note?: string | null;
}

export interface PitchProfile {
  problem_statement?: string | null;
  solution_summary?: string | null;
  business_model?: string | null;
  traction_claims: string[];
  funding_ask?: string | null;
  team_notes?: string | null;
}

export interface SocialProfile {
  platforms: string[];
  follower_counts: Record<string, number>;
  posting_cadence_note?: string | null;
  content_themes: string[];
}

export interface StartupProfile {
  company_name?: string | null;
  one_line_summary?: string | null;
  source_links: Record<string, string>;
  unreachable_sources: SourceType[];
  technical: TechnicalProfile;
  product: ProductProfile;
  pitch: PitchProfile;
  social: SocialProfile;
  evidence_log: Evidence[];
  created_at?: string | null;
}

export interface ProfileStatusResponse {
  status: string;
  error?: string | null;
  profile: StartupProfile | null;
}

export interface ChatResponse {
  reply: string;
  specialists_used: string[];
  remaining_grounding_issues: string[];
}
