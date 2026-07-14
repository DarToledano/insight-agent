import type { ChartConfig, TableData } from "../types/api";

export interface ChartRow {
  [key: string]: string | number;
}

const MAX_CHART_ROWS = 40;

function isNumeric(value: unknown): value is number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return true;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed);
  }
  return false;
}

function toNumber(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function truncateLabel(value: unknown, maxLength = 24): string {
  const label = value === null || value === undefined ? "Unknown" : String(value);
  if (label.length <= maxLength) {
    return label;
  }
  return `${label.slice(0, maxLength - 1)}…`;
}

export function buildChartRows(
  table: TableData,
  chart: ChartConfig,
): ChartRow[] | null {
  if (chart.type === "none" || !chart.y_key) {
    return null;
  }

  const yIndex = table.columns.indexOf(chart.y_key);
  if (yIndex === -1) {
    return null;
  }

  if (chart.type === "kpi") {
    const firstRow = table.rows[0];
    if (!firstRow || !isNumeric(firstRow[yIndex])) {
      return null;
    }
    return [{ [chart.y_key]: toNumber(firstRow[yIndex]) }];
  }

  const xIndex = chart.x_key ? table.columns.indexOf(chart.x_key) : -1;
  if (xIndex === -1) {
    return null;
  }

  const rows = table.rows
    .slice(0, MAX_CHART_ROWS)
    .map((row, index) => {
      const xValue = truncateLabel(row[xIndex]);
      const yValue = toNumber(row[yIndex]);
      return {
        [chart.x_key]: xValue,
        [chart.y_key]: yValue,
        __index: index,
      };
    })
    .filter((row) => isNumeric(row[chart.y_key]));

  return rows.length > 0 ? rows : null;
}

export function getKpiValue(rows: ChartRow[] | null, yKey: string): number | null {
  if (!rows || rows.length === 0) {
    return null;
  }
  const value = rows[0][yKey];
  return typeof value === "number" ? value : null;
}
