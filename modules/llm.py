# llm.py - Generate answers using HuggingFace flan-t5-base (free, local)

from transformers import pipeline

# Load the model once at module level (avoids reloading on every call)
print("[llm] Loading flan-t5-base model (first run may take a moment)...")

_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    max_new_tokens=300
)

print("[llm] Model loaded successfully.")


def generate_answer(query: str, context: str) -> str:
    """
    Generate an answer using flan-t5-base given a question and context.

    Args:
        query: The user's question
        context: Combined text scraped from web sources

    Returns:
        Generated answer string
    """
    if not context.strip():
        return "I could not find enough information to answer that question."

    # Construct a clear prompt for the model
    prompt = (
        f"Answer the following question based on the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Answer:"
    )

    # Truncate prompt if too long (flan-t5-base has a 512 token limit)
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