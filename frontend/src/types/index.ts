export interface SafetyClassification {
  risk_level: "safe" | "caution" | "urgent" | "emergency";
  route_override: boolean;
  red_flags: string[];
  reason: string;
}

export interface ClaimMatrixEntry {
  claim_id: string;
  text: string;
  claim_type: string;
  importance: string;
  status:
    | "SUPPORTED"
    | "PARTIALLY_SUPPORTED"
    | "WEAKLY_SUPPORTED"
    | "CONTRADICTED"
    | "INSUFFICIENT_EVIDENCE"
    | "NOT_VERIFIABLE";
  overall_evidence_quality: "HIGH" | "MODERATE" | "LOW" | "VERY_LOW";
  reasoning: string;
  source_ids: string[];
}

export interface Source {
  source_id: string;
  title: string;
  publisher: string;
  url: string;
  source_type: string;
}

export interface UncertaintyItem {
  topic: string;
  description: string;
  competing_hypotheses: string[];
  distinguishing_factors: string[];
}

export interface ExtractedInformation {
  symptoms: string[];
  duration?: string | null;
  severity?: string | null;
  age?: string | null;
  sex?: string | null;
  report_values: string[];
  medications: string[];
  history: string[];
  missing_information: string[];
  ambiguous_information: string[];
  unreadable_information: string[];
}

export interface FinalSafetyCheck {
  risk_level: "safe" | "caution" | "urgent" | "emergency";
  safety_notice: string;
  must_seek_emergency: boolean;
}

export interface ResponseAssessment {
  certainty: "likely" | "possible" | "unclear" | "cannot_determine";
  evidence_quality: "strong" | "moderate" | "limited" | "insufficient";
}

export interface ModelDeliberationDetail {
  model_name: string;
  model_id: string;
  initial_analysis: string;
  critique_given: string;
  critique_received: string;
  revised_analysis: string;
  was_revised: boolean;
}

export type ModelResponse = ModelDeliberationDetail;

export interface CouncilResponse {
  prompt: string;
  route: string;
  safety: SafetyClassification;
  answer: string;
  assessment: ResponseAssessment;
  recommendations: string[];
  missing_information: string[];
  extracted_information?: ExtractedInformation | null;
  claims: ClaimMatrixEntry[];
  sources: Source[];
  uncertainties: UncertaintyItem[];
  model_details?: Record<string, ModelDeliberationDetail> | null;
  final_safety?: FinalSafetyCheck | null;
  phases_completed: string[];
}

export type Phase =
  | "idle"
  | "safety_and_routing"
  | "information_extraction"
  | "dual_model_analysis"
  | "evidence_retrieval"
  | "peer_review"
  | "re_evaluation"
  | "final_adjudication"
  | "final_safety_gate"
  | "done"
  | "error";
