import React, { useState } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Send, Sparkles, Settings } from "lucide-react";

type Role = "user" | "assistant";
type Mode = "chat" | "page-chat";
type View = "chat" | "settings";

interface Message {
  id: string;
  role: Role;
  content: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState("Ollama");
  const [model, setModel] = useState("llama3");
  const [isSending, setIsSending] = useState(false);
  const [mode, setMode] = useState<Mode>("chat");
  const [pageContext, setPageContext] = useState<string>("");
  const [pageTitle, setPageTitle] = useState<string>("");
  const [selection, setSelection] = useState<string>("");
  const [view, setView] = useState<View>("chat");
  const [ollamaHost, setOllamaHost] = useState("http://localhost:11434");
  const [openrouterKey, setOpenrouterKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [saveMsg, setSaveMsg] = useState("");
  const [streaming, setStreaming] = useState(false);

  const streamAbortRef = React.useRef<(() => void) | null>(null);

  const loadSettings = async () => {
    try {
      const result = await chrome.storage.local.get(["ollamaHost", "openrouterKey", "openaiKey"]);
      if (result.ollamaHost) setOllamaHost(result.ollamaHost);
      if (result.openrouterKey) setOpenrouterKey(result.openrouterKey);
      if (result.openaiKey) setOpenaiKey(result.openaiKey);
    } catch (err) {
      console.error("Failed to load settings", err);
    }
  };

  const saveSettings = async () => {
    try {
      await chrome.storage.local.set({ ollamaHost, openrouterKey, openaiKey });
      setSaveMsg("Saved");
      setTimeout(() => setSaveMsg(""), 1200);
    } catch (err) {
      setSaveMsg("Save failed");
    }
  };

  const loadPageContext = async () => {
    try {
      const [ctxRes, selRes] = await Promise.all([
        chrome.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
          const tab = tabs[0];
          if (!tab?.id) return Promise.resolve({ ok: false, context: null } as any);
          return chrome.tabs.sendMessage(tab.id, { type: "GET_PAGE_CONTEXT" }).catch(() => ({ ok: false, context: null }));
        }),
        chrome.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
          const tab = tabs[0];
          if (!tab?.id) return Promise.resolve({ ok: false, selection: "" } as any);
          return chrome.tabs.sendMessage(tab.id, { type: "GET_SELECTION" }).catch(() => ({ ok: false, selection: "" }));
        }),
      ]);
      const ctx = (ctxRes as any)?.context;
      if (ctx) {
        setPageTitle(ctx.title || "");
        setPageContext([`URL: ${ctx.url}`, `Title: ${ctx.title || ""}`, ctx.text].join("\n\n"));
      }
      const sel = (selRes as any)?.selection;
      setSelection(sel || "");
    } catch (err) {
      console.error("Failed to load page context", err);
    }
  };

  const onSend = async () => {
    const text = input.trim();
    if (!text) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setIsSending(true);

    const systemPrefix = mode === "page-chat" ? buildPagePrompt() : undefined;
    const outboundMessages = [...messages, userMsg].map(({ role, content }) => ({ role, content }));
    if (systemPrefix) {
      outboundMessages.unshift({ role: "system", content: systemPrefix });
    }

    try {
      const res = await chrome.runtime.sendMessage({
        type: "CHAT_STREAM_REQUEST",
        payload: {
          messages: outboundMessages,
          provider,
          model,
          sessionId: `sidepanel-${Date.now()}`,
        },
      });

      if (!res?.ok) {
        throw new Error(res?.error || "Stream request failed");
      }

      const assistantId = crypto.randomUUID();
      setMessages((m) => [...m, { id: assistantId, role: "assistant", content: "" }]);
      setStreaming(true);

      const listenerId = `sidepanel-${Date.now()}`;
      const registerPromise = new Promise<{ remove?: () => void }>((resolve) => {
        const attempts = [0, 50, 150];
        let index = 0;

        const tryRegister = () => {
          chrome.runtime.sendMessage(
            { type: "REGISTER_STREAM_LISTENER", payload: { requestId: res.requestId, listenerId } },
            (regRes: any) => {
              if (chrome.runtime.lastError || !regRes?.ok) {
                index++;
                if (index < attempts.length) {
                  setTimeout(tryRegister, attempts[index]);
                  return;
                }
                resolve({});
                return;
              }
              resolve(regRes);
            }
          );
        };

        tryRegister();
      });

      const { remove } = await registerPromise;

      await new Promise<void>((resolve) => {
        const handler = (_msg: any, sender: any) => {
          if (sender.id !== chrome.runtime.id) return false;
          if (_msg?.type !== "STREAM_TOKEN" || _msg?.requestId !== res.requestId) return false;
          const chunk = _msg.payload?.chunk;
          if (!chunk) return false;
          if (chunk === "__DONE__") {
            setStreaming(false);
            remove?.();
            resolve();
            return false;
          }
          setMessages((m) =>
            m.map((msg) =>
              msg.id === assistantId ? { ...msg, content: msg.content + chunk } : msg
            )
          );
          return false;
        };

        const listener = (...args: any[]) => handler(...args);
        chrome.runtime.onMessage.addListener(listener);
        streamAbortRef.current = () => {
          chrome.runtime.onMessage.removeListener(listener);
          remove?.();
          setStreaming(false);
          resolve();
        };
      });
    } catch (err) {
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: `Error: ${(err as Error).message}` }]);
      setStreaming(false);
    } finally {
      setIsSending(false);
    }
  };

  const buildPagePrompt = () => {
    const parts = ["You are AgenticBrowser page-chat mode. Use the provided page context to answer accurately."];
    if (pageTitle) parts.push(`Page title: ${pageTitle}`);
    if (selection) parts.push(`User selection: ${selection}`);
    if (pageContext) parts.push(`Page context:\n${pageContext}`);
    parts.push("If the answer is not in the context, say so and give a best-effort answer.");
    return parts.join("\n");
  };

  const switchMode = (next: Mode) => {
    setMode(next);
    if (next === "page-chat") loadPageContext();
  };

  const switchView = (next: View) => {
    setView(next);
    if (next === "settings") loadSettings();
  };

  return (
    <div className="h-screen w-[380px] flex flex-col">
      <header className="flex items-center justify-between px-4 py-3 border-b border-white/10 backdrop-blur-md bg-black/30">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-[#FF2FA7] to-[#A259FF] grid place-items-center shadow-[0_0_20px_rgba(162,89,255,0.35)]">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-wide">AgenticBrowser</div>
            <div className="text-[11px] text-white/60">{provider} · {model}</div>
          </div>
        </div>
        <div className="flex gap-1">
          <button
            onClick={() => switchView("chat")}
            className={`h-8 px-3 rounded-lg text-xs transition ${view === "chat" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
          >
            Chat
          </button>
          <button
            onClick={() => switchView("settings")}
            className={`h-8 px-3 rounded-lg text-xs transition ${view === "settings" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
          >
            <Settings className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {view === "chat" ? (
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="flex gap-1 px-4 py-2">
            <button
              onClick={() => switchMode("chat")}
              className={`h-8 px-3 rounded-lg text-xs transition ${mode === "chat" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
            >
              Chat
            </button>
            <button
              onClick={() => switchMode("page-chat")}
              className={`h-8 px-3 rounded-lg text-xs transition ${mode === "page-chat" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
            >
              Page Chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {mode === "page-chat" && (
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3 space-y-2">
                <div className="text-xs font-semibold">Page Context</div>
                <div className="text-[11px] text-white/70 truncate">{pageTitle || "No title"}</div>
                <div className="text-[11px] text-white/70 truncate">{selection ? `Selection: ${selection}` : "No selection"}</div>
                <button onClick={loadPageContext} className="h-8 px-3 rounded-xl bg-white/8 border border-white/10 text-xs hover:border-[#A259FF]">
                  Refresh context
                </button>
              </div>
            )}

            {messages.length === 0 && (
              <div className="h-full grid place-items-center text-center px-6">
                <div>
                  <div className="text-2xl font-bold bg-gradient-to-r from-[#FF2FA7] via-[#A259FF] to-[#39FF14] bg-clip-text text-transparent">What&apos;s next?</div>
                  <p className="mt-2 text-sm text-white/60">Switch to Page Chat to ask questions about the current page, or just start chatting.</p>
                </div>
              </div>
            )}
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`max-w-[92%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
                  m.role === "user" ? "ml-auto bg-gradient-to-br from-[#FF2FA7]/90 to-[#A259FF]/90" : "mr-auto bg-white/8 border border-white/10"
                }`}
              >
                <div className="whitespace-pre-wrap break-words">{m.content}</div>
              </motion.div>
            ))}
            {isSending && (
              <div className="mr-auto max-w-[92%] rounded-2xl px-3.5 py-2.5 text-sm bg-white/8 border border-white/10">
                <span className="inline-flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#39FF14] animate-bounce" />
                  <span className="h-1.5 w-1.5 rounded-full bg-[#FF2FA7] animate-bounce" style={{ animationDelay: "80ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-[#A259FF] animate-bounce" style={{ animationDelay: "160ms" }} />
                </span>
              </div>
            )}
          </div>

          <div className="p-3 border-t border-white/10 bg-black/25 backdrop-blur-md">
            <div className="flex gap-2">
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="h-10 rounded-xl bg-white/8 border border-white/10 px-3 text-xs outline-none focus:border-[#A259FF]"
              >
                <option>Ollama</option>
                <option>OpenRouter</option>
                <option>OpenCode</option>
                <option>OpenAI</option>
                <option>Gemini</option>
                <option>Claude</option>
              </select>
              <input
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="h-10 flex-1 rounded-xl bg-white/8 border border-white/10 px-3 text-xs outline-none focus:border-[#A259FF]"
                placeholder="Model"
              />
            </div>
            <div className="mt-2 flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onSend()}
                className="flex-1 h-10 rounded-xl bg-white/8 border border-white/10 px-3 text-sm outline-none focus:border-[#A259FF]"
                placeholder={mode === "page-chat" ? "Ask about this page…" : "Ask anything…"}
              />
              <button
                onClick={onSend}
                disabled={isSending}
                className="h-10 px-3 rounded-xl bg-gradient-to-r from-[#FF2FA7] to-[#A259FF] disabled:opacity-60 flex items-center gap-1 text-sm font-semibold"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
            <div className="text-sm font-semibold">Providers</div>
            <label className="block text-xs text-white/70">Ollama Host</label>
            <input
              value={ollamaHost}
              onChange={(e) => setOllamaHost(e.target.value)}
              className="h-10 w-full rounded-xl bg-white/8 border border-white/10 px-3 text-xs outline-none focus:border-[#A259FF]"
              placeholder="http://localhost:11434"
            />
            <label className="block text-xs text-white/70">OpenRouter Key</label>
            <input
              value={openrouterKey}
              onChange={(e) => setOpenrouterKey(e.target.value)}
              className="h-10 w-full rounded-xl bg-white/8 border border-white/10 px-3 text-xs outline-none focus:border-[#A259FF]"
              placeholder="sk-or-..."
              type="password"
            />
            <label className="block text-xs text-white/70">OpenAI Key</label>
            <input
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              className="h-10 w-full rounded-xl bg-white/8 border border-white/10 px-3 text-xs outline-none focus:border-[#A259FF]"
              placeholder="sk-..."
              type="password"
            />
            <div className="flex items-center gap-2">
              <button onClick={saveSettings} className="h-9 px-4 rounded-xl bg-gradient-to-r from-[#FF2FA7] to-[#A259FF] text-xs font-semibold">Save</button>
              <span className="text-[11px] text-white/70">{saveMsg}</span>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="text-sm font-semibold mb-2">Theme</div>
            <div className="text-xs text-white/60">AgenticBrowser uses a pink/purple/green retro punk theme.</div>
          </div>
        </div>
      )}
    </div>
  );
}
