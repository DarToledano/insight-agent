import { BarChart3 } from "lucide-react";
import type { ChartConfig, TableData } from "../../types/api";
import { buildChartRows, getKpiValue } from "../../utils/chartRows";
import { BarResultChart } from "./BarResultChart";
import { KpiCard } from "./KpiCard";
import { LineResultChart } from "./LineResultChart";
import { PieResultChart } from "./PieResultChart";
import styles from "./ChartRenderer.module.css";

interface ChartRendererProps {
  chart: ChartConfig;
  table: TableData;
}

export function ChartRenderer({ chart, table }: ChartRendererProps) {
  const data = buildChartRows(table, chart);
  const hasChart = chart.type !== "none" && data !== null;

  return (
    <section className={styles.section} aria-label="Data visualization">
      <div className={styles.header}>
        <BarChart3 size={18} strokeWidth={2} />
        <h2 className={styles.title}>{hasChart ? chart.title : "Visualization"}</h2>
      </div>

      {!hasChart ? (
        <div className={styles.placeholder}>
          <div className={styles.placeholderIcon}>
            <BarChart3 size={32} strokeWidth={1.5} />
          </div>
          <p className={styles.placeholderTitle}>No chart for this result</p>
          <p className={styles.placeholderText}>
            The table view is the best way to explore this data set.
          </p>
        </div>
      ) : chart.type === "kpi" ? (
        <KpiCard
          title={chart.title}
          value={getKpiValue(data, chart.y_key) ?? 0}
          valueKey={chart.y_key}
        />
      ) : (
        <div className={styles.chartWrap}>
          {chart.type === "bar" && (
            <BarResultChart data={data} xKey={chart.x_key} yKey={chart.y_key} />
          )}
          {chart.type === "line" && (
            <LineResultChart data={data} xKey={chart.x_key} yKey={chart.y_key} />
          )}
          {chart.type === "pie" && (
            <PieResultChart data={data} xKey={chart.x_key} yKey={chart.y_key} />
          )}
        </div>
      )}
    </section>
  );
}
