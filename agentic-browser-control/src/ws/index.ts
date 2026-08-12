import { WebSocket, WebSocketServer } from "ws";
import { sessionStore } from "../auth/session.js";
import { forwardChat } from "../chat/forwarder.js";

export function wireWs(server: any) {
  const wss = new WebSocketServer({ server, path: "/control" });

  wss.on("connection", (ws: WebSocket) => {
    ws.on("message", async (data: Buffer) => {
      try {
        const msg = JSON.parse(data.toString());
        if (msg.type === "auth") {
          sessionStore.set(msg.sessionId, { authenticated: !!msg.token, ws });
          ws.send(JSON.stringify({ type: "auth_ok", sessionId: msg.sessionId }));
        } else if (msg.type === "chat") {
          const session = sessionStore.get(msg.sessionId);
          if (!session?.authenticated) {
            ws.send(JSON.stringify({ type: "error", message: "Unauthenticated" }));
            return;
          }
          try {
            const data = await forwardChat({
              sessionId: msg.sessionId,
              provider: msg.provider,
              model: msg.model,
              messages: msg.messages || [],
            });
            ws.send(JSON.stringify({ type: "chat_result", id: msg.id, data }));
          } catch (err: any) {
            ws.send(JSON.stringify({ type: "error", message: err?.message || "Backend error" }));
          }
        }
      } catch (err) {
        ws.send(JSON.stringify({ type: "error", message: (err as Error).message }));
      }
    });
  });

  return wss;
}
