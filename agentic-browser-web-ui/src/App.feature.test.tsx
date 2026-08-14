import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../src/App";

describe("App", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it("shows empty state when messages are empty", () => {
    render(<App />);
    expect(screen.getByText("What's next?")).toBeTruthy();
  });

  it("loads settings into provider and timeout fields", async () => {
    const user = userEvent.setup();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: "openrouter",
        chatModel: "openai/gpt-4o-mini",
        ollamaTimeout: 60,
        openrouterTimeout: 45,
        openaiTimeout: 30,
        ollamaHost: "http://localhost:11434",
        openrouterKey: "sk-or",
        openaiKey: "sk-ai",
      }),
    });

    render(<App />);
    await user.click(screen.getByText("Settings"));
    const selects = await screen.findAllByRole("combobox");
    expect(selects[0].value).toBe("openrouter");
    expect(await screen.findByDisplayValue("openai/gpt-4o-mini")).toBeTruthy();
    expect(await screen.findByDisplayValue("60")).toBeTruthy();
  });

  it("saves settings via POST and shows confirmation", async () => {
    const user = userEvent.setup();
    (global.fetch as any).mockResolvedValue({ ok: true, json: async () => ({ ok: true }) });

    render(<App />);
    await user.click(screen.getByText("Settings"));
    const inputs = await screen.findAllByRole("textbox");
    await user.clear(inputs[0]);
    await user.type(inputs[0], "http://ollama.local");
    await user.click(screen.getByText("Save"));
    expect(await screen.findByText(/saved/i)).toBeTruthy();
  });
});
