import React from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { CouncilResponse } from "../types";

interface MedicalAssessmentProps {
  result: CouncilResponse;
}

export const MedicalAssessment: React.FC<MedicalAssessmentProps> = ({
  result,
}) => {
  const {
    safety,
    answer,
    assessment,
    recommendations,
    missing_information,
    route,
    extracted_information,
  } = result;

  const isEmergency = safety.risk_level === "emergency";
  const isUrgent = safety.risk_level === "urgent";
  const isCaution = safety.risk_level === "caution";

  const certaintyLabels: Record<string, { label: string; color: string }> = {
    likely: { label: "Likely", color: "#10b981" },
    possible: { label: "Possible", color: "#3b82f6" },
    unclear: { label: "Unclear", color: "#f59e0b" },
    cannot_determine: { label: "Cannot Determine", color: "#ef4444" },
  };

  const evidenceQualityLabels: Record<string, { label: string; color: string }> = {
    strong: { label: "Strong Evidence", color: "#10b981" },
    moderate: { label: "Moderate Evidence", color: "#3b82f6" },
    limited: { label: "Limited Evidence", color: "#f59e0b" },
    insufficient: { label: "Insufficient Evidence", color: "#ef4444" },
  };

  const certaintyInfo =
    certaintyLabels[assessment.certainty] || certaintyLabels["possible"];
  const evidenceInfo =
    evidenceQualityLabels[assessment.evidence_quality] ||
    evidenceQualityLabels["moderate"];

  return (
    <div className="medical-assessment">
      {(isEmergency || isUrgent || isCaution) && (
        <motion.div
          className={`safety-banner safety-banner--${safety.risk_level}`}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="safety-banner__header">
            <span className="safety-banner__icon">
              {isEmergency ? "🚨 EMERGENCY ALERT" : isUrgent ? "⚠️ URGENT MEDICAL NOTICE" : "ℹ️ CAUTION"}
            </span>
            <span className="safety-banner__badge">{safety.risk_level.toUpperCase()}</span>
          </div>
          <p className="safety-banner__reason">
            {safety.reason ||
              (isEmergency
                ? "Immediate emergency symptoms detected. Please call emergency services (911) or go to the nearest emergency department immediately."
                : "Prompt clinical evaluation by a medical professional is strongly advised.")}
          </p>
          {safety.red_flags.length > 0 && (
            <ul className="safety-banner__flags">
              {safety.red_flags.map((flag, idx) => (
                <li key={idx}>• {flag}</li>
              ))}
            </ul>
          )}
        </motion.div>
      )}

      <div className="assessment-card">
        <div className="assessment-card__header">
          <div className="assessment-card__title-group">
            <h2 className="assessment-card__title">Clinical Assessment</h2>
            <span className="assessment-card__route-tag">{route}</span>
          </div>

          <div className="assessment-card__badges">
            <span
              className="meta-badge"
              style={{
                borderColor: certaintyInfo.color,
                color: certaintyInfo.color,
              }}
            >
              Certainty: {certaintyInfo.label}
            </span>

            <span
              className="meta-badge"
              style={{
                borderColor: evidenceInfo.color,
                color: evidenceInfo.color,
              }}
            >
              Quality: {evidenceInfo.label}
            </span>
          </div>
        </div>

        <div className="assessment-card__body">
          <div className="assessment-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
          </div>
        </div>

        {extracted_information && (
          <div className="assessment-section">
            <h3 className="assessment-section__title">🧭 Relevant Extracted Information</h3>
            <ul className="assessment-section__list">
              {extracted_information.symptoms.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Symptoms:</strong> {extracted_information.symptoms.join(", ")}
                </li>
              )}
              {extracted_information.duration && (
                <li className="assessment-section__item">
                  <strong>Duration:</strong> {extracted_information.duration}
                </li>
              )}
              {extracted_information.severity && (
                <li className="assessment-section__item">
                  <strong>Severity:</strong> {extracted_information.severity}
                </li>
              )}
              {extracted_information.age && (
                <li className="assessment-section__item">
                  <strong>Age:</strong> {extracted_information.age}
                </li>
              )}
              {extracted_information.sex && (
                <li className="assessment-section__item">
                  <strong>Sex:</strong> {extracted_information.sex}
                </li>
              )}
              {extracted_information.report_values.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Report Values:</strong> {extracted_information.report_values.join(", ")}
                </li>
              )}
              {extracted_information.medications.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Medications:</strong> {extracted_information.medications.join(", ")}
                </li>
              )}
              {extracted_information.history.length > 0 && (
                <li className="assessment-section__item">
                  <strong>History:</strong> {extracted_information.history.join(", ")}
                </li>
              )}
              {extracted_information.missing_information.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Missing:</strong> {extracted_information.missing_information.join(", ")}
                </li>
              )}
              {extracted_information.ambiguous_information.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Ambiguous:</strong> {extracted_information.ambiguous_information.join(", ")}
                </li>
              )}
              {extracted_information.unreadable_information.length > 0 && (
                <li className="assessment-section__item">
                  <strong>Unreadable:</strong> {extracted_information.unreadable_information.join(", ")}
                </li>
              )}
            </ul>
          </div>
        )}

        {recommendations.length > 0 && (
          <div className="assessment-section">
            <h3 className="assessment-section__title">💡 Recommended Next Steps</h3>
            <ul className="assessment-section__list">
              {recommendations.map((rec, idx) => (
                <li key={idx} className="assessment-section__item">
                  <span className="bullet">▸</span> {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {missing_information.length > 0 && (
          <div className="assessment-section assessment-section--missing">
            <h3 className="assessment-section__title">
              🔍 What Could Change This Assessment
            </h3>
            <p className="assessment-section__sub">
              The following additional clinical details would improve diagnostic clarity:
            </p>
            <ul className="assessment-section__list">
              {missing_information.map((item, idx) => (
                <li key={idx} className="assessment-section__item">
                  <span className="bullet">?</span> {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
