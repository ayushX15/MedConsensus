import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { ClaimMatrixEntry, Source } from "../types";

interface EvidenceSectionProps {
  claims: ClaimMatrixEntry[];
  sources: Source[];
}

export const EvidenceSection: React.FC<EvidenceSectionProps> = ({
  claims,
  sources,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedClaimId, setExpandedClaimId] = useState<string | null>(null);

  if (claims.length === 0 && sources.length === 0) {
    return null;
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SUPPORTED":
        return { label: "Strongly Supported", color: "#10b981", bg: "rgba(16, 185, 129, 0.1)" };
      case "PARTIALLY_SUPPORTED":
        return { label: "Partially Supported", color: "#3b82f6", bg: "rgba(59, 130, 246, 0.1)" };
      case "WEAKLY_SUPPORTED":
        return { label: "Weakly Supported", color: "#f59e0b", bg: "rgba(245, 158, 11, 0.1)" };
      case "CONTRADICTED":
        return { label: "Contradicted", color: "#ef4444", bg: "rgba(239, 68, 68, 0.1)" };
      case "INSUFFICIENT_EVIDENCE":
      case "NOT_VERIFIABLE":
      default:
        return { label: "Insufficient Evidence", color: "#9ca3af", bg: "rgba(156, 163, 175, 0.1)" };
    }
  };

  const getSourceById = (sourceId: string) => {
    return sources.find((s) => s.source_id === sourceId);
  };

  return (
    <div className="evidence-accordion">
      <button
        className="evidence-accordion__header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="evidence-accordion__title-group">
          <span className="evidence-accordion__icon">📚</span>
          <h3>Evidence & Source Verification</h3>
          <span className="evidence-accordion__count">
            {claims.length} Claims • {sources.length} Verified Sources
          </span>
        </div>
        <span className={`evidence-accordion__chevron ${isOpen ? "open" : ""}`}>
          ▼
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="evidence-accordion__content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="claims-grid">
              {claims.map((claim) => {
                const statusInfo = getStatusBadge(claim.status);
                const isExpanded = expandedClaimId === claim.claim_id;
                const claimSources = claim.source_ids
                  .map(getSourceById)
                  .filter((s): s is Source => s !== undefined);

                return (
                  <div key={claim.claim_id} className="claim-card">
                    <div
                      className="claim-card__header"
                      onClick={() =>
                        setExpandedClaimId(isExpanded ? null : claim.claim_id)
                      }
                    >
                      <div className="claim-card__title-row">
                        <span className="claim-card__id">{claim.claim_id}</span>
                        <p className="claim-card__text">{claim.text}</p>
                      </div>

                      <div className="claim-card__meta">
                        <span
                          className="status-pill"
                          style={{
                            color: statusInfo.color,
                            backgroundColor: statusInfo.bg,
                            borderColor: statusInfo.color,
                          }}
                        >
                          {statusInfo.label}
                        </span>
                        <span className="quality-pill">
                          Quality: {claim.overall_evidence_quality}
                        </span>
                        <span className="claim-card__expand-icon">
                          {isExpanded ? "−" : "+"}
                        </span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="claim-card__details">
                        {claim.reasoning && (
                          <div className="claim-card__reasoning">
                            <strong>Verification Reason:</strong> {claim.reasoning}
                          </div>
                        )}

                        <div className="claim-card__sources">
                          <strong>Supporting References ({claimSources.length}):</strong>
                          {claimSources.length > 0 ? (
                            <div className="source-cards-list">
                              {claimSources.map((src) => (
                                <div key={src.source_id} className="source-mini-card">
                                  <div className="source-mini-card__main">
                                    <span className="source-mini-card__publisher">
                                      {src.publisher}
                                    </span>
                                    <h5 className="source-mini-card__title">
                                      {src.title}
                                    </h5>
                                  </div>
                                  {src.url && (
                                    <a
                                      href={src.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="source-mini-card__link"
                                    >
                                      View Source ↗
                                    </a>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="no-sources">
                              No explicit web source linked for this specific claim. Status reflects generalized clinical baseline.
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
