def build_context(results, max_chars=4000):
    context = ""
    for r in results:
        if len(context) + len(r["text"]) <= max_chars:
            context += r["text"] + "\n\n"
        else:
            break
    return context.strip()

def build_memory_context(chat_history, last_n=6):
    # take last N messages (like 3 user+assistant pairs)
    recent = chat_history[-last_n:]
    memory_text = ""
    for msg in recent:
        memory_text += f"{msg['role'].upper()}: {msg['content']}\n"
    return memory_text.strip()

def build_prompt(context, query, memory):
    return f"""
            You are an AI assistant.

            You must answer using:
            1) Memory (previous conversation)
            2) Book Context (retrieved chunks)

            If answer is not in Book Context, say: "Not found in the book".

            Conversation Memory:
            {memory}

            Book Context:
            {context}

            User Question:
            {query}

            Answer:
            """
