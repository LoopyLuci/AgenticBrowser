import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App feature flow", () => {
  it("submits settings and shows save feedback", async () => {
    render(<App />);
    await userEvent.click(screen.getByRole("button", { name: /settings/i }));
    const ollamaInput = screen.getByPlaceholderText("http://localhost:11434");
    await userEvent.clear(ollamaInput);
    await userEvent.type(ollamaInput, "http://localhost:9999/ollama");
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => expect(screen.getByText("Saved")).toBeDefined());
  });

  it("sends a chat message", async () => {
    render(<App />);
    const input = screen.getByPlaceholderText("Ask anything…");
    await userEvent.type(input, "hello{Enter}");
    expect(screen.getByText("hello")).toBeDefined();
  });

  it("switches between chat and settings views", async () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /chat/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /settings/i })).toBeDefined();
  });
});
