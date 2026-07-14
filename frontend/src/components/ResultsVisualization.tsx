import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { BarChart3 } from "lucide-react";
import { inferChartConfig } from "../utils/chartData";
import styles from "./ResultsVisualization.module.css";

const CHART_COLORS = ["#7c3aed", "#3b82f6", "#06b6d4", "#8b5cf6", "#2563eb", "#22d3ee"];

interface ResultsVisualizationProps {
  columns: string[];
  rows: unknown[][];
}

export function ResultsVisualization({ columns, rows }: ResultsVisualizationProps) {
  const config = inferChartConfig(columns, rows);

  return (
    <section className={styles.section} aria-label="Data visualization">
      <div className={styles.header}>
        <BarChart3 size={18} strokeWidth={2} />
        <h2 className={styles.title}>Visualization</h2>
      </div>

      {!config ? (
        <div className={styles.placeholder}>
          <div className={styles.placeholderIcon}>
            <BarChart3 size={32} strokeWidth={1.5} />
          </div>
          <p className={styles.placeholderTitle}>Chart preview</p>
          <p className={styles.placeholderText}>
            Visualizations appear automatically when results include numeric data.
          </p>
        </div>
      ) : (
        <div className={styles.chartWrap}>
          <ResponsiveContainer width="100%" height={280}>
            {config.type === "pie" ? (
              <PieChart>
                <Pie
                  data={config.data}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  innerRadius={45}
                  paddingAngle={2}
                >
                  {config.data.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid var(--color-border)",
                    background: "var(--color-bg-elevated)",
                  }}
                />
              </PieChart>
            ) : config.type === "line" ? (
              <LineChart data={config.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid var(--color-border)",
                    background: "var(--color-bg-elevated)",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#7c3aed"
                  strokeWidth={2.5}
                  dot={{ fill: "#7c3aed", r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            ) : (
              <BarChart data={config.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--color-text-muted)" }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid var(--color-border)",
                    background: "var(--color-bg-elevated)",
                  }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {config.data.map((_, index) => (
                    <Cell
                      key={`bar-${index}`}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            )}
          </ResponsiveContainer>
          <p className={styles.chartLabel}>
            {config.labelColumn} vs {config.valueColumn}
          </p>
        </div>
      )}
    </section>
  );
}
