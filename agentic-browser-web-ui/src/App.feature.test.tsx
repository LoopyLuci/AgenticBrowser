import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
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

  it("sends a chat message and shows assistant reply", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ message: { content: "Hello from mocked backend" } }),
    } as any);
    render(<App />);
    const input = screen.getByPlaceholderText("Ask anything…");
    await userEvent.type(input, "hello{Enter}");
    await waitFor(() => expect(screen.getByText("Hello from mocked backend")).toBeDefined());
  });

  it("switches between chat and settings views", async () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /chat/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /settings/i })).toBeDefined();
  });

  it("shows offline banner when backend is unreachable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("fetch failed"));
    render(<App />);
    const input = screen.getByPlaceholderText("Ask anything…");
    await userEvent.type(input, "hello{Enter}");
    await waitFor(() => expect(screen.getByText(/Backend unreachable/i)).toBeDefined());
  });

  it("shows offline banner when backend returns an error status", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: false,
      status: 500,
    } as any);
    render(<App />);
    const input = screen.getByPlaceholderText("Ask anything…");
    await userEvent.type(input, "hello{Enter}");
    await waitFor(() => expect(screen.getByText(/Backend unreachable/i)).toBeDefined());
  });

  it("shows empty-state prompt when chat is empty", async () => {
    render(<App />);
    expect(screen.getByText("What's next?")).toBeDefined();
    expect(screen.getByText(/Connect a provider/i)).toBeDefined();
  });
});
