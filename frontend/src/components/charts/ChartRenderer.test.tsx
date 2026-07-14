import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChartRenderer } from "./ChartRenderer";

describe("ChartRenderer", () => {
  it("renders a bar chart from backend chart config", () => {
    render(
      <ChartRenderer
        chart={{
          type: "bar",
          x_key: "name",
          y_key: "total_revenue",
          title: "Total Revenue by Name",
        }}
        table={{
          columns: ["name", "total_revenue"],
          rows: [
            ["Zenith Consulting", 47940],
            ["SecureNet Corp", 28764],
          ],
        }}
      />,
    );

    expect(screen.getByText("Total Revenue by Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Data visualization")).toBeInTheDocument();
  });

  it("shows placeholder when chart type is none", () => {
    render(
      <ChartRenderer
        chart={{ type: "none", x_key: "", y_key: "", title: "" }}
        table={{ columns: ["name"], rows: [["Zenith Consulting"]] }}
      />,
    );

    expect(screen.getByText("No chart for this result")).toBeInTheDocument();
  });

  it("renders a KPI card for single-value results", () => {
    render(
      <ChartRenderer
        chart={{
          type: "kpi",
          x_key: "",
          y_key: "total_revenue",
          title: "Total Revenue",
        }}
        table={{
          columns: ["total_revenue"],
          rows: [[125000]],
        }}
      />,
    );

    expect(screen.getByLabelText("Total Revenue KPI")).toBeInTheDocument();
    expect(screen.getByText("125,000")).toBeInTheDocument();
  });

  it("lists all pie chart categories including small values", () => {
    render(
      <ChartRenderer
        chart={{
          type: "pie",
          x_key: "subscription_plan",
          y_key: "total_revenue",
          title: "Total Revenue by Subscription Plan",
        }}
        table={{
          columns: ["subscription_plan", "total_revenue"],
          rows: [
            ["enterprise", 131036],
            ["pro", 4776],
            ["starter", 196],
          ],
        }}
      />,
    );

    expect(screen.getByText("enterprise")).toBeInTheDocument();
    expect(screen.getByText("pro")).toBeInTheDocument();
    expect(screen.getByText("starter")).toBeInTheDocument();
    expect(screen.getByText(/196/)).toBeInTheDocument();
  });
});
