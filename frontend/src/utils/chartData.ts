export type ChartType = "bar" | "line" | "pie" | "none";

export interface ChartPoint {
  name: string;
  value: number;
}

export interface ChartConfig {
  type: ChartType;
  data: ChartPoint[];
  labelColumn: string;
  valueColumn: string;
}

function isNumeric(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function formatLabel(value: unknown): string {
  if (value === null || value === undefined) {
    return "Unknown";
  }
  return String(value);
}

export function inferChartConfig(
  columns: string[],
  rows: unknown[][],
): ChartConfig | null {
  if (rows.length === 0 || columns.length < 2) {
    return null;
  }

  const numericColIndex = columns.findIndex((_, colIndex) =>
    rows.every((row) => isNumeric(row[colIndex]) || row[colIndex] === null),
  );

  if (numericColIndex === -1) {
    return null;
  }

  const labelColIndex = numericColIndex === 0 ? 1 : 0;
  const data: ChartPoint[] = rows
    .slice(0, 12)
    .map((row) => ({
      name: formatLabel(row[labelColIndex]),
      value: isNumeric(row[numericColIndex]) ? row[numericColIndex] : 0,
    }))
    .filter((point) => point.name !== "Unknown" || point.value !== 0);

  if (data.length === 0) {
    return null;
  }

  const type: ChartType =
    data.length <= 5 ? "pie" : rows.length > 6 ? "line" : "bar";

  return {
    type,
    data,
    labelColumn: columns[labelColIndex] ?? "category",
    valueColumn: columns[numericColIndex] ?? "value",
  };
}
