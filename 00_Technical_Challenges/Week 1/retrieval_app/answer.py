"""Stage 5: turn retrieved chunks into an answer.

YOUR CODE GOES HERE. The prompt is yours to write — it is the cheapest thing
in the pipeline to change and often the most effective.
"""

from .index import Hit, client

CHAT_MODEL = "claude-haiku-5-5"


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    """Assemble the messages list sent to the chat model.

    Args:
        question: the user's question.
        hits: what search() returned. May be empty.

    Returns:
        A list of {"role": ..., "content": ...} dicts — a system message
        setting the rules, and a user message carrying the context and the
        question.

    Three things your prompt has to decide, and they are real decisions:
      1. How do you label each chunk in the context so the model can refer to
         it? (hit.chunk_id exists for this.)
      2. What should it do when the context does not contain the answer? Say
         so explicitly, or it will answer from the nearest chunk regardless.
      3. What happens when `hits` is empty? Write that branch deliberately.

    Hint: Session 2's RAG_SYSTEM_TEMPLATE is a good starting point, and a
    better one once you have read Step 3's failures and edited it.
    """
    messages = [
        {"role": "system", "content": "You are an assistant that answers questions based on the provided excerpts. "
        "If the answer is not in the excerpts, say you don't know. Do not use your own knowledge to answer the question or provide any referrals. "
        "Do not make up answers or hallucinate. If the excerpts are empty, say you don't know. "
        "Each excerpt may start or end mid-sentence because the text was split into pieces; never say a section is missing or cut off. "
        "You see excerpts, not the full document, so don't make claims beyond the excerpts. "
        "Keep it short; do not describe excerpts that don't answer the question. "},
        {"role": "user", "content": f"Context:\n{'\n\n'.join(f'[chunk {h.chunk_id}] {h.text}' for h in hits) if hits else '(no excerpts)'}\n\nQuestion: {question}"}
    ]
    return messages 
 

    


def answer(question: str, hits: list[Hit]) -> str:
    """Call the chat model and return its reply as a string.

    Hint: `client().chat.completions.create(model=CHAT_MODEL, messages=...)`,
    then dig out `.choices[0].message.content`. Look up what `temperature`
    does to your results when you run the same question twice.
    """
    response = client().chat.completions.create(model=CHAT_MODEL, messages=build_messages(question, hits), temperature=1.0) #Haiku model does not support tempeorature
    return response.choices[0].message.content
