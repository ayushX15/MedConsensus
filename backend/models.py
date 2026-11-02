from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CouncilRequest(BaseModel):
    prompt: str


class SafetyClassification(BaseModel):
    risk_level: str = Field(
        ..., description="safe | caution | urgent | emergency"
    )
    route_override: bool = False
    red_flags: List[str] = Field(default_factory=list)
    reason: str = ""


class RouterClassification(BaseModel):
    category: str = Field(
        ...,
        description="SIMPLE_MEDICAL | GENERAL | MEDICAL_ANALYSIS | URGENT_MEDICAL | EMERGENCY",
    )
    reason: str = ""


class ExtractedInformation(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity: Optional[str] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    report_values: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    history: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    ambiguous_information: List[str] = Field(default_factory=list)
    unreadable_information: List[str] = Field(default_factory=list)


class Claim(BaseModel):
    claim_id: str
    text: str
    claim_type: str = Field(
        "GENERAL_MEDICAL_FACT",
        description="GENERAL_MEDICAL_FACT | PATIENT_SPECIFIC_INFERENCE | RECOMMENDATION | STATISTICAL_CLAIM | SAFETY_CLAIM | OTHER",
    )
    importance: str = Field("HIGH", description="HIGH | MEDIUM | LOW")


class Source(BaseModel):
    source_id: str
    title: str
    publisher: str = "Medical Reference / Web Search"
    url: str
    source_type: str = Field(
        "medical_reference",
        description="clinical_guideline | systematic_review | peer_reviewed_study | public_health | academic_institution | medical_reference | other",
    )


class ClaimEvidenceEvaluation(BaseModel):
    claim_id: str
    source_id: str
    relationship: str = Field(
        "SUPPORTS",
        description="SUPPORTS | PARTIALLY_SUPPORTS | CONTRADICTS | DOES_NOT_ADDRESS",
    )
    evidence_quality: str = Field(
        "MODERATE", description="HIGH | MODERATE | LOW | VERY_LOW"
    )
    reason: str = ""


class ClaimMatrixEntry(BaseModel):
    claim_id: str
    text: str
    claim_type: str = "GENERAL_MEDICAL_FACT"
    importance: str = "HIGH"
    status: str = Field(
        "SUPPORTED",
        description="SUPPORTED | PARTIALLY_SUPPORTED | WEAKLY_SUPPORTED | CONTRADICTED | INSUFFICIENT_EVIDENCE | NOT_VERIFIABLE",
    )
    overall_evidence_quality: str = Field(
        "MODERATE", description="HIGH | MODERATE | LOW | VERY_LOW"
    )
    reasoning: str = ""
    source_ids: List[str] = Field(default_factory=list)


class UncertaintyItem(BaseModel):
    topic: str
    description: str
    competing_hypotheses: List[str] = Field(default_factory=list)
    distinguishing_factors: List[str] = Field(default_factory=list)


class AdjudicationAssessment(BaseModel):
    answer: str
    certainty: str = Field(
        "possible", description="likely | possible | unclear | cannot_determine"
    )
    evidence_quality: str = Field(
        "moderate", description="strong | moderate | limited | insufficient"
    )
    recommendations: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    uncertainties: List[UncertaintyItem] = Field(default_factory=list)


class ResponseAssessment(BaseModel):
    certainty: str = Field(
        "possible", description="likely | possible | unclear | cannot_determine"
    )
    evidence_quality: str = Field(
        "moderate", description="strong | moderate | limited | insufficient"
    )


class FinalSafetyCheck(BaseModel):
    risk_level: str = "safe"  # safe | caution | urgent | emergency
    safety_notice: str = ""
    must_seek_emergency: bool = False


class ModelDeliberationDetail(BaseModel):
    model_name: str
    model_id: str
    initial_analysis: str
    critique_given: str = ""
    critique_received: str = ""
    revised_analysis: str = ""
    was_revised: bool = False


class CouncilResponse(BaseModel):
    prompt: str
    route: str
    safety: SafetyClassification
    answer: str
    assessment: ResponseAssessment
    recommendations: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    extracted_information: Optional[ExtractedInformation] = None
    claims: List[ClaimMatrixEntry] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    uncertainties: List[UncertaintyItem] = Field(default_factory=list)
    model_details: Optional[Dict[str, ModelDeliberationDetail]] = None
    final_safety: Optional[FinalSafetyCheck] = None
    phases_completed: List[str] = Field(default_factory=list)
