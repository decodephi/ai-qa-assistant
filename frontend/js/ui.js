// frontend/js/ui.js
// DOM rendering helpers — pure functions that build HTML and update the DOM.

/** Format time as HH:MM */
function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/** Escape HTML to prevent XSS */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/** Auto-grow textarea */
export function autoGrow(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 140) + 'px';
}

/** Scroll chat to the bottom */
export function scrollToBottom(container) {
  requestAnimationFrame(() => {
    container.scrollTop = container.scrollHeight;
  });
}

/** Render a user message bubble */
export function renderUserMessage(container, text) {
  const html = `
    <div class="message user" id="msg-${Date.now()}">
      <div class="avatar user-avatar">🙋</div>
      <div class="bubble-wrapper">
        <div class="bubble user-bubble">${escapeHtml(text)}</div>
        <div class="message-time">${formatTime()}</div>
      </div>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
  scrollToBottom(container);
}

/** Render the typing indicator; returns the element so it can be removed */
export function renderTypingIndicator(container) {
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typing-indicator';
  el.innerHTML = `
    <div class="avatar bot-avatar">🤖</div>
    <div class="typing-dots">
      <span></span><span></span><span></span>
    </div>
    <span class="typing-label">Searching & thinking…</span>
  `;
  container.appendChild(el);
  scrollToBottom(container);
  return el;
}

/** Remove the typing indicator */
export function removeTypingIndicator() {
  document.getElementById('typing-indicator')?.remove();
}

/** Render a bot response with key points and sources */
export function renderBotMessage(container, { answer, key_points = [], sources = [], backend = '' }) {
  // Key points section
  let kpHtml = '';
  if (key_points.length > 0) {
    const items = key_points
      .map(kp => `<li>${escapeHtml(kp)}</li>`)
      .join('');
    kpHtml = `
      <div class="key-points">
        <div class="kp-label">📌 Key Points</div>
        <ul class="kp-list">${items}</ul>
      </div>
    `;
  }

  // Sources section
  let srcHtml = '';
  if (sources.length > 0) {
    const cards = sources
      .filter(s => s.url)
      .map(s => `
        <a href="${s.url}" target="_blank" rel="noopener noreferrer" class="source-card">
          <span class="source-icon">↗</span>
          <span class="source-title">${escapeHtml(s.title || s.url)}</span>
        </a>
      `).join('');
    srcHtml = `
      <div class="sources">
        <div class="sources-label">🔗 Sources</div>
        ${cards}
      </div>
    `;
  }

  // Backend badge (subtle)
  const backendNote = backend
    ? `<div class="message-time" style="margin-top:8px">via ${escapeHtml(backend)}</div>`
    : '';

  const html = `
    <div class="message bot" id="msg-${Date.now()}">
      <div class="avatar bot-avatar">🤖</div>
      <div class="bubble-wrapper">
        <div class="bubble bot-bubble">${formatAnswer(answer)}</div>
        ${kpHtml}
        ${srcHtml}
        ${backendNote}
        <div class="message-time">${formatTime()}</div>
      </div>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);
  scrollToBottom(container);
}

/** Convert newlines to <br> and handle basic markdown-like bold */
function formatAnswer(text) {
  if (!text) return 'No answer generated.';
  return escapeHtml(text)
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code style="font-family:monospace;background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:4px">$1</code>');
}

/** Update the backend label in the header */
export function updateBackendBadge(backend) {
  const badge = document.getElementById('backend-label');
  if (badge && backend) badge.textContent = backend;
}

/** Update the sidebar history panel */
export function renderSidebarHistory(history) {
  const container = document.getElementById('sidebar-history');
  const countEl   = document.getElementById('history-count');
  if (!container) return;

  if (!history || history.length === 0) {
    container.innerHTML = `<div style="color:var(--text-muted);font-size:0.8rem;padding:8px">No history yet.</div>`;
    if (countEl) countEl.textContent = '0 turns';
    return;
  }

  const turns = Math.floor(history.length / 2);
  if (countEl) countEl.textContent = `${turns} turn${turns !== 1 ? 's' : ''}`;

  container.innerHTML = history.map(entry => `
    <div class="history-item">
      <div class="history-item-role ${entry.role}">${entry.role === 'user' ? '🙋 You' : '🤖 Bot'}</div>
      <div class="history-item-text">${escapeHtml(entry.content)}</div>
    </div>
  `).join('');
}

/** Show a toast message */
export function showToast(message, durationMs = 3500) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), durationMs);
}

/** Hide the welcome screen */
export function hideWelcome() {
  document.getElementById('welcome')?.classList.add('hidden');
}
