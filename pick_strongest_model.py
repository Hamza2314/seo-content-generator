from anthropic import Anthropic
import os
from dotenv import load_dotenv
import re

def pick_strongest_model(client: Anthropic):
    try:
        raw = client.models.list()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models: {e}")
    
    ids = []
    for item in raw:
        mid = getattr(item, "id", None) or (item.get("id") if isinstance(item, dict) else item)
        if isinstance(mid, str):
            ids.append(mid)

    if not ids:
        raise RuntimeError("No models returned by API.")

    def extract_date(model_id: str) -> int:
        m = re.search(r'(\d{8})', model_id)
        return int(m.group(1)) if m else 0

    family_rank = {"sonnet": 3, "opus": 2, "haiku": 1}

    def score(model_id: str):
        lid = model_id.lower()
        fam_score = max((v for k, v in family_rank.items() if k in lid), default=0)
        date = extract_date(model_id)
        return (fam_score, date)

    best = sorted(ids, key=score, reverse=True)[0]
    return best


if __name__ == "__main__":
    load_dotenv()
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
    
    best_model = pick_strongest_model(client)
    
    response = client.messages.create(
        model=best_model,
        max_tokens=50,
        messages=[{"role": "user", "content": "Say something short."}]
    )
    
    print("API confirms model:", response.model)
    print("Content:", response.content[0].text)