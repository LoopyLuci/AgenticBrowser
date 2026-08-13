import { setupServer } from "msw/node";
import { http, HttpResponse } from "msw";

export const server = setupServer();

export const mockSettings = {
  ollamaHost: "http://localhost:11434",
  openrouterKey: "demo",
  openaiKey: "demo",
};

export const mockChatResponse = {
  provider: "ollama",
  model: "llama3",
  message: { content: "Hello from mocked backend" },
  session_id: "test-session",
};

server.use(
  http.post("http://localhost:8123/v1/settings", () => {
    return HttpResponse.json(mockSettings);
  }),
  http.post("http://localhost:8123/v1/chat", () => {
    return HttpResponse.json(mockChatResponse);
  }),
  http.get("http://localhost:8123/v1/settings", () => {
    return HttpResponse.json(mockSettings);
  })
);
