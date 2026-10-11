
from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

class SentimentRequest(BaseModel):
    sentences: list[str]

positive = set("""
love loved lovely like liked likes great excellent amazing awesome
good happy wonderful fantastic best perfect beautiful enjoy enjoyed
delightful brilliant positive pleased success successful excited glad
thankful thanks recommend win winning impressive superb outstanding
fun helpful nice fantastic favorite favourite incredible better
beautifully smile cheerful satisfied easy convenient reliable
appreciate appreciated enjoy joyful fantastic adore adorable
""".split())

negative = set("""
hate hated terrible awful bad worst horrible sad angry disappointed
disappointing poor ugly boring annoying annoyed fail failed failure
broken useless painful difficult wrong problem problems frustrated
frustrating upset unhappy depressed fear scared regret disgusting
slow rude complaint complaints loss lose losing error errors stressful
damaged disaster pathetic miserable unpleasant inconvenient unfortunate
worse worst dislike disliked sadly unfortunately irritating irritating
""".split())

negations = {
    "not", "never", "no", "neither", "nor", "hardly", "barely",
    "isn't", "wasn't", "don't", "doesn't", "didn't", "can't",
    "couldn't", "won't", "wouldn't"
}

intensifiers = {"very", "really", "extremely", "absolutely", "so"}

def classify(sentence: str) -> str:
    words = re.findall(r"[a-z']+", sentence.lower())
    score = 0
    negate = False
    multiplier = 1

    for word in words:
        if word in negations:
            negate = True
            continue

        if word in intensifiers:
            multiplier = 1.5
            continue

        value = 1 if word in positive else -1 if word in negative else 0

        if value:
            score += (-value if negate else value) * multiplier
            negate = False
            multiplier = 1
        else:
            negate = False
            multiplier = 1

    if any(x in sentence for x in ["😊", "😍", "❤️", "😃", "😁"]):
        score += 2
    if any(x in sentence for x in ["😢", "😭", "😡", "😞", "💔"]):
        score -= 2

    if score > 0:
        return "happy"
    if score < 0:
        return "sad"
    return "neutral"

@app.get("/")
def home():
    return {"message": "Sentiment API is running"}

@app.post("/sentiment")
def sentiment(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": classify(sentence)
            }
            for sentence in request.sentences
        ]
    }
