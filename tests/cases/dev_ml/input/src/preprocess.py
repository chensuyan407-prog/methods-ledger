"""Clean raw THUCNews dump and write jsonl splits."""
import json, random
from sklearn.model_selection import train_test_split
MIN_CHARS = 20
MAX_CHARS = 2000

def run(raw):
    docs = [d for d in raw if MIN_CHARS <= len(d["text"]) <= MAX_CHARS]
    docs = list({d["text"]: d for d in docs}.values())  # exact dedup
    train, rest = train_test_split(docs, test_size=0.2, random_state=2023, stratify=[d["label"] for d in docs])
    val, test = train_test_split(rest, test_size=0.5, random_state=2023)
    return train, val, test
