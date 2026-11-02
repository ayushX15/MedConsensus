import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { runCouncil } from "./api/council";
import type { CouncilResponse, Phase } from "./types";
import { PromptInput } from "./components/PromptInput";
import { PhaseIndicator } from "./components/PhaseIndicator";
import { CouncilView } from "./components/CouncilView";
import "./App.css";

const ease = [0.22, 1, 0.36, 1] as const;

function App() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [result, setResult] = useState<CouncilResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isLoading = phase !== "idle" && phase !== "done" && phase !== "error";

  const handleSubmit = async (prompt: string) => {
    setPhase("safety_and_routing");
    setResult(null);
    setError(null);

    // Timed progression matched to accelerated hybrid deliberation pipeline
    const t1 = setTimeout(() => setPhase("information_extraction"), 1200);
    const t2 = setTimeout(() => setPhase("dual_model_analysis"), 2800);
    const t3 = setTimeout(() => setPhase("evidence_retrieval"), 5000);
    const t4 = setTimeout(() => setPhase("peer_review"), 7500);
    const t5 = setTimeout(() => setPhase("re_evaluation"), 9500);
    const t6 = setTimeout(() => setPhase("final_adjudication"), 11200);
    const t7 = setTimeout(() => setPhase("final_safety_gate"), 12800);

    try {
      const response = await runCouncil(prompt);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(t6);
      clearTimeout(t7);

      setResult(response);
      setPhase("done");
    } catch (err) {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
      clearTimeout(t6);
      clearTimeout(t7);

      setError(err instanceof Error ? err.message : "Unknown error");
      setPhase("error");
    }
  };

  return (
    <div className="app">
      <div className="app__glow" />

      <motion.header
        className="header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease }}
      >
        <div className="header__ornament">🩺</div>
        <h1 className="header__title">Consilium</h1>
        <p className="header__subtitle">
          Evidence-Grounded AI Medical Decision Support Architecture
        </p>
        <div className="header__line" />
      </motion.header>

      <motion.main
        className="main"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2, ease }}
      >
        <PromptInput onSubmit={handleSubmit} isLoading={isLoading} />
        <PhaseIndicator phase={phase} />

        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              key="error"
              className="error-banner"
              initial={{ opacity: 0, y: 12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -12, scale: 0.98 }}
              transition={{ duration: 0.3 }}
            >
              <span className="error-banner__icon">✕</span>
              <span>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
            >
              <CouncilView result={result} />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.main>
    </div>
  );
}

export default App;
