import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { ChartRow } from "../../utils/chartRows";
import { CHART_TOOLTIP_STYLE, PIE_CHART_COLORS } from "./chartTheme";
import styles from "./PieResultChart.module.css";

interface PieResultChartProps {
  data: ChartRow[];
  xKey: string;
  yKey: string;
}

function formatValue(value: number): string {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);
}

export function PieResultChart({ data, xKey, yKey }: PieResultChartProps) {
  const total = data.reduce((sum, row) => sum + (Number(row[yKey]) || 0), 0);

  return (
    <div className={styles.wrap}>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            dataKey={yKey}
            nameKey={xKey}
            cx="50%"
            cy="50%"
            outerRadius={88}
            innerRadius={44}
            paddingAngle={0}
            minAngle={5}
            stroke="none"
          >
            {data.map((_, index) => (
              <Cell
                key={`pie-${index}`}
                fill={PIE_CHART_COLORS[index % PIE_CHART_COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={CHART_TOOLTIP_STYLE}
            formatter={(value: number, name: string) => [formatValue(value), name]}
          />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            iconSize={8}
            wrapperStyle={{
              fontSize: "12px",
              paddingTop: "8px",
              color: "var(--color-text-secondary)",
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      <ul className={styles.breakdown} aria-label="Chart categories">
        {data.map((row, index) => {
          const value = Number(row[yKey]) || 0;
          const label = String(row[xKey]);
          const percent = total > 0 ? ((value / total) * 100).toFixed(1) : "0.0";
          const color = PIE_CHART_COLORS[index % PIE_CHART_COLORS.length];

          return (
            <li key={`${label}-${index}`} className={styles.breakdownItem}>
              <span
                className={styles.swatch}
                style={{ background: color }}
                aria-hidden="true"
              />
              <span className={styles.breakdownLabel}>{label}</span>
              <span className={styles.breakdownValue}>
                {formatValue(value)} ({percent}%)
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
