import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import * as api from "./services/api";
import type { AskResponse } from "./types/api";

const mockResponse: AskResponse = {
  answer: "Zenith Consulting generated the highest revenue at 47,940.",
  table: {
    columns: ["name", "total_revenue"],
    rows: [
      ["Zenith Consulting", 47940],
      ["SecureNet Corp", 28764],
    ],
  },
  chart: {
    type: "bar",
    x_key: "name",
    y_key: "total_revenue",
    title: "Total Revenue by Name",
  },
  metadata: {
    row_count: 2,
    execution_time_ms: 42,
  },
  debug: {
    sql: "SELECT name, SUM(amount) AS total_revenue FROM payments GROUP BY name",
  },
};

function getAskButton() {
  return within(screen.getByRole("form", { name: "Question form" })).getByRole(
    "button",
    { name: "Ask" },
  );
}

describe("App", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("shows validation error for empty question", () => {
    render(<App />);

    fireEvent.submit(screen.getByRole("form", { name: "Question form" }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Please enter a question before asking.",
    );
  });

  it("shows loading state while submitting", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "askQuestion").mockImplementation(
      () =>
        new Promise((resolve) => {
          window.setTimeout(() => resolve(mockResponse), 100);
        }),
    );

    render(<App />);
    await user.type(
      screen.getByLabelText("Your question"),
      "Which companies have the highest revenue?",
    );
    await user.click(getAskButton());

    expect(
      within(screen.getByRole("form", { name: "Question form" })).getByRole(
        "button",
        { name: "Analyzing…" },
      ),
    ).toBeDisabled();
    expect(screen.getByText("Running analysis…")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(mockResponse.answer)).toBeInTheDocument();
    });
  });

  it("displays answer and dynamic table", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "askQuestion").mockResolvedValue(mockResponse);

    render(<App />);
    await user.type(screen.getByLabelText("Your question"), "Highest revenue?");
    await user.click(getAskButton());

    expect(await screen.findByText(mockResponse.answer)).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "name" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "total_revenue" })).toBeInTheDocument();
    expect(screen.getByText("Zenith Consulting")).toBeInTheDocument();
    expect(screen.getByText("47,940")).toBeInTheDocument();
    expect(screen.getByText("2 rows")).toBeInTheDocument();
    expect(screen.getByText("42 ms")).toBeInTheDocument();
    expect(screen.getByText("Total Revenue by Name")).toBeInTheDocument();
  });

  it("shows API error message", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "askQuestion").mockRejectedValue({
      message: "Unable to reach the backend.",
    });

    render(<App />);
    await user.type(screen.getByLabelText("Your question"), "Test question");
    await user.click(getAskButton());

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Unable to reach the backend.",
    );
  });

  it("opens the SQL section", async () => {
    const user = userEvent.setup();
    vi.spyOn(api, "askQuestion").mockResolvedValue(mockResponse);

    render(<App />);
    await user.type(screen.getByLabelText("Your question"), "Highest revenue?");
    await user.click(getAskButton());

    await screen.findByText(mockResponse.answer);

    expect(screen.queryByText(mockResponse.debug.sql)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Show generated SQL/i }));

    expect(screen.getByText(mockResponse.debug.sql)).toBeInTheDocument();
  });

  it("fills the input when an example question is clicked", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(
      screen.getByRole("button", {
        name: "Which companies have the highest revenue?",
      }),
    );

    expect(screen.getByLabelText("Your question")).toHaveValue(
      "Which companies have the highest revenue?",
    );
  });
});
