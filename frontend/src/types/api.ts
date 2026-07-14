export type ChartType = "bar" | "line" | "pie" | "kpi" | "none";

export interface ChartConfig {
  type: ChartType;
  x_key: string;
  y_key: string;
  title: string;
}

export interface AskRequest {
  question: string;
}

export interface TableData {
  columns: string[];
  rows: unknown[][];
}

export interface AskMetadata {
  row_count: number;
  execution_time_ms: number;
}

export interface AskDebug {
  sql: string;
}

export interface AskResponse {
  answer: string;
  table: TableData;
  chart: ChartConfig;
  metadata: AskMetadata;
  debug: AskDebug;
}

export interface ApiError {
  message: string;
  status?: number;
}
