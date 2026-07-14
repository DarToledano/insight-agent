import { Clock, Cpu, Rows3 } from "lucide-react";
import styles from "./QueryMetadata.module.css";

interface QueryMetadataProps {
  rowCount: number;
  executionTimeMs: number;
  modelName?: string;
}

export function QueryMetadata({
  rowCount,
  executionTimeMs,
  modelName = "GPT-4.1-mini",
}: QueryMetadataProps) {
  return (
    <section className={styles.section} aria-label="Query metadata">
      <span className={styles.badge}>
        <Rows3 size={14} aria-hidden="true" />
        {rowCount.toLocaleString()} row{rowCount === 1 ? "" : "s"}
      </span>
      <span className={styles.badge}>
        <Clock size={14} aria-hidden="true" />
        {executionTimeMs.toLocaleString()} ms
      </span>
      <span className={styles.badge}>
        <Cpu size={14} aria-hidden="true" />
        {modelName}
      </span>
    </section>
  );
}
