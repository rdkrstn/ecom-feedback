export type ReviewStatus = "draft" | "running" | "waiting_for_band" | "changes_required" | "completed" | "failed";
export type Priority = "low" | "medium" | "high";
export type Frequency = "low" | "medium" | "high";

export interface FeedbackReviewInput {
  product_name: string;
  product_category: string;
  product_description?: string | null;
  support_tickets: string;
  customer_reviews: string;
  return_reasons?: string | null;
  social_comments?: string | null;
  current_faq?: string | null;
  product_page_copy?: string | null;
  main_business_concern?: string | null;
}

export interface DetectedIssue {
  issue: string;
  frequency: Frequency;
  source_types: string[];
  customer_language: string[];
  business_impact: string[];
  recommended_action: string;
}

export interface UGCBrief {
  title: string;
  goal: string;
  source_issue: string;
  creator_instructions: string[];
  hooks: string[];
  shot_list: string[];
  proof_needed: string[];
}

export interface SupportMacro {
  name: string;
  use_case: string;
  body: string;
  related_issue: string;
}

export interface FAQUpdate {
  question: string;
  answer: string;
  related_issue: string;
}

export interface ProductPageTask {
  section: string;
  task: string;
  reason: string;
  related_issue: string;
  priority: Priority;
}

export interface OwnerTask {
  owner: "Content" | "Support" | "Storefront" | "Operations";
  task: string;
  priority: Priority;
  source_agent: string;
  related_issue: string;
}

export interface FinalReport {
  status: "changes_required" | "completed";
  primary_customer_issue: string;
  priority: Priority;
  executive_summary: string;
  detected_issues: DetectedIssue[];
  ugc_briefs: UGCBrief[];
  support_macros: SupportMacro[];
  faq_updates: FAQUpdate[];
  product_page_tasks: ProductPageTask[];
  owner_handoff: OwnerTask[];
  source_evidence: string[];
  next_review_recommendation: string;
}

export interface ReviewRecord {
  id: string;
  input: FeedbackReviewInput;
  status: ReviewStatus;
  final_report: FinalReport | null;
  created_at: string;
  updated_at: string;
}

export interface AgentEvent {
  id: string;
  review_id: string;
  agent_key: string;
  agent_name: string;
  event_type: string;
  status: string;
  summary: string;
  payload: Record<string, unknown>;
  source_agents: string[];
  handoff_to: string[];
  band_room_id?: string | null;
  band_message_id?: string | null;
  created_at: string;
}

export interface KickoffMessage {
  review_id: string;
  kickoff_message: string;
}
