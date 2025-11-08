import os
from dotenv import load_dotenv
import requests
import anthropic
from pick_strongest_model import pick_strongest_model

load_dotenv()
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
CLAUDE_MODEL = pick_strongest_model(client)

# Cities to exclude from keyword results, KEEP: Hamburg, Frankfurt, München, Neumünster (client service regions)
CITY_MODIFIERS = [
    "berlin", "bonn", "duisburg", "augsburg", "aachen", "köln", "leipzig", "stuttgart",
    "bremen", "düsseldorf", "hannover", "kiel", "saarbrücken", "potsdam", "erfurt",
    "mainz", "wiesbaden", "dortmund", "essen"
]

def get_semrush_raw_keywords(topic, max_keywords=50):
    """Get raw keywords from SEMrush API"""
    print(f"[INFO] SEMrush API called with topic: '{topic}'")
    url = (
        f"https://api.semrush.com/?type=phrase_related&key={SEMRUSH_API_KEY}"
        f"&phrase={topic}&database=de&export_columns=Ph,Nq&display_limit={max_keywords}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        print("📦 SEMrush Raw Response:")
        print(response.text)

        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return []

        keywords = []
        for line in lines[1:]:
            try:
                phrase, volume = line.strip().split(";")
                volume = int(volume)
                if volume >= 10 and not any(city in phrase.lower() for city in CITY_MODIFIERS):
                    keywords.append((phrase.strip(), volume))
            except ValueError:
                continue

        print(f"[INFO] SEMrush found {len(keywords)} cleaned keywords")
        keywords.sort(key=lambda x: x[1], reverse=True)
        return keywords

    except Exception as e:
        print(f"[ERROR] SEMrush fetch failed: {e}")
        return []

def select_and_group_keywords_with_claude(topic, keyword_volume_list):
    """Use Claude to select and group similar keywords, returning 20 keywords"""
    if not keyword_volume_list:
        return []
    
    print(f"[INFO] Claude analyzing {len(keyword_volume_list)} keywords for grouping and selection")
    keyword_block = "\n".join([f"{kw} — {vol}" for kw, vol in keyword_volume_list])

    prompt = f"""
Keywords with search volume:

{keyword_block}

You are given a list of keywords (with search volume) from SEMrush. Your task is to:

Group Similar Keywords:
Identify keywords that are just variations, typos, synonyms of the same concept.
Merge them into one descriptive representative keyword.

Select 20 Final Keywords:
Pick the 20 most relevant and descriptive grouped keywords that cover the whole topic area.
Prioritize keywords that are legally precise, descriptive, and commonly used.
Avoid duplicates, redundant forms, or overly generic terms.
Keep keywords that are comprehensive and representative of the topic.

Output Format:
Return the final 20 grouped keywords each in one line without numbering.
No extra commentary, just the clean list.

Goal: Get the 20 strongest, most descriptive grouped keywords that represent the essence of the topic.
"""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=800,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        keywords_text = response.content[0].text.strip()
        keywords_list = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
        print(f"[INFO] Claude selected {len(keywords_list)} grouped keywords")
        return keywords_list
    except Exception as e:
        print(f"[ERROR] Claude keyword grouping failed: {e}")
        return []

def get_seo_keywords_for_topic(topic):
    """Main function to get grouped SEO keywords for a topic"""
    raw_keywords = get_semrush_raw_keywords(topic)
    if raw_keywords:
        grouped_keywords = select_and_group_keywords_with_claude(topic, raw_keywords)
        return grouped_keywords
    return []

# Test Run
if __name__ == "__main__":
    topic = "betäubungsmittelstrafrecht"
    keywords = get_seo_keywords_for_topic(topic)
    print("Final Grouped Keywords:")
    for i, kw in enumerate(keywords, 1):
        print(f"{i}. {kw}")