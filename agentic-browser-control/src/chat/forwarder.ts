import axios from "axios";

const BACKEND = process.env.AGENTIC_BACKEND || "http://localhost:8123";

export async function forwardChat(payload: {
  sessionId: string;
  provider: string;
  model: string;
  messages: Array<Record<string, any>>;
}) {
  const resp = await axios.post(`${BACKEND}/v1/chat`, {
    session_id: payload.sessionId,
    messages: payload.messages,
    provider: payload.provider || "ollama",
    model: payload.model || "llama3",
  });
  return resp.data;
}
