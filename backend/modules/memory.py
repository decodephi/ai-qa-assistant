# backend/modules/memory.py
# Short-term conversation memory (last N Q&A turns).

import logging
from collections import deque

logger = logging.getLogger(__name__)

MAX_TURNS        = 6    # full Q&A pairs to remember
MAX_CONTENT_CHARS = 400  # truncate stored messages


class ChatMemory:
    """
    Circular buffer storing the last MAX_TURNS conversation turns.

    Each turn = 1 user message + 1 assistant message = 2 entries.
    Total deque capacity = MAX_TURNS * 2.
    """

    def __init__(self, max_turns: int = MAX_TURNS):
        self._history: deque = deque(maxlen=max_turns * 2)

    # ── Write ──────────────────────────────────────────────────────────────────
    def add_turn(self, user_msg: str, assistant_msg: str) -> None:
        """Save one full conversation turn."""
        self._history.append({
            "role":    "user",
            "content": user_msg.strip()[:MAX_CONTENT_CHARS],
        })
        self._history.append({
            "role":    "assistant",
            "content": assistant_msg.strip()[:MAX_CONTENT_CHARS],
        })

    # ── Read ───────────────────────────────────────────────────────────────────
    def get_history(self) -> list[dict]:
        """Return the full history as a list of role/content dicts."""
        return list(self._history)

    def format_for_prompt(self) -> str:
        """Format history as a readable block for the LLM prompt."""
        if not self._history:
            return ""
        lines = []
        for entry in self._history:
            role = "User" if entry["role"] == "user" else "Assistant"
            lines.append(f"{role}: {entry['content']}")
        return "\n".join(lines)

    def enhance_query(self, current_query: str) -> str:
        """
        Enrich a follow-up query with context from the last user question.

        Heuristic: if the query is short or starts with a follow-up signal word,
        prepend the last user question to help the search and LLM.
        """
        FOLLOW_UP_SIGNALS = {
            "what about", "and", "also", "more", "tell me more",
            "explain", "why", "how", "who", "when", "where",
            "it", "this", "that", "its", "their", "he", "she", "they",
        }

        query_lower = current_query.lower().strip()
        first_word  = query_lower.split()[0] if query_lower.split() else ""

        is_follow_up = (
            len(query_lower.split()) <= 5
            or first_word in FOLLOW_UP_SIGNALS
            or any(query_lower.startswith(sig) for sig in FOLLOW_UP_SIGNALS if " " in sig)
        )

        if is_follow_up and self._history:
            past_user_msgs = [e["content"] for e in self._history if e["role"] == "user"]
            if past_user_msgs:
                last_q   = past_user_msgs[-1]
                enhanced = f"{last_q} {current_query}"
                logger.debug("[memory] Enhanced query: %r", enhanced)
                return enhanced

        return current_query

    # ── Manage ─────────────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Wipe all stored history."""
        self._history.clear()

    def __len__(self) -> int:
        return len(self._history)


# Singleton
chat_memory = ChatMemory()
