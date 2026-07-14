import { Sparkles } from "lucide-react";
import styles from "./AnswerCard.module.css";

interface AnswerCardProps {
  answer: string;
}

export function AnswerCard({ answer }: AnswerCardProps) {
  return (
    <section className={styles.card} aria-label="Analysis answer">
      <div className={styles.header}>
        <div className={styles.badge}>
          <Sparkles size={16} strokeWidth={2.25} />
          <span>AI Insight</span>
        </div>
      </div>
      <p className={styles.text}>{answer}</p>
    </section>
  );
}
