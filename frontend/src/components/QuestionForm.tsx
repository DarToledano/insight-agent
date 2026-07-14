import type { FormEvent } from "react";
import { ArrowUp, Loader2 } from "lucide-react";
import styles from "./QuestionForm.module.css";

interface QuestionFormProps {
  question: string;
  loading: boolean;
  onQuestionChange: (value: string) => void;
  onSubmit: () => void;
}

export function QuestionForm({
  question,
  loading,
  onQuestionChange,
  onSubmit,
}: QuestionFormProps) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!loading) {
      onSubmit();
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!loading && question.trim()) {
        onSubmit();
      }
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} aria-label="Question form">
      <label htmlFor="question-input" className={styles.srOnly}>
        Your question
      </label>
      <div className={`${styles.promptBox} ${loading ? styles.loading : ""}`}>
        <textarea
          id="question-input"
          className={styles.input}
          rows={3}
          placeholder="Ask anything about your business data…"
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <div className={styles.footer}>
          {loading ? (
            <span className={styles.status} role="status" aria-live="polite">
              <Loader2 size={16} className={styles.spinner} aria-hidden="true" />
              Running analysis…
            </span>
          ) : (
            <span className={styles.hint}>Press Enter to send · Shift+Enter for new line</span>
          )}
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={loading || !question.trim()}
            aria-label={loading ? "Analyzing…" : "Ask"}
          >
            {loading ? (
              <>
                <Loader2 size={20} className={styles.spinner} />
                Analyzing…
              </>
            ) : (
              <>
                Ask
                <ArrowUp size={20} strokeWidth={2.5} />
              </>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
