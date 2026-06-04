// frontend/js/ui.js
// DOM rendering helpers — clean, minimal, no emoji clutter.

function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

export function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

export function scrollToBottom(el) {
  requestAnimationFrame(() => { el.scrollTop = el.scrollHeight; });
}

export function renderUserMessage(container, text) {
  container.insertAdjacentHTML('beforeend', `
    <div class="message user">
      <div class="avatar">you</div>
      <div class="bubble-wrapper">
        <div class="bubble user-bubble">${escapeHtml(text)}</div>
        <div class="message-time">${formatTime()}</div>
      </div>
    </div>
  `);
  scrollToBottom(container);
}

export function renderTypingIndicator(container) {
  const el = document.createElement('div');
  el.className = 'typing-indicator';
  el.id = 'typing-indicator';
  el.innerHTML = `
    <div class="avatar">ai</div>
    <div class="typing-dots"><span></span><span></span><span></span></div>
    <span class="typing-label">searching...</span>
  `;
  container.appendChild(el);
  scrollToBottom(container);
  return el;
}

export function removeTypingIndicator() {
  document.getElementById('typing-indicator')?.remove();
}

export function renderBotMessage(container, { answer, key_points = [], sources = [], backend = '' }) {
  // Key points
  let kpHtml = '';
  if (key_points.length > 0) {
    kpHtml = `
      <div class="key-points">
        <div class="kp-label">Key points</div>
        <ul class="kp-list">
          ${key_points.map(kp => `<li>${escapeHtml(kp)}</li>`).join('')}
        </ul>
      </div>`;
  }

  // Sources
  let srcHtml = '';
  if (sources.filter(s => s.url).length > 0) {
    srcHtml = `
      <div class="sources">
        <div class="sources-label">Sources</div>
        ${sources.filter(s => s.url).map(s => `
          <a href="${s.url}" target="_blank" rel="noopener" class="source-card">
            <span class="source-icon">↗</span>
            <span class="source-title">${escapeHtml(s.title || s.url)}</span>
          </a>`).join('')}
      </div>`;
  }

  const backendNote = backend
    ? `<div class="message-time" style="margin-top:6px">${escapeHtml(backend)}</div>` : '';

  container.insertAdjacentHTML('beforeend', `
    <div class="message bot">
      <div class="avatar">ai</div>
      <div class="bubble-wrapper">
        <div class="bubble bot-bubble">${formatAnswer(answer)}</div>
        ${kpHtml}
        ${srcHtml}
        ${backendNote}
        <div class="message-time">${formatTime()}</div>
      </div>
    </div>
  `);
  scrollToBottom(container);
}

function formatAnswer(text) {
  if (!text) return 'No answer generated.';
  return escapeHtml(text)
    .replace(/\n\n/g, '</p><p style="margin-top:8px">')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code style="font-family:monospace;font-size:0.85em;background:#f0f0f0;padding:1px 5px;border-radius:3px;border:1px solid #ddd">$1</code>');
}

export function updateBackendBadge(backend) {
  const el = document.getElementById('backend-label');
  const dot = document.getElementById('status-dot');
  if (el && backend) {
    el.textContent = backend;
    if (dot) dot.classList.add('active');
  }
}

export function renderSidebarHistory(history) {
  const container = document.getElementById('sidebar-history');
  const countEl   = document.getElementById('history-count');
  if (!container) return;

  if (!history || history.length === 0) {
    container.innerHTML = `<div style="color:var(--gray-400);font-size:0.78rem;padding:8px">No history yet.</div>`;
    if (countEl) countEl.textContent = '0 turns';
    return;
  }

  const turns = Math.floor(history.length / 2);
  if (countEl) countEl.textContent = `${turns} turn${turns !== 1 ? 's' : ''}`;

  container.innerHTML = history.map(e => `
    <div class="history-item">
      <div class="history-item-role ${e.role}">${e.role === 'user' ? 'you' : 'ai'}</div>
      <div class="history-item-text">${escapeHtml(e.content)}</div>
    </div>`).join('');
}

export function showToast(msg, ms = 3000) {
  let t = document.getElementById('toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), ms);
}

export function hideWelcome() {
  document.getElementById('welcome')?.classList.add('hidden');
}
