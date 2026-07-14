import type { AskResponse } from "../types/api";
import { AnswerCard } from "./AnswerCard";
import { QueryMetadata } from "./QueryMetadata";
import { ResultsTable } from "./ResultsTable";
import { ResultsVisualization } from "./ResultsVisualization";
import { SqlViewer } from "./SqlViewer";
import styles from "./ResultsPanel.module.css";

interface ResultsPanelProps {
  result: AskResponse;
}

export function ResultsPanel({ result }: ResultsPanelProps) {
  return (
    <div className={styles.panel}>
      <AnswerCard answer={result.answer} />

      <QueryMetadata
        rowCount={result.metadata.row_count}
        executionTimeMs={result.metadata.execution_time_ms}
      />

      <div className={styles.grid}>
        <ResultsTable columns={result.table.columns} rows={result.table.rows} />
        <ResultsVisualization
          columns={result.table.columns}
          rows={result.table.rows}
        />
      </div>

      <SqlViewer sql={result.debug.sql} />
    </div>
  );
}
