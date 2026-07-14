import { Table2 } from "lucide-react";
import { formatCellValue } from "../utils/formatCell";
import styles from "./ResultsTable.module.css";

interface ResultsTableProps {
  columns: string[];
  rows: unknown[][];
}

export function ResultsTable({ columns, rows }: ResultsTableProps) {
  return (
    <section className={styles.section} aria-label="Query results">
      <div className={styles.header}>
        <Table2 size={18} strokeWidth={2} />
        <h2 className={styles.title}>Results</h2>
      </div>

      {rows.length === 0 ? (
        <p className={styles.empty}>No rows were returned for this question.</p>
      ) : (
        <div className={styles.scroll}>
          <table className={styles.table}>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {columns.map((_, colIndex) => (
                    <td key={`${rowIndex}-${colIndex}`}>
                      {formatCellValue(row[colIndex])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
