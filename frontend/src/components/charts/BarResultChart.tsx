import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartRow } from "../../utils/chartRows";
import { CHART_AXIS_TICK, CHART_COLORS, CHART_TOOLTIP_STYLE } from "./chartTheme";

interface BarResultChartProps {
  data: ChartRow[];
  xKey: string;
  yKey: string;
}

export function BarResultChart({ data, xKey, yKey }: BarResultChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
        <XAxis
          dataKey={xKey}
          tick={CHART_AXIS_TICK}
          tickLine={false}
          interval={0}
          angle={data.length > 6 ? -25 : 0}
          textAnchor={data.length > 6 ? "end" : "middle"}
          height={data.length > 6 ? 70 : 30}
        />
        <YAxis tick={CHART_AXIS_TICK} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
        <Bar dataKey={yKey} radius={[6, 6, 0, 0]}>
          {data.map((_, index) => (
            <Cell key={`bar-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
