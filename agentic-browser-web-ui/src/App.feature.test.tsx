import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../src/App";

describe("App", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders empty state and switches to settings", async () => {
    const user = userEvent.setup();
    render(<App />);
    expect(screen.getByText("What's next?")).toBeTruthy();
    await user.click(screen.getByText("Settings"));
    expect(screen.getByText("Providers")).toBeTruthy();
  });

  it("loads settings into UI fields", async () => {
    const user = userEvent.setup();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: "openrouter",
        chatModel: "openai/gpt-4o-mini",
        ollamaHost: "http://localhost:11434",
        openrouterKey: "sk-or",
        openaiKey: "sk-ai",
        ollamaTimeout: 60,
        openrouterTimeout: 45,
        openaiTimeout: 30,
      }),
    });

    render(<App />);
    await user.click(screen.getByText("Settings"));
    const selects = await screen.findAllByRole("combobox");
    expect(selects[0].value).toBe("openrouter");
    expect(await screen.findByDisplayValue("openai/gpt-4o-mini")).toBeTruthy();
    expect(await screen.findByDisplayValue("60")).toBeTruthy();
  });

  it("saves settings and shows confirmation", async () => {
    const user = userEvent.setup();
    let lastPayload: unknown;
    global.fetch = vi.fn().mockImplementation(async (url, opts) => {
      if (typeof opts === "object" && opts && "body" in opts) {
        lastPayload = JSON.parse((opts.body as string) || "{}");
      }
      return { ok: true, json: async () => ({ ok: true }) } as Response;
    });

    render(<App />);
    await user.click(screen.getByText("Settings"));
    const inputs = await screen.findAllByRole("textbox");
    await user.clear(inputs[0]);
    await user.type(inputs[0], "http://ollama.local");
    await user.click(screen.getByText("Save"));
    expect(await screen.findByText(/saved/i)).toBeTruthy();
    expect((lastPayload as any).ollamaHost).toBe("http://ollama.local");
  });

  it("sends chat and shows assistant message", async () => {
    const user = userEvent.setup();
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          provider: "ollama",
          chatModel: "llama3",
          ollamaTimeout: 120,
          openrouterTimeout: 45,
          openaiTimeout: 30,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: { content: "hello from assistant" }, provider: "ollama", model: "llama3" }),
      });

    render(<App />);
    const input = screen.getByPlaceholderText("Ask anything…");
    await user.type(input, "hi");
    await user.click(screen.getByRole("button", { name: "" }));
    expect(await screen.findByText("hello from assistant")).toBeTruthy();
  });
});
