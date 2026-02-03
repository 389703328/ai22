class AIService:
    @staticmethod
    def generate_response(prompt: str) -> str:
        return f"AI processed: {prompt}"

    @staticmethod
    def analyze_text(text: str) -> dict:
        return {"text": text, "length": len(text), "word_count": len(text.split())}
