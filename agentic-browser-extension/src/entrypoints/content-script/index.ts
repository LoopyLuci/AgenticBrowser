// AgenticBrowser content script: real DOM extraction + tool execution bridge
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "get_page") {
    const text = document.body ? document.body.innerText || document.body.textContent || "" : "";
    sendResponse({ ok: true, text: text.slice(0, 20000) });
    return true;
  }
  if (msg.type === "get_selection") {
    const text = window.getSelection()?.toString() || "";
    sendResponse({ ok: true, text });
    return true;
  }
  if (msg.type === "inject_bubble") {
    if (document.getElementById("agentic-browser-bubble")) {
      sendResponse({ ok: true });
      return true;
    }
    const bubble = document.createElement("div");
    bubble.id = "agentic-browser-bubble";
    bubble.style.cssText = "position:fixed;bottom:16px;right:16px;background:#141420;color:#eaeaea;padding:10px 12px;border:1px solid #a259ff;border-radius:12px;font-family:sans-serif;font-size:12px;z-index:2147483647;box-shadow:0 6px 20px rgba(0,0,0,0.4);";
    bubble.textContent = msg.payload || "AgenticBrowser";
    document.body.appendChild(bubble);
    sendResponse({ ok: true });
    return true;
  }
  return false;
});
