import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { ModelDeliberationDetail } from "../types";

interface Props {
  response: ModelDeliberationDetail;
  index: number;
}

const accentColors = ["var(--accent)", "var(--accent-secondary)"];
const ease = [0.22, 1, 0.36, 1] as const;

export function ResponsePanel({ response, index }: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const accent = accentColors[index % 2];

  return (
    <div
      className="panel"
      style={{ "--panel-accent": accent } as React.CSSProperties}
    >
      <div className="panel__accent-line" />

      <div className="panel__header">
        <h3 className="panel__model-name">{response.model_name}</h3>
        {response.was_revised ? (
          <span className="panel__badge panel__badge--revised">Revised</span>
        ) : (
          <span className="panel__badge panel__badge--unchanged">Unchanged</span>
        )}
      </div>

      <div className="panel__section">
        <h4 className="panel__section-title">Final Analysis</h4>
        <div className="panel__content">{response.revised_analysis || response.initial_analysis}</div>
      </div>

      <button
        className="panel__toggle"
        onClick={() => setShowDetails(!showDetails)}
        aria-expanded={showDetails}
      >
        {showDetails ? "Hide" : "View"} deliberation process
      </button>

      <AnimatePresence>
        {showDetails && (
          <motion.div
            className="panel__details"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease }}
            style={{ overflow: "hidden" }}
          >
            <div className="panel__details-inner">
              <div className="panel__detail-block">
                <h4 className="panel__section-title">Initial Analysis</h4>
                <div className="panel__content">
                  {response.initial_analysis}
                </div>
              </div>
              <div className="panel__detail-block">
                <h4 className="panel__section-title">Critique Received</h4>
                <div className="panel__content">
                  {response.critique_received}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
