import { describe, expect, it } from "vitest";
import type { ChartConfig } from "../types/api";
import { buildChartRows, getKpiValue } from "./chartRows";

describe("buildChartRows", () => {
  it("builds bar chart rows from table data", () => {
    const chart: ChartConfig = {
      type: "bar",
      x_key: "name",
      y_key: "total_revenue",
      title: "Total Revenue by Name",
    };

    const rows = buildChartRows(
      {
        columns: ["name", "total_revenue"],
        rows: [
          ["Zenith Consulting", 47940],
          ["SecureNet Corp", 28764],
        ],
      },
      chart,
    );

    expect(rows).toEqual([
      { name: "Zenith Consulting", total_revenue: 47940, __index: 0 },
      { name: "SecureNet Corp", total_revenue: 28764, __index: 1 },
    ]);
  });

  it("returns null when chart type is none", () => {
    const rows = buildChartRows(
      { columns: ["name"], rows: [["Zenith Consulting"]] },
      { type: "none", x_key: "", y_key: "", title: "" },
    );
    expect(rows).toBeNull();
  });

  it("builds kpi value rows", () => {
    const chart: ChartConfig = {
      type: "kpi",
      x_key: "",
      y_key: "total_revenue",
      title: "Total Revenue",
    };

    const rows = buildChartRows(
      { columns: ["total_revenue"], rows: [[125000]] },
      chart,
    );

    expect(getKpiValue(rows, "total_revenue")).toBe(125000);
  });
});
