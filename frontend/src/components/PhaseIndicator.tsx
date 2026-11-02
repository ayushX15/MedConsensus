import React from "react";
import { motion } from "framer-motion";
import type { Phase } from "../types";

interface PhaseIndicatorProps {
  phase: Phase;
}

const PHASES = [
  { id: "safety_and_routing", label: "Safety & Router", icon: "🛡️" },
  { id: "information_extraction", label: "Extract Clinical Data", icon: "📋" },
  { id: "dual_model_analysis", label: "Parallel Analyst Generation", icon: "⚡" },
  { id: "evidence_retrieval", label: "Evidence & Search Retrieval", icon: "🔎" },
  { id: "peer_review", label: "Cross-Model Peer Critique", icon: "⚖️" },
  { id: "re_evaluation", label: "Re-Evaluation & Revision", icon: "🔄" },
  { id: "final_adjudication", label: "Model 3 Adjudication", icon: "🩺" },
  { id: "final_safety_gate", label: "Final Safety Gate Audit", icon: "✅" },
];

export const PhaseIndicator: React.FC<PhaseIndicatorProps> = ({ phase }) => {
  if (phase === "idle") return null;

  const currentIdx = PHASES.findIndex((p) => p.id === phase);

  return (
    <div className="phase-indicator-card">
      <div className="phase-indicator-card__header">
        <h4 className="phase-indicator-card__title">
          {phase === "done"
            ? "✨ Deliberation & Verification Complete"
            : phase === "error"
            ? "❌ Deliberation Encountered an Error"
            : "⏳ Evidence Pipeline Processing..."}
        </h4>
      </div>

      <div className="phase-indicator-steps">
        {PHASES.map((p, idx) => {
          let statusClass = "pending";
          if (phase === "done") {
            statusClass = "completed";
          } else if (currentIdx !== -1) {
            if (idx < currentIdx) statusClass = "completed";
            else if (idx === currentIdx) statusClass = "active";
          }

          return (
            <motion.div
              key={p.id}
              className={`phase-step phase-step--${statusClass}`}
              animate={{
                scale: statusClass === "active" ? 1.03 : 1,
              }}
              transition={{ duration: 0.2 }}
            >
              <span className="phase-step__icon">{p.icon}</span>
              <span className="phase-step__label">{p.label}</span>
              {statusClass === "completed" && (
                <span className="phase-step__check">✓</span>
              )}
              {statusClass === "active" && (
                <span className="phase-step__spinner" />
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
