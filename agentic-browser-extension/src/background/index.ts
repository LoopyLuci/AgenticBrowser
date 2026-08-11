const API_BASE = "http://localhost:8123";
const CONTROL_BASE = "http://localhost:8766";

type StreamListener = (chunk: string) => void;

const streamListeners: Map<string, Set<StreamListener>> = new Map();

function notifyStreamListeners(requestId: string, chunk: string) {
  const listeners = streamListeners.get(requestId);
  if (listeners) {
    listeners.forEach((fn) => {
      try {
        fn(chunk);
      } catch {}
    });
  }

  try {
    chrome.runtime.sendMessage({ type: "STREAM_TOKEN", requestId, payload: { chunk } });
  } catch {}
}

function addStreamListener(requestId: string, listener: StreamListener) {
  if (!streamListeners.has(requestId)) {
    streamListeners.set(requestId, new Set());
  }
  streamListeners.get(requestId)!.add(listener);
  return () => {
    const set = streamListeners.get(requestId);
    if (set) {
      set.delete(listener);
      if (set.size === 0) {
        streamListeners.delete(requestId);
      }
    }
  };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "CHAT_REQUEST") {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/v1/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: message.payload.messages,
            provider: message.payload.provider,
            model: message.payload.model,
            stream: !!message.payload.stream,
          }),
        });
        const data = await res.json();
        sendResponse({ ok: true, data });
      } catch (err) {
        sendResponse({ ok: false, error: (err as Error).message });
      }
    })();
    return true;
  }

  if (message?.type === "CHAT_STREAM_REQUEST") {
    (async () => {
      try {
        const requestId = `${message.payload.sessionId || "default"}-${Date.now()}`;
        const res = await fetch(`${API_BASE}/v1/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: message.payload.messages,
            provider: message.payload.provider,
            model: message.payload.model,
            session_id: message.payload.sessionId,
          }),
        });

        if (!res.ok || !res.body) {
          const text = await res.text();
          sendResponse({ ok: false, error: text || `HTTP ${res.status}` });
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let done = false;
        let aborted = false;

        const cleanup = addStreamListener(requestId, () => {
          aborted = true;
        });

        while (!done && !aborted) {
          const { value, done: readerDone } = await reader.read();
          if (readerDone) {
            done = true;
            break;
          }
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";
          for (const part of parts) {
            const trimmed = part.trim();
            if (!trimmed || !trimmed.startsWith("data:")) continue;
            const payload = trimmed.slice(5).trim();
            if (payload === "[DONE]") {
              done = true;
              break;
            }
            notifyStreamListeners(requestId, payload);
          }
        }

        cleanup();
        notifyStreamListeners(requestId, "__DONE__");
        sendResponse({ ok: true, requestId });
      } catch (err) {
        sendResponse({ ok: false, error: (err as Error).message });
      }
    })();
    return true;
  }

  if (message?.type === "REGISTER_STREAM_LISTENER") {
    const requestId = message.payload?.requestId;
    const listenerId = message.payload?.listenerId;
    if (!requestId || !listenerId) {
      sendResponse({ ok: false, error: "missing requestId/listenerId" });
      return;
    }
    const listeners = new Map<string, (chunk: string) => void>();
    const remove = addStreamListener(requestId, (chunk) => {
      listeners.forEach((fn) => {
        try {
          fn(chunk);
        } catch {}
      });
    });
    listeners.set(listenerId, (chunk) => {});
    sendResponse({ ok: true, remove });
    return;
  }

  if (message?.type === "CONTROL_REQUEST") {
    (async () => {
      try {
        const res = await fetch(`${CONTROL_BASE}/v1/control/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(message.payload),
        });
        const data = await res.json();
        sendResponse({ ok: true, data });
      } catch (err) {
        sendResponse({ ok: false, error: (err as Error).message });
      }
    })();
    return true;
  }
  if (message?.type === "TOOL_REQUEST") {
    (async () => {
      try {
        const context = await collectPageContext();
        const res = await fetch(`${API_BASE}/v1/tools`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: message.payload.name,
            arguments: message.payload.arguments || {},
            confirm: !!message.payload.confirm,
            context,
          }),
        });
        const data = await res.json();
        sendResponse({ ok: true, data });
      } catch (err) {
        sendResponse({ ok: false, error: (err as Error).message });
      }
    })();
    return true;
  }
  sendResponse({ ok: false, error: "Unknown message type" });
  return true;
});

async function collectPageContext() {
  try {
    const [tabResult, pageResult, selectionResult] = await Promise.all([
      chrome.tabs.query({ active: true, currentWindow: true }),
      chrome.tabs.sendMessage((await chrome.tabs.query({ active: true, currentWindow: true }))[0].id, { type: "get_page" }),
      chrome.tabs.sendMessage((await chrome.tabs.query({ active: true, currentWindow: true }))[0].id, { type: "get_selection" }),
    ]);
    const tab = tabResult[0];
    const page = pageResult || {};
    const selection = selectionResult || {};
    return {
      title: tab?.title,
      url: tab?.url,
      pageText: page.text,
      selection: selection.text,
    };
  } catch (err) {
    return {};
  }
}

export { addStreamListener, notifyStreamListeners };
