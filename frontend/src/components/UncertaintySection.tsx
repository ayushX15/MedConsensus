import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { UncertaintyItem } from "../types";

interface UncertaintySectionProps {
  uncertainties: UncertaintyItem[];
}

export const UncertaintySection: React.FC<UncertaintySectionProps> = ({
  uncertainties,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  if (!uncertainties || uncertainties.length === 0) {
    return null;
  }

  return (
    <div className="uncertainty-accordion">
      <button
        className="uncertainty-accordion__header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="uncertainty-accordion__title-group">
          <span className="uncertainty-accordion__icon">⚖️</span>
          <h3>Areas of Diagnostic Uncertainty</h3>
          <span className="uncertainty-accordion__count">
            {uncertainties.length} area{uncertainties.length !== 1 ? "s" : ""}
          </span>
        </div>
        <span
          className={`uncertainty-accordion__chevron ${isOpen ? "open" : ""}`}
        >
          ▼
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="uncertainty-accordion__content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="uncertainty-list">
              {uncertainties.map((item, idx) => {
                const isExpanded = expandedIdx === idx;
                return (
                  <div key={idx} className="uncertainty-card">
                    <div
                      className="uncertainty-card__header"
                      onClick={() =>
                        setExpandedIdx(isExpanded ? null : idx)
                      }
                    >
                      <h4 className="uncertainty-card__topic">{item.topic}</h4>
                      <span className="uncertainty-card__expand">
                        {isExpanded ? "−" : "+"}
                      </span>
                    </div>

                    <p className="uncertainty-card__description">
                      {item.description}
                    </p>

                    {isExpanded && (
                      <div className="uncertainty-card__details">
                        {item.competing_hypotheses.length > 0 && (
                          <div className="uncertainty-card__section">
                            <strong>Competing Possibilities:</strong>
                            <ul>
                              {item.competing_hypotheses.map((h, hIdx) => (
                                <li key={hIdx}>{h}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {item.distinguishing_factors.length > 0 && (
                          <div className="uncertainty-card__section">
                            <strong>
                              What Would Help Distinguish:
                            </strong>
                            <ul>
                              {item.distinguishing_factors.map((f, fIdx) => (
                                <li key={fIdx}>{f}</li>
                              ))}
                            </ul>
                          </div>
                        )}
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
