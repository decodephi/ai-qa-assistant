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
    
    ''' #For only pass prompt paramenter it will show smae prompt in repetation.
            #  Now adding same extra paramenter to get strong result
    '''  

    try:
        result = _generator(
            
            prompt,
            max_new_tokens = 300,
            do_sample=True,
            temperature=0.7,
            top_p = 0.9,
            repetition_penalty = 1.2
            
            )
        answer = result[0].get("generated_text", "").strip()
        
        return answer if answer else "The model could not generate a response."
    except Exception as e:
        print(f"[llm] Error: {e}")
        return "An error occurred while generating the answer."
    
    
    
  