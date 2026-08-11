import React, { useState } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Sparkles } from "lucide-react";

export default function App() {
  const [input, setInput] = useState("");
  const send = () => {
    if (!input.trim()) return;
    chrome.runtime.sendMessage({ type: "chat", text: input });
    setInput("");
  };
  return (
    <div className="w-80 p-3 bg-[#141420] text-gray-200">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="text-[#ff2fa7]" />
        <div className="font-bold text-sm">AgenticBrowser</div>
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          className="flex-1 rounded bg-[#0b0b12] border border-[#a259ff]/40 px-2 py-1 text-xs outline-none"
          placeholder="Quick chat..."
        />
        <button
          onClick={send}
          className="rounded bg-[#ff2fa7] px-2 py-1 text-xs font-semibold text-black"
        >
          Send
        </button>
      </div>
      <div className="mt-2 text-[10px] text-gray-400">Popup ready</div>
    </div>
  );
}
