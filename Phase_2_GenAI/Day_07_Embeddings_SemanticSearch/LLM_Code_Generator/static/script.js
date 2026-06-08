/**
 * LLM Code Generator — script.js
 * Handles form submission, API calls, UI state, and copy-to-clipboard.
 */

"use strict";

// ── DOM refs ──────────────────────────────────────────────────────────────────
const languageSelect    = document.getElementById("language");
const taskTextarea      = document.getElementById("task");
const charCount         = document.getElementById("charCount");
const generateBtn       = document.getElementById("generateBtn");
const btnText           = generateBtn.querySelector(".btn-text");
const btnSpinner        = generateBtn.querySelector(".btn-spinner");
const copyBtn           = document.getElementById("copyBtn");
const codeContainer     = document.getElementById("codeContainer");
const errorContainer    = document.getElementById("errorContainer");
const errorMessage      = document.getElementById("errorMessage");
const statusBadge       = document.getElementById("statusBadge");
const tokenUsage        = document.getElementById("tokenUsage");
const promptTokensEl    = document.getElementById("promptTokens");
const completionTokensEl= document.getElementById("completionTokens");
const totalTokensEl     = document.getElementById("totalTokens");

// ── Character counter ─────────────────────────────────────────────────────────
taskTextarea.addEventListener("input", () => {
  charCount.textContent = taskTextarea.value.length;
});

// ── Main generate handler ─────────────────────────────────────────────────────
generateBtn.addEventListener("click", async () => {
  const language = languageSelect.value.trim();
  const task     = taskTextarea.value.trim();

  if (!task) {
    showError("Please enter a task description.");
    return;
  }

  setLoading(true);
  clearOutput();

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language, task }),
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      showError(data.error || "An unexpected error occurred.");
      setStatus("error", "Failed");
      return;
    }

    renderCode(data.code, data.language);
    renderTokens(data.token_usage);
    setStatus("success", "✓ Generated");

  } catch (err) {
    showError("Network error — could not reach the server. Please try again.");
    setStatus("error", "Error");
    console.error("Fetch error:", err);
  } finally {
    setLoading(false);
  }
});

// ── Copy to clipboard ─────────────────────────────────────────────────────────
copyBtn.addEventListener("click", () => {
  const codeEl = codeContainer.querySelector("code");
  if (!codeEl) return;

  navigator.clipboard.writeText(codeEl.innerText).then(() => {
    const original = copyBtn.textContent;
    copyBtn.textContent = "✅ Copied!";
    setTimeout(() => { copyBtn.textContent = original; }, 2000);
  }).catch(() => {
    // Fallback for browsers without clipboard API
    const range = document.createRange();
    range.selectNode(codeEl);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand("copy");
    window.getSelection().removeAllRanges();
  });
});

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Renders the generated code with syntax highlighting.
 * @param {string} code - Raw code string from the API.
 * @param {string} language - Language key for highlight.js.
 */
function renderCode(code, language) {
  const langMap = { javascript: "javascript", python: "python", sql: "sql" };
  const hlLang  = langMap[language] || "plaintext";

  const pre  = document.createElement("pre");
  const code_ = document.createElement("code");
  code_.className = `language-${hlLang}`;
  code_.textContent = code;
  pre.appendChild(code_);

  codeContainer.innerHTML = "";
  codeContainer.appendChild(pre);

  hljs.highlightElement(code_);

  copyBtn.classList.remove("hidden");
}

/**
 * Updates the token usage display.
 * @param {{ prompt_tokens: number, completion_tokens: number, total_tokens: number }} usage
 */
function renderTokens(usage) {
  promptTokensEl.textContent     = (usage.prompt_tokens     ?? 0).toLocaleString();
  completionTokensEl.textContent = (usage.completion_tokens ?? 0).toLocaleString();
  totalTokensEl.textContent      = (usage.total_tokens      ?? 0).toLocaleString();
  tokenUsage.classList.remove("hidden");
}

/**
 * Shows an error message in the error container.
 * @param {string} message - Error text to display.
 */
function showError(message) {
  errorMessage.textContent = `⚠️ ${message}`;
  errorContainer.classList.remove("hidden");
}

/**
 * Sets the status badge text and style.
 * @param {"success"|"error"} type
 * @param {string} text
 */
function setStatus(type, text) {
  statusBadge.textContent = text;
  statusBadge.className   = `status-badge ${type}`;
  statusBadge.classList.remove("hidden");
}

/**
 * Toggles the loading state on the generate button.
 * @param {boolean} loading
 */
function setLoading(loading) {
  generateBtn.disabled = loading;
  btnText.classList.toggle("hidden", loading);
  btnSpinner.classList.toggle("hidden", !loading);
}

/** Clears all output areas. */
function clearOutput() {
  codeContainer.innerHTML = "";
  errorContainer.classList.add("hidden");
  statusBadge.classList.add("hidden");
  tokenUsage.classList.add("hidden");
  copyBtn.classList.add("hidden");
  errorMessage.textContent = "";
}
