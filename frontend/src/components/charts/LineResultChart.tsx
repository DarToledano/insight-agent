import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartRow } from "../../utils/chartRows";
import { CHART_AXIS_TICK, CHART_TOOLTIP_STYLE } from "./chartTheme";

interface LineResultChartProps {
  data: ChartRow[];
  xKey: string;
  yKey: string;
}

export function LineResultChart({ data, xKey, yKey }: LineResultChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
        <XAxis dataKey={xKey} tick={CHART_AXIS_TICK} tickLine={false} />
        <YAxis tick={CHART_AXIS_TICK} tickLine={false} axisLine={false} />
        <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
        <Line
          type="monotone"
          dataKey={yKey}
          stroke="#7c3aed"
          strokeWidth={2.5}
          dot={{ fill: "#7c3aed", r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
