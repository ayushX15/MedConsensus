import { useState, useCallback } from "react";

interface Props {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

export function PromptInput({ onSubmit, isLoading }: Props) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (prompt.trim() && !isLoading) {
        onSubmit(prompt.trim());
      }
    },
    [prompt, isLoading, onSubmit]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        if (prompt.trim() && !isLoading) {
          onSubmit(prompt.trim());
        }
      }
    },
    [prompt, isLoading, onSubmit]
  );

  return (
    <form onSubmit={handleSubmit} className="prompt-form">
      <div className="prompt-form__field">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your symptoms, lab results, or medical question..."
          rows={4}
          disabled={isLoading}
          className="prompt-form__textarea"
        />
        <div className="prompt-form__footer">
          <span className="prompt-form__hint">
            {isLoading ? "" : "Ctrl + Enter"}
          </span>
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="prompt-form__submit"
          >
            {isLoading ? (
              <>
                <span className="prompt-form__spinner" />
                Deliberating…
              </>
            ) : (
              <>
                Convene the Council
                <span className="prompt-form__arrow">→</span>
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
