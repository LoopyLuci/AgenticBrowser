import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "./App";

function okResponse(body: any): Response {
  return {
    ok: true,
    status: 200,
    json: async () => body,
    text: async () => JSON.stringify(body),
  } as unknown as Response;
}

describe("App feature", () => {
  beforeEach(() => {
    vi.resetModules();
  });

  it("renders empty state when no messages", async () => {
    render(<App />);
    expect(await screen.findByText("What's next?")).toBeTruthy();
  });

  it("shows backend error when chat fetch fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("fetch failed"));
    render(<App />);
    await userEvent.click(screen.getByPlaceholderText("Ask anything…"));
    await userEvent.type(screen.getByPlaceholderText("Ask anything…"), "hello");
    await userEvent.keyboard("{Enter}");
    expect(await screen.findByText(/Error: fetch failed/)).toBeTruthy();
  });

  it("shows empty input guard when sending blank text", async () => {
    render(<App />);
    await userEvent.click(screen.getByPlaceholderText("Ask anything…"));
    await userEvent.keyboard("{Enter}");
    expect(await screen.findByText("What's next?")).toBeTruthy();
  });

  it("loads settings and shows them after navigation", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(okResponse({
      ollamaHost: "http://example",
      openrouterKey: "sk-abc",
      openaiKey: "sk-def",
      ollamaTimeout: 90,
    }));
    render(<App />);
    await userEvent.click(screen.getByText("Settings"));
    expect(await screen.findByDisplayValue("http://example")).toBeTruthy();
    expect(await screen.findByDisplayValue("90")).toBeTruthy();
  });

  it("saves timeout and shows saved message", async () => {
    let captured: any = null;
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input: any, init?: any) => {
      if (typeof input === "string" && input.includes("/v1/settings")) {
        captured = JSON.parse(init?.body || "{}");
        return okResponse({}) as Response;
      }
      return okResponse({}) as Response;
    });
    render(<App />);
    await userEvent.click(screen.getByText("Settings"));
    const timeoutInput = await screen.findByDisplayValue("120");
    await userEvent.clear(timeoutInput);
    await userEvent.type(timeoutInput, "30");
    await userEvent.click(screen.getByText("Save"));
    expect(screen.getByText("Saved")).toBeTruthy();
    expect(captured?.ollamaTimeout).toBe(30);
  });
});
