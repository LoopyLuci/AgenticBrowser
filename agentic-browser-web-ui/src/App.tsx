import React, { useState } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Send, Sparkles, Settings } from "lucide-react";

type Role = "user" | "assistant";

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
  const [view, setView] = useState<"chat" | "settings">("chat");
  const [ollamaHost, setOllamaHost] = useState("http://localhost:11434");
  const [openrouterKey, setOpenrouterKey] = useState("");
  const [openaiKey, setOpenaiKey] = useState("");
  const [saveMsg, setSaveMsg] = useState("");

  const onSend = async () => {
    const text = input.trim();
    if (!text) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setIsSending(true);
    try {
      const res = await fetch("http://localhost:8123/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMsg].map(({ role, content }) => ({ role, content })),
          provider,
          model,
        }),
      });
      const data = await res.json();
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: JSON.stringify(data, null, 2) },
      ]);
    } catch (err) {
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: `Error: ${(err as Error).message}` }]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 backdrop-blur-md bg-black/30">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#FF2FA7] to-[#A259FF] grid place-items-center shadow-[0_0_25px_rgba(162,89,255,0.35)]">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="text-base font-semibold tracking-wide">AgenticBrowser</div>
            <div className="text-xs text-white/60">Next-gen agentic browser assistant</div>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setView("chat")}
            className={`h-9 px-3 rounded-xl text-xs transition ${view === "chat" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
          >
            Chat
          </button>
          <button
            onClick={() => setView("settings")}
            className={`h-9 px-3 rounded-xl text-xs transition flex items-center gap-1 ${view === "settings" ? "bg-white/10 text-white" : "text-white/60 hover:text-white"}`}
          >
            <Settings className="h-3.5 w-3.5" /> Settings
          </button>
        </div>
      </header>

      {view === "chat" ? (
        <main className="flex-1 overflow-y-auto px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-4">
            {messages.length === 0 && (
              <div className="h-[60vh] grid place-items-center text-center">
                <div>
                  <div className="text-4xl font-bold bg-gradient-to-r from-[#FF2FA7] via-[#A259FF] to-[#39FF14] bg-clip-text text-transparent">What&apos;s next?</div>
                  <p className="mt-3 text-sm text-white/60">Connect a provider, choose a model, and start your agentic session.</p>
                </div>
              </div>
            )}
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  m.role === "user" ? "ml-auto bg-gradient-to-br from-[#FF2FA7]/90 to-[#A259FF]/90" : "mr-auto bg-white/8 border border-white/10"
                }`}
              >
                <div className="whitespace-pre-wrap break-words">{m.content}</div>
              </motion.div>
            ))}
            {isSending && (
              <div className="mr-auto max-w-[85%] rounded-2xl px-4 py-3 text-sm bg-white/8 border border-white/10">
                <span className="inline-flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#39FF14] animate-bounce" />
                  <span className="h-1.5 w-1.5 rounded-full bg-[#FF2FA7] animate-bounce" style={{ animationDelay: "80ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-[#A259FF] animate-bounce" style={{ animationDelay: "160ms" }} />
                </span>
              </div>
            )}
          </div>
        </main>
      ) : (
        <main className="flex-1 overflow-y-auto px-6 py-4">
          <div className="max-w-3xl mx-auto space-y-4">
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
                <button
                  onClick={async () => {
                    await fetch("http://localhost:8123/v1/settings", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({ ollamaHost, openrouterKey, openaiKey }),
                    });
                    setSaveMsg("Saved");
                    setTimeout(() => setSaveMsg(""), 1200);
                  }}
                  className="h-9 px-4 rounded-xl bg-gradient-to-r from-[#FF2FA7] to-[#A259FF] text-xs font-semibold"
                >
                  Save
                </button>
                <span className="text-[11px] text-white/70">{saveMsg}</span>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-sm font-semibold mb-2">Theme</div>
              <div className="text-xs text-white/60">AgenticBrowser uses a pink/purple/green retro punk theme.</div>
            </div>
          </div>
        </main>
      )}

      <footer className="px-6 py-4 border-t border-white/10 bg-black/25 backdrop-blur-md">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onSend()}
            className="flex-1 h-12 rounded-2xl bg-white/8 border border-white/10 px-4 text-sm outline-none focus:border-[#A259FF]"
            placeholder="Ask anything…"
          />
          <button
            onClick={onSend}
            disabled={isSending}
            className="h-12 px-5 rounded-2xl bg-gradient-to-r from-[#FF2FA7] to-[#A259FF] disabled:opacity-60 flex items-center gap-2 text-sm font-semibold"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </footer>
    </div>
  );
}
