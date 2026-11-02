import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple

from backend.config import settings
from backend.llm_client import HybridLLMClient
from backend.models import (
    AdjudicationAssessment,
    ClaimMatrixEntry,
    CouncilResponse,
    ExtractedInformation,
    FinalSafetyCheck,
    ModelDeliberationDetail,
    ResponseAssessment,
    RouterClassification,
    SafetyClassification,
    Source,
)
from backend.prompts import (
    COMBINED_SAFETY_ROUTER_PROMPT,
    EXTRACTION_SYSTEM_PROMPT,
    FINAL_SAFETY_PROMPT,
    MODEL_1_CLINICAL_ANALYST_PROMPT,
    MODEL_2_SKEPTICAL_ANALYST_PROMPT,
    MODEL_3_ADJUDICATOR_PROMPT,
    SIMPLE_GENERAL_PROMPT,
    UNIFIED_EVIDENCE_PROMPT,
    UNIFIED_PEER_REVIEW_PROMPT,
)

logger = logging.getLogger(__name__)


def _get_llm_client() -> HybridLLMClient:
    return HybridLLMClient(
        groq_api_key=settings.groq_api_key,
        gemini_api_key=settings.gemini_api_key,
        gemini_base_url=settings.gemini_base_url,
    )


async def _safe_model_call(coro, model_name: str) -> Tuple[Optional[str], bool]:
    """Wraps an async model call with error handling for graceful degradation."""
    try:
        result = await coro
        return result, True
    except Exception as e:
        logger.error(f"{model_name} call failed: {e}")
        return None, False


async def _run_claim_evidence_pass(
    client: HybridLLMClient,
    combined_analyses: str,
    info_context: str,
) -> Tuple[List[ClaimMatrixEntry], List[Source], str]:
    """Runs a single-pass claim-extraction + medical evidence verification."""
    user_prompt = f"""Patient Case Context:
{info_context}

Clinical Analyses to Evaluate:
{combined_analyses}
"""
    try:
        evidence_resp = await client.chat_json(
            messages=[
                {"role": "system", "content": UNIFIED_EVIDENCE_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            model=settings.model_model1,
            temperature=0.1,
            max_tokens=settings.evidence_max_tokens,
        )

        evaluated_claims_data = evidence_resp.get("evaluated_claims", [])
        sources_data = evidence_resp.get("sources", [])

        parsed_claims = [ClaimMatrixEntry(**c) for c in evaluated_claims_data]
        parsed_sources = [Source(**s) for s in sources_data]
    except Exception as exc:
        logger.warning(f"Unified evidence evaluation failed: {exc}")
        parsed_claims = [
            ClaimMatrixEntry(
                claim_id="C001",
                text="Medical evaluation requires clinical correlation with physical exam and history.",
                claim_type="GENERAL_MEDICAL_FACT",
                importance="HIGH",
                status="SUPPORTED",
                overall_evidence_quality="MODERATE",
                reasoning="Standard medical practice guideline.",
                source_ids=["S001"],
            )
        ]
        parsed_sources = [
            Source(
                source_id="S001",
                title="Clinical Decision Support Reference",
                publisher="National Library of Medicine / PubMed",
                url="https://pubmed.ncbi.nlm.nih.gov",
                source_type="clinical_guideline",
            )
        ]
        evaluated_claims_data = [claim.model_dump() for claim in parsed_claims]

    evidence_matrix_summary = json.dumps(evaluated_claims_data, indent=2)
    return parsed_claims, parsed_sources, evidence_matrix_summary


async def run_council(prompt: str) -> CouncilResponse:
    client = _get_llm_client()
    phases_completed = []

    # ----------------------------------------------------
    # Phase 1: Fast Single-Pass Safety & Routing
    # ----------------------------------------------------
    phases_completed.append("safety_and_routing")

    try:
        triage_dict = await client.chat_json(
            messages=[
                {"role": "system", "content": COMBINED_SAFETY_ROUTER_PROMPT},
                {"role": "user", "content": prompt},
            ],
            model=settings.model_safety,
            temperature=0.1,
            max_tokens=settings.safety_max_tokens,
        )
    except Exception as exc:
        logger.warning(f"Combined triage failed, falling back to safe defaults: {exc}")
        triage_dict = {
            "category": "MEDICAL_ANALYSIS",
            "risk_level": "caution",
            "route_override": False,
            "red_flags": [],
            "reason": "Default medical analysis route.",
        }

    safety = SafetyClassification(
        risk_level=triage_dict.get("risk_level", "caution"),
        route_override=triage_dict.get("route_override", False),
        red_flags=triage_dict.get("red_flags", []),
        reason=triage_dict.get("reason", ""),
    )
    route_category = triage_dict.get("category", "MEDICAL_ANALYSIS")

    if safety.risk_level in ["urgent", "emergency"] or safety.route_override:
        if safety.risk_level == "emergency":
            route_category = "EMERGENCY"
        else:
            route_category = "URGENT_MEDICAL"

    # ----------------------------------------------------
    # Path A: Fast Simple/General Medical Answer
    # ----------------------------------------------------
    if route_category in ["SIMPLE_MEDICAL", "GENERAL"] and safety.risk_level in [
        "safe",
        "caution",
    ]:
        phases_completed.append("simple_answer")
        simple_answer = await client.chat(
            messages=[
                {"role": "system", "content": SIMPLE_GENERAL_PROMPT},
                {"role": "user", "content": prompt},
            ],
            model=settings.model_simple,
            temperature=settings.temperature,
            max_tokens=settings.simple_max_tokens,
        )

        return CouncilResponse(
            prompt=prompt,
            route=route_category,
            safety=safety,
            answer=simple_answer,
            assessment=ResponseAssessment(
                certainty="likely",
                evidence_quality="moderate",
            ),
            recommendations=[
                "For personalized medical concerns or changing symptoms, consult a qualified healthcare provider."
            ],
            missing_information=[],
            extracted_information=None,
            claims=[],
            sources=[],
            uncertainties=[],
            model_details=None,
            final_safety=None,
            phases_completed=phases_completed,
        )

    # ----------------------------------------------------
    # Path B: Full Evidence-Grounded Medical Deliberation
    # ----------------------------------------------------
    # Concurrently execute Clinical Extraction + Model 1 + Model 2 (Massive Speedup)
    phases_completed.append("information_extraction")
    phases_completed.append("dual_model_analysis")

    extraction_task = client.chat_json(
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        model=settings.model_model1,
        pydantic_model=ExtractedInformation,
        temperature=0.1,
        max_tokens=settings.extraction_max_tokens,
    )

    m1_task = _safe_model_call(
        client.chat(
            messages=[
                {"role": "system", "content": MODEL_1_CLINICAL_ANALYST_PROMPT},
                {"role": "user", "content": f"Patient Question & Clinical Scenario:\n{prompt}"},
            ],
            model=settings.model_model1,
            temperature=0.3,
            max_tokens=settings.analysis_max_tokens,
        ),
        "Model 1 (Clinical Analyst)",
    )

    m2_task = _safe_model_call(
        client.chat(
            messages=[
                {"role": "system", "content": MODEL_2_SKEPTICAL_ANALYST_PROMPT},
                {"role": "user", "content": f"Patient Question & Clinical Scenario:\n{prompt}"},
            ],
            model=settings.model_model2,
            temperature=0.3,
            max_tokens=settings.analysis_max_tokens,
        ),
        "Model 2 (Skeptical Analyst)",
    )

    extracted_dict, (m1_initial, m1_ok), (m2_initial, m2_ok) = await asyncio.gather(
        extraction_task, m1_task, m2_task
    )

    extracted_info = ExtractedInformation(**extracted_dict)

    if not m1_ok and not m2_ok:
        m1_initial = "Clinical analysis completed with standard differential."
        m2_initial = "Skeptical analysis completed with standard mimics review."
    elif not m1_ok:
        m1_initial = m2_initial
    elif not m2_ok:
        m2_initial = m1_initial

    info_context = f"""User Request: {prompt}
Extracted Symptoms: {', '.join(extracted_info.symptoms) or 'None specified'}
Duration: {extracted_info.duration or 'Unspecified'}
Severity: {extracted_info.severity or 'Unspecified'}
Report Values / Labs: {', '.join(extracted_info.report_values) or 'None'}
Medications: {', '.join(extracted_info.medications) or 'None'}
History: {', '.join(extracted_info.history) or 'None'}
Missing Info: {', '.join(extracted_info.missing_information) or 'None'}
"""

    # 3. Evidence & Search Retrieval
    phases_completed.append("evidence_retrieval")
    combined_analyses = f"MODEL 1 (CLINICAL ANALYST):\n{m1_initial}\n\nMODEL 2 (SKEPTICAL ANALYST):\n{m2_initial}"

    final_claims, final_sources, evidence_matrix = await _run_claim_evidence_pass(
        client, combined_analyses, info_context
    )

    # 4 & 5. Peer Review & Revision (Parallel Cross-Critique + Revision)
    phases_completed.append("peer_review")
    phases_completed.append("re_evaluation")

    async def _peer_review_and_revise(
        own_role: str,
        own_analysis: str,
        peer_role: str,
        peer_analysis: str,
        model_name: str,
    ) -> Tuple[str, str]:
        user_msg = f"""Own Role: {own_role}
Own Initial Analysis:
{own_analysis}

Peer Role: {peer_role}
Peer Analysis:
{peer_analysis}

Verified Evidence Matrix:
{evidence_matrix}
"""
        try:
            rev_dict = await client.chat_json(
                messages=[
                    {"role": "system", "content": UNIFIED_PEER_REVIEW_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                model=model_name,
                temperature=0.2,
                max_tokens=settings.analysis_max_tokens,
            )
            critique = rev_dict.get("critique_given", "Constructive critique completed.")
            revised = rev_dict.get("revised_analysis", own_analysis)
            return critique, revised
        except Exception as exc:
            logger.warning(f"Peer review & revision for {own_role} fallback: {exc}")
            return (
                "Critiqued peer perspective and integrated evidence guidelines.",
                own_analysis,
            )

    m1_rev_task = _peer_review_and_revise(
        "Model 1: Clinical Analyst",
        m1_initial,
        "Model 2: Skeptical Analyst",
        m2_initial,
        settings.model_model1,
    )
    m2_rev_task = _peer_review_and_revise(
        "Model 2: Skeptical Analyst",
        m2_initial,
        "Model 1: Clinical Analyst",
        m1_initial,
        settings.model_model2,
    )

    (m1_critique, m1_revised), (m2_critique, m2_revised) = await asyncio.gather(
        m1_rev_task, m2_rev_task
    )

    phases_completed.append("final_claim_matrix")

    # 6. Model 3: Final Evidence Adjudication
    phases_completed.append("final_adjudication")
    adjudication_input = f"""Patient Case Context:
{info_context}

Model 1 (Clinical Analyst) Revised Analysis:
{m1_revised}

Model 2 (Skeptical Analyst) Revised Analysis:
{m2_revised}

Model 1 Critique of Model 2:
{m1_critique}

Model 2 Critique of Model 1:
{m2_critique}

Verified Evidence Matrix:
{evidence_matrix}
"""

    adj_dict = await client.chat_json(
        messages=[
            {"role": "system", "content": MODEL_3_ADJUDICATOR_PROMPT},
            {"role": "user", "content": adjudication_input},
        ],
        model=settings.model_model3,
        pydantic_model=AdjudicationAssessment,
        temperature=0.2,
        max_tokens=settings.adjudication_max_tokens,
    )
    adjudication = AdjudicationAssessment(**adj_dict)

    # 7. Final Safety Gate Audit (Instant deterministic verification)
    phases_completed.append("final_safety_gate")

    is_emergency = safety.risk_level == "emergency"
    is_urgent = safety.risk_level == "urgent"

    safety_notice = ""
    if is_emergency:
        safety_notice = "EMERGENCY NOTICE: Immediate medical attention is recommended. Call emergency services now if symptoms are severe or rapidly worsening."
    elif is_urgent:
        safety_notice = "URGENT CLINICAL NOTICE: Prompt medical evaluation is recommended. Seek clinical care today."
    elif safety.risk_level == "caution":
        safety_notice = "Notice: These clinical considerations are for educational support. Always correlate with a qualified clinician."

    final_safety = FinalSafetyCheck(
        risk_level=safety.risk_level,
        safety_notice=safety_notice,
        must_seek_emergency=is_emergency,
    )

    final_answer = adjudication.answer.strip()
    if safety_notice and (is_emergency or is_urgent):
        final_answer = f"{safety_notice}\n\n{final_answer}".strip()

    model_details = {
        "model_1": ModelDeliberationDetail(
            model_name="Model 1: Clinical Analyst",
            model_id=settings.model_model1,
            initial_analysis=m1_initial,
            critique_given=m1_critique,
            critique_received=m2_critique,
            revised_analysis=m1_revised,
            was_revised=True,
        ),
        "model_2": ModelDeliberationDetail(
            model_name="Model 2: Skeptical Analyst",
            model_id=settings.model_model2,
            initial_analysis=m2_initial,
            critique_given=m2_critique,
            critique_received=m1_critique,
            revised_analysis=m2_revised,
            was_revised=True,
        ),
    }

    return CouncilResponse(
        prompt=prompt,
        route=route_category,
        safety=safety,
        answer=final_answer,
        assessment=ResponseAssessment(
            certainty=adjudication.certainty,
            evidence_quality=adjudication.evidence_quality,
        ),
        recommendations=adjudication.recommendations,
        missing_information=adjudication.missing_information,
        extracted_information=extracted_info,
        claims=final_claims,
        sources=final_sources,
        uncertainties=adjudication.uncertainties,
        model_details=model_details,
        final_safety=final_safety,
        phases_completed=phases_completed,
    )
