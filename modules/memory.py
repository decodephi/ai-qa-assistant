
# Manages short-term chat history (last N conversations).
# This is a simple in-process store — no database required.
# Each conversation turn is stored as {"role": "user"/"assistant", "content": "..."}

from collections import deque

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_TURNS = 5          # number of full Q&A pairs to remember
MAX_CONTENT_CHARS = 300  # truncate each stored message to save memory


class ChatMemory:
    """
    Stores the last MAX_TURNS conversation turns in a circular buffer (deque).

    Structure of each entry:
        {
            "role":    "user" | "assistant",
            "content": "..."
        }
    A single 'turn' = 1 user message + 1 assistant message = 2 entries.
    So we store MAX_TURNS * 2 entries total.
    """

    def __init__(self, max_turns: int = MAX_TURNS):
        # maxlen * 2 because each turn has a user + assistant message
        self._history: deque = deque(maxlen=max_turns * 2)

    def add_turn(self, user_msg: str, assistant_msg: str) -> None:
        """
        Save one full conversation turn (user question + assistant answer).

        Args:
            user_msg:      The question the user asked
            assistant_msg: The answer the assistant gave
        """
        # Truncate to avoid bloating the prompt with huge stored text
        self._history.append({
            "role": "user",
            "content": user_msg.strip()[:MAX_CONTENT_CHARS]
        })
        self._history.append({
            "role": "assistant",
            "content": assistant_msg.strip()[:MAX_CONTENT_CHARS]
        })

    def get_history(self) -> list[dict]:
        """
        Return the full stored history as a list of role/content dicts.

        Returns:
            e.g. [
                {"role": "user",      "content": "What is AI?"},
                {"role": "assistant", "content": "AI stands for..."},
                ...
            ]
        """
        return list(self._history)

    def format_for_prompt(self) -> str:
        """
        Convert history to a readable block for injecting into the LLM prompt.

        Returns:
            A multi-line string like:
                User: What is AI?
                Assistant: AI stands for Artificial Intelligence...
        """
        if not self._history:
            return ""

        lines = []
        for entry in self._history:
            role = "User" if entry["role"] == "user" else "Assistant"
            lines.append(f"{role}: {entry['content']}")
        return "\n".join(lines)

    def enhance_query(self, current_query: str) -> str:
        """
        If the user asks a follow-up (e.g. 'What about its history?'),
        prepend the last user question to give the LLM full context.

        Args:
            current_query: The latest question from the user

        Returns:
            Enriched query string for better web search & retrieval
        """
        follow_up_signals = [
            "what about", "and", "also", "more about", "tell me more",
            "explain", "why", "how", "who", "when", "where", "it", "this", "that"
        ]

        query_lower = current_query.lower().strip()

        # Check if this looks like a follow-up question
        is_follow_up = (
            len(query_lower.split()) <= 6 or
            any(query_lower.startswith(signal) for signal in follow_up_signals)
        )

        if is_follow_up and self._history:
            # Get last user question for context enrichment
            past_user_msgs = [
                e["content"] for e in self._history if e["role"] == "user"
            ]
            if past_user_msgs:
                last_question = past_user_msgs[-1]
                enhanced = f"{last_question} {current_query}"
                print(f"[memory] Enhanced query: '{enhanced}'")
                return enhanced

        return current_query

    def clear(self) -> None:
        """Wipe all stored history."""
        self._history.clear()

    def __len__(self) -> int:
        return len(self._history)



chat_memory = ChatMemory()


