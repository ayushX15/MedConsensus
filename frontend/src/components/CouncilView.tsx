import React from "react";
import type { CouncilResponse } from "../types";
import { MedicalAssessment } from "./MedicalAssessment";
import { EvidenceSection } from "./EvidenceSection";
import { UncertaintySection } from "./UncertaintySection";
import { DeliberationView } from "./DeliberationView";

interface CouncilViewProps {
  result: CouncilResponse;
}

export const CouncilView: React.FC<CouncilViewProps> = ({ result }) => {
  return (
    <div className="council-view">
      <MedicalAssessment result={result} />
      <EvidenceSection claims={result.claims} sources={result.sources} />
      <UncertaintySection uncertainties={result.uncertainties} />
      <DeliberationView modelDetails={result.model_details} />
    </div>
  );
};
