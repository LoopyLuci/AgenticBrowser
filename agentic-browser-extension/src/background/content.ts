// AgenticBrowser content script: DOM extraction + page context
const STORAGE_KEY = "agentic-browser-context";

function getTextContent() {
  const clone = document.body ? document.body.cloneNode(true) : document.documentElement.cloneNode(true);
  const cleanup = clone.querySelectorAll("script, style, noscript, svg, nav, footer, header");
  cleanup.forEach((el) => el.remove());
  const text = (clone.innerText || "").replace(/\s+/g, " ").trim();
  return text.slice(0, 12000);
}

function getSelectionText() {
  const sel = window.getSelection();
  const text = sel ? sel.toString().trim() : "";
  return text;
}

function getPageContext() {
  return {
    url: location.href,
    title: document.title,
    text: getTextContent(),
    selection: getSelectionText(),
    timestamp: Date.now(),
  };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "GET_PAGE_CONTEXT") {
    try {
      const ctx = getPageContext();
      sendResponse({ ok: true, context: ctx });
    } catch (err) {
      sendResponse({ ok: false, error: (err as Error).message });
    }
    return true;
  }
  if (message?.type === "GET_SELECTION") {
    try {
      const text = getSelectionText();
      sendResponse({ ok: true, selection: text });
    } catch (err) {
      sendResponse({ ok: false, error: (err as Error).message });
    }
    return true;
  }
  sendResponse({ ok: false, error: "Unknown message type" });
  return true;
});

console.log("AgenticBrowser content script loaded");
