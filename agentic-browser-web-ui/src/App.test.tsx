import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders AgenticBrowser heading", () => {
    render(<App />);
    expect(screen.getByText("AgenticBrowser")).toBeTruthy();
  });

  it("renders chat input", () => {
    render(<App />);
    expect(screen.getByPlaceholderText("Ask anything…")).toBeTruthy();
  });
});
