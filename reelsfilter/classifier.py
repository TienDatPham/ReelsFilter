import json
import os
import re

import ollama


def classify(title: str, description: str, url: str, categories: list[str]) -> dict:
    """Classify a reel into one of the given categories using Ollama."""
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    cat_list = ", ".join(categories)

    prompt = (
        f"You are a content classifier. Given a Facebook Reel's metadata, "
        f"pick exactly ONE category from this list: {cat_list}.\n\n"
        f"URL: {url}\n"
        f"Title: {title or '(no title)'}\n"
        f"Description: {description or '(no description)'}\n\n"
        f'Respond ONLY with valid JSON in this exact format: '
        f'{{"category": "<name>", "confidence": <0.0-1.0>}}'
    )

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response["message"]["content"].strip()

    # Extract JSON even if the model wraps it in markdown fences
    match = re.search(r"\{.*?\}", raw, re.DOTALL)
    if match:
        data = json.loads(match.group())
        category = data.get("category", "other").lower()
        if category not in categories:
            category = "other"
        confidence = float(data.get("confidence", 0.0))
        return {"category": category, "confidence": round(confidence, 2)}

    return {"category": "other", "confidence": 0.0}
