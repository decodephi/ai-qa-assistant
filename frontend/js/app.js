// frontend/js/app.js
// Main controller — wires up the UI, API calls, and user interactions.

import { askQuestion, clearMemory, getHistory, getStatus } from './api.js';
import {
  autoGrow,
  scrollToBottom,
  renderUserMessage,
  renderTypingIndicator,
  removeTypingIndicator,
  renderBotMessage,
  renderSidebarHistory,
  updateBackendBadge,
  showToast,
  hideWelcome,
} from './ui.js';

// ── DOM refs ───────────────────────────────────────────────────────────────────
const chatMessages = document.getElementById('chat-messages');
const chatInput    = document.getElementById('chat-input');
const sendBtn      = document.getElementById('send-btn');
const clearBtn     = document.getElementById('clear-btn');

// ── State ──────────────────────────────────────────────────────────────────────
let isLoading = false;

// ── Init ───────────────────────────────────────────────────────────────────────
async function init() {
  // Fetch status to show active backend
  try {
    const status = await getStatus();
    updateBackendBadge(status.backend);
  } catch (_) {
    updateBackendBadge('Offline');
  }

  // Restore history from server
  try {
    const history = await getHistory();
    renderSidebarHistory(history);
  } catch (_) { /* silent */ }

  // Wire up suggestion chips
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chatInput.value = chip.textContent.trim();
      chatInput.dispatchEvent(new Event('input'));
      chatInput.focus();
    });
  });
}

// ── Send message ───────────────────────────────────────────────────────────────
async function sendMessage() {
  const query = chatInput.value.trim();
  if (!query || isLoading) return;

  // Disable UI
  isLoading      = true;
  sendBtn.disabled = true;
  chatInput.value  = '';
  chatInput.style.height = 'auto';

  // Hide welcome screen on first message
  hideWelcome();

  // Show user bubble
  renderUserMessage(chatMessages, query);

  // Show typing indicator
  renderTypingIndicator(chatMessages);

  try {
    const result = await askQuestion(query);

    removeTypingIndicator();
    renderBotMessage(chatMessages, result);
    updateBackendBadge(result.backend);

    // Refresh sidebar history
    const history = await getHistory();
    renderSidebarHistory(history);

  } catch (error) {
    removeTypingIndicator();
    showToast(`⚠️ ${error.message || 'Something went wrong. Please try again.'}`);
    renderBotMessage(chatMessages, {
      answer:     'Sorry, I encountered an error. Please check the server and try again.',
      key_points: [],
      sources:    [],
    });
  } finally {
    isLoading        = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// ── Clear conversation ─────────────────────────────────────────────────────────
async function clearConversation() {
  if (isLoading) return;
  try {
    await clearMemory();
  } catch (_) { /* silent */ }

  // Clear UI
  chatMessages.innerHTML = '';

  // Restore welcome screen
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.classList.remove('hidden');

  renderSidebarHistory([]);
  showToast('🗑️ Conversation cleared.');
}

// ── Event listeners ────────────────────────────────────────────────────────────
sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', clearConversation);

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

chatInput.addEventListener('input', () => autoGrow(chatInput));

// ── Start ──────────────────────────────────────────────────────────────────────
init();
