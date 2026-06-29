import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _normalize_score(score):
    return max(0.0, min(1.0, score))

def get_groq_score(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Return ONLY a float between 0.0 and 1.0 representing the probability this text is AI-generated (1.0 = AI)."},
                {"role": "user", "content": text}
            ],
            temperature=0.0,
            max_tokens=10
        )
        return float(response.choices[0].message.content.strip())
    except:
        return 0.5

def get_stylometric_score(text):
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    if len(lengths) < 2: return 0.5
    mean = sum(lengths) / len(lengths)
    variance = sum((length - mean) ** 2 for length in lengths) / len(lengths)
    score = 1.0 - min(1.0, variance / 100.0)
    return _normalize_score(score)

def get_vocabulary_richness(text):
    words = re.findall(r"\b\w+\b", text.lower())
    if not words: return 0.5
    ttr = len(set(words)) / len(words)
    score = 1.0 - min(1.0, ttr / 1.0)
    return _normalize_score(score)
