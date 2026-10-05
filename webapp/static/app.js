// ── State ──────────────────────────────────────────────────────
const state = {
  meta: null,
  settings: null,
  sending: false,
};

const el = (id) => document.getElementById(id);

// ── API helpers ────────────────────────────────────────────────
async function apiGet(path) {
  const r = await fetch(path);
  return r.json();
}
async function apiPost(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return r.json();
}

// ── Chat rendering ─────────────────────────────────────────────
const chatArea = el("chatArea");

function scrollToBottom() {
  chatArea.scrollTop = chatArea.scrollHeight;
}

function addUserBubble(text) {
  const row = document.createElement("div");
  row.className = "bubble-row user";
  row.innerHTML = `<div class="bubble user"></div>`;
  row.querySelector(".bubble").textContent = text;
  chatArea.appendChild(row);
  scrollToBottom();
}

function addAssistantText(text, isError) {
  const row = document.createElement("div");
  row.className = "bubble-row assistant";
  const bubble = document.createElement("div");
  bubble.className = "bubble assistant" + (isError ? " error" : "");
  const pre = document.createElement("pre");
  pre.textContent = text;
  bubble.appendChild(pre);
  row.appendChild(bubble);
  chatArea.appendChild(row);
  scrollToBottom();
  return bubble;
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "bubble-row assistant";
  row.innerHTML = `
    <div class="bubble assistant">
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>`;
  chatArea.appendChild(row);
  scrollToBottom();
  return row;
}

function addConfirmCard(toolInfo) {
  const row = document.createElement("div");
  row.className = "bubble-row assistant";

  const card = document.createElement("div");
  card.className = "confirm-card";

  const paramsText = JSON.stringify(toolInfo.params || {}, null, 2);

  card.innerHTML = `
    <div class="confirm-title">⚠️ Cần xác nhận hành động</div>
    <div class="confirm-tool">${escapeHtml(toolInfo.tool)}</div>
    <div class="confirm-message"></div>
    <pre class="confirm-params"></pre>
    <div class="confirm-actions">
      <button class="btn-neutral" data-action="cancel">Hủy</button>
      <button class="btn-danger" data-action="confirm">Xác nhận thực hiện</button>
    </div>
  `;
  card.querySelector(".confirm-message").textContent = toolInfo.message || "";
  card.querySelector(".confirm-params").textContent = paramsText;

  const cancelBtn = card.querySelector('[data-action="cancel"]');
  const confirmBtn = card.querySelector('[data-action="confirm"]');

  const resolve = async (didConfirm) => {
    cancelBtn.classList.add("btn-disabled");
    confirmBtn.classList.add("btn-disabled");

    if (!didConfirm) {
      const note = document.createElement("div");
      note.className = "confirm-resolved-note";
      note.textContent = "Đã hủy — không có gì bị thay đổi.";
      card.appendChild(note);
      return;
    }

    const note = document.createElement("div");
    note.className = "confirm-resolved-note";
    note.textContent = "Đang thực hiện…";
    card.appendChild(note);

    const result = await apiPost("/api/confirm", {
      tool: toolInfo.tool,
      params: toolInfo.params,
      message: toolInfo.message,
    });
    note.remove();
    addAssistantText(result.result ?? "", !result.success);
  };

  cancelBtn.addEventListener("click", () => resolve(false));
  confirmBtn.addEventListener("click", () => resolve(true));

  row.appendChild(card);
  chatArea.appendChild(row);
  scrollToBottom();
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

// ── Sending a message ───────────────────────────────────────────
const inputBox = el("inputBox");
const sendBtn = el("sendBtn");

async function sendMessage() {
  const text = inputBox.value.trim();
  if (!text || state.sending) return;

  state.sending = true;
  sendBtn.disabled = true;
  inputBox.value = "";
  autoGrow();

  addUserBubble(text);
  const typingRow = addTypingIndicator();

  try {
    const result = await apiPost("/api/chat", { message: text });
    typingRow.remove();

    if (result.need_confirm) {
      addConfirmCard({
        tool: result.tool,
        params: result.params,
        message: result.message,
      });
    } else {
      addAssistantText(result.result ?? "(không có phản hồi)", !result.success);
    }
  } catch (e) {
    typingRow.remove();
    addAssistantText(`❌ Lỗi kết nối tới server: ${e}`, true);
  } finally {
    state.sending = false;
    sendBtn.disabled = false;
    refreshStatus();
  }
}

sendBtn.addEventListener("click", sendMessage);
inputBox.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
function autoGrow() {
  inputBox.style.height = "auto";
  inputBox.style.height = Math.min(inputBox.scrollHeight, 140) + "px";
}
inputBox.addEventListener("input", autoGrow);

// ── Help button ─────────────────────────────────────────────────
el("helpBtn").addEventListener("click", async () => {
  const typingRow = addTypingIndicator();
  const result = await apiPost("/api/help", {});
  typingRow.remove();
  addAssistantText(result.result ?? "", !result.success);
});

// ── Status pill / not-ready banner ───────────────────────────────
async function refreshStatus() {
  try {
    const status = await apiGet("/api/status");
    el("statusLabel").textContent = status.label;
    const dot = el("statusDot");
    dot.classList.remove("ready", "not-ready");
    dot.classList.add(status.ready ? "ready" : "not-ready");

    const banner = el("notReadyBanner");
    if (!status.ready) {
      el("notReadyText").textContent = status.reason;
      banner.classList.remove("hidden");
    } else {
      banner.classList.add("hidden");
    }
  } catch (e) {
    el("statusLabel").textContent = "Không thể kết nối server";
  }
}

// ── Settings modal ────────────────────────────────────────────────
const overlay = el("settingsOverlay");

el("settingsBtn").addEventListener("click", openSettings);
el("closeSettingsBtn").addEventListener("click", closeSettings);
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeSettings();
});

async function openSettings() {
  overlay.classList.remove("hidden");
  if (!state.meta) state.meta = await apiGet("/api/meta");
  state.settings = await apiGet("/api/settings");
  populateSettingsForm();
}
function closeSettings() {
  overlay.classList.add("hidden");
}

// Tabs
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.querySelector(`.tab-panel[data-tab="${btn.dataset.tab}"]`).classList.add("active");
  });
});

function populateSettingsForm() {
  const s = state.settings;
  const meta = state.meta;

  // Mode radios
  document.querySelectorAll('input[name="mode"]').forEach((r) => {
    r.checked = r.value === s.mode;
    r.onchange = () => updateProviderFieldsVisibility(r.value);
  });
  updateProviderFieldsVisibility(s.mode);

  // Local tiers
  const tierBox = el("tierOptions");
  tierBox.innerHTML = "";
  const activeTier = s.local_tier || meta.recommended_tier;
  Object.entries(meta.local_tiers).forEach(([key, cfg]) => {
    const div = document.createElement("div");
    div.className = "tier-option" + (key === activeTier ? " selected" : "");
    div.dataset.tier = key;
    div.innerHTML = `<span>${cfg.label}</span><span class="tier-ram">RAM máy: ${meta.ram_gb} GB</span>`;
    div.addEventListener("click", () => {
      tierBox.querySelectorAll(".tier-option").forEach((o) => o.classList.remove("selected"));
      div.classList.add("selected");
    });
    tierBox.appendChild(div);
  });
  el("ramHint").textContent = `(máy bạn có ${meta.ram_gb} GB — gợi ý: ${meta.recommended_tier})`;

  // Cloud keys
  el("groqApiKey").value = s.groq_api_key || "";
  el("geminiApiKey").value = s.gemini_api_key || "";
  el("groqSignup").href = meta.signup_urls.groq;
  el("geminiSignup").href = meta.signup_urls.gemini;

  // Blacklist
  renderBlacklist(s.user_blacklist || []);

  // Theme
  document.querySelectorAll('input[name="theme"]').forEach((r) => {
    r.checked = r.value === (s.theme || "dark");
  });

  el("settingsSaveStatus").textContent = "";
}

function updateProviderFieldsVisibility(mode) {
  el("localFields").classList.toggle("visible", mode === "local");
  el("groqFields").classList.toggle("visible", mode === "groq");
  el("geminiFields").classList.toggle("visible", mode === "gemini");
}

// Blacklist management (edited only in memory until "Lưu thay đổi")
let workingBlacklist = [];
function renderBlacklist(list) {
  workingBlacklist = [...list];
  const ul = el("blacklistList");
  ul.innerHTML = "";
  workingBlacklist.forEach((path, idx) => {
    const li = document.createElement("li");
    li.innerHTML = `<span></span><button data-idx="${idx}">✕</button>`;
    li.querySelector("span").textContent = path;
    li.querySelector("button").addEventListener("click", () => {
      workingBlacklist.splice(idx, 1);
      renderBlacklist(workingBlacklist);
    });
    ul.appendChild(li);
  });
}
el("addBlacklistBtn").addEventListener("click", () => {
  const input = el("blacklistInput");
  const val = input.value.trim();
  if (!val) return;
  workingBlacklist.push(val);
  input.value = "";
  renderBlacklist(workingBlacklist);
});

// Save
el("saveSettingsBtn").addEventListener("click", async () => {
  const mode = document.querySelector('input[name="mode"]:checked')?.value || "local";
  const tierEl = document.querySelector(".tier-option.selected");
  const theme = document.querySelector('input[name="theme"]:checked')?.value || "dark";

  const payload = {
    mode,
    local_tier: tierEl ? tierEl.dataset.tier : undefined,
    groq_api_key: el("groqApiKey").value.trim(),
    gemini_api_key: el("geminiApiKey").value.trim(),
    user_blacklist: workingBlacklist,
    theme,
  };

  const res = await apiPost("/api/settings", payload);
  if (res.success) {
    state.settings = res.settings;
    el("settingsSaveStatus").textContent = "✓ Đã lưu";
    applyTheme(res.settings.theme);
    refreshStatus();
    setTimeout(() => (el("settingsSaveStatus").textContent = ""), 2500);
  } else {
    el("settingsSaveStatus").textContent = "❌ Lưu thất bại";
  }
});

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme === "light" ? "light" : "dark");
}

// ── Init ───────────────────────────────────────────────────────
(async function init() {
  try {
    const s = await apiGet("/api/settings");
    applyTheme(s.theme);
  } catch (e) {
    /* server chưa sẵn sàng, giữ theme mặc định */
  }
  refreshStatus();
  setInterval(refreshStatus, 15000);
  inputBox.focus();
})();
