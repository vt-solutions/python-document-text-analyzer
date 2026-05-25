def analyze_text(text: str) -> dict:
    return {
        "characters": len(text),
        "words": len(text.split()),
        "text": text,
    }