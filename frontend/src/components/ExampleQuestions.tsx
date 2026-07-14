import {
  Clock,
  DollarSign,
  Headphones,
  PieChart,
  type LucideIcon,
} from "lucide-react";
import styles from "./ExampleQuestions.module.css";

const EXAMPLES: { question: string; title: string; icon: LucideIcon }[] = [
  {
    question: "Which companies have the highest revenue?",
    title: "Top revenue companies",
    icon: DollarSign,
  },
  {
    question: "Show total revenue by subscription plan",
    title: "Revenue by plan",
    icon: PieChart,
  },
  {
    question: "Which companies have the most support tickets?",
    title: "Support ticket volume",
    icon: Headphones,
  },
  {
    question: "Which users have not logged in recently?",
    title: "Inactive users",
    icon: Clock,
  },
];

interface ExampleQuestionsProps {
  disabled?: boolean;
  onSelect: (question: string) => void;
}

export function ExampleQuestions({ disabled, onSelect }: ExampleQuestionsProps) {
  return (
    <section className={styles.section} aria-label="Example questions">
      <h2 className={styles.heading}>Try an example</h2>
      <div className={styles.grid}>
        {EXAMPLES.map(({ question, title, icon: Icon }) => (
          <button
            key={question}
            type="button"
            className={styles.card}
            onClick={() => onSelect(question)}
            disabled={disabled}
            aria-label={question}
          >
            <div className={styles.iconWrap}>
              <Icon size={22} strokeWidth={2} />
            </div>
            <div className={styles.text}>
              <span className={styles.title}>{title}</span>
              <span className={styles.question}>{question}</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
