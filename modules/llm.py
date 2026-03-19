# llm.py - Generate answers using HuggingFace flan-t5-base (free, local)

# modules/llm.py
# Generate answers using HuggingFace flan-t5-base (free, runs fully locally)
#
# CHANGED in v2:
#   - generate_answer() now accepts a single pre-built prompt string
#   - Prompt construction moved to prompt_builder.py
#   - This module only handles model loading and inference

from transformers import pipeline

print("[llm] Loading flan-t5-base model (first run may take a moment)...")

_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=300
)

print("[llm] Model loaded successfully.")


def generate_answer(prompt: str) -> str:
    """
    Generate an answer from a fully pre-built prompt string.

    CHANGED (v2): Old signature was generate_answer(query, context).
    Prompt is now assembled externally by prompt_builder.py which includes:
      - chat history
      - retrieved chunks from vector DB
      - structured output instructions (Answer + Key Points format)

    Args:
        prompt: Complete prompt string from prompt_builder.build_prompt()

    Returns:
        Raw generated text string from the model
    """
    if not prompt or not prompt.strip():
        return "I could not find enough information to answer that question."

    # Safety truncation — flan-t5-base handles ~512 tokens ~ 2000 chars
    prompt = prompt[:2000]

    try:
        result = _generator(prompt)
        answer = result[0].get("generated_text", "").strip()
        return answer if answer else "The model could not generate a response."
    except Exception as e:
        print(f"[llm] Error generating answer: {e}")
        return "An error occurred while generating the answer."
    
    
    
'''     
if __name__ == "__main__":
    test_query = "What is Artificial Intelligence?"

    test_context = """
    Artificial intelligence (AI) is the simulation of human intelligence in machines.
    It enables machines to learn, reason, and make decisions.
    AI is widely used in healthcare, finance, and automation.
    """

    print("\n[llm] Running test...\n")

    response = generate_answer(test_query, test_context)

    print("Question:", test_query)
    print("\nAnswer:\n", response)
    
'''

if __name__ == "__main__":
    print("\nTesting LLM...\n")

    test_prompt = """
    Context:
    AI is the simulation of human intelligence in machines.

    Question:
    What is AI?

    Answer:
    """

    response = generate_answer(test_prompt)

    print("Generated Answer:\n")
    print(response)