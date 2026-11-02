import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { ModelDeliberationDetail } from "../types";

interface DeliberationViewProps {
  modelDetails?: Record<string, ModelDeliberationDetail> | null;
}

export const DeliberationView: React.FC<DeliberationViewProps> = ({
  modelDetails,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<"model_1" | "model_2">("model_1");

  if (!modelDetails) {
    return null;
  }

  const model1 = modelDetails.model_1;
  const model2 = modelDetails.model_2;

  const currentModel = activeTab === "model_1" ? model1 : model2;

  return (
    <div className="deliberation-accordion">
      <button
        className="deliberation-accordion__header"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="deliberation-accordion__title-group">
          <span className="deliberation-accordion__icon">⚖️</span>
          <h3>Internal Dual-Model Deliberation Details</h3>
          <span className="deliberation-accordion__sub">
            (Clinical Analyst vs Skeptical Analyst Debug Log)
          </span>
        </div>
        <span className={`deliberation-accordion__chevron ${isOpen ? "open" : ""}`}>
          ▼
        </span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="deliberation-accordion__content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="deliberation-tabs">
              <button
                className={`deliberation-tab ${
                  activeTab === "model_1" ? "active" : ""
                }`}
                onClick={() => setActiveTab("model_1")}
              >
                🔬 Model 1: Clinical Analyst ({model1?.model_id})
              </button>
              <button
                className={`deliberation-tab ${
                  activeTab === "model_2" ? "active" : ""
                }`}
                onClick={() => setActiveTab("model_2")}
              >
                🔍 Model 2: Skeptical Analyst ({model2?.model_id})
              </button>
            </div>

            {currentModel && (
              <div className="deliberation-panel">
                <div className="deliberation-block">
                  <h4>1. Initial Independent Analysis</h4>
                  <pre className="deliberation-text">
                    {currentModel.initial_analysis}
                  </pre>
                </div>

                <div className="deliberation-block">
                  <h4>2. Peer Critique Received</h4>
                  <pre className="deliberation-text">
                    {currentModel.critique_received || "No critique received."}
                  </pre>
                </div>

                <div className="deliberation-block">
                  <h4>
                    3. Revised Analysis{" "}
                    {currentModel.was_revised ? "(Revised)" : "(Unchanged)"}
                  </h4>
                  <pre className="deliberation-text">
                    {currentModel.revised_analysis || currentModel.initial_analysis}
                  </pre>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
