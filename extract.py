import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_PROMPT = """
You are an English learning assistant. Given an English passage, produce structured study material as JSON.
Output rules — follow every one of them exactly:
- Every text field must be in English, EXCEPT `translation`, which must be in Simplified Chinese.
- For every vocabulary entry, use the base form (lemma), never the inflected form that appears in the passage.
- Provide exactly 4 key sentences: the most important ones in the passage.
- Provide 5 to 10 vocabulary entries, only for words worth learning by an intermediate learner. Skip basic words.
- Provide exactly 3 takeaways.
- `difficulty` must be exactly one of these lowercase strings:
easy, medium, hard.
- `source` must be exactly "unknown" if the source is not given.
Never guess or invent a source.

The JSON must have exactly these fields:
- source: string
- topic: a short English label, at most 8 words
- key_sentences: list of objects with:
      - text: copied verbatim from the passage
      - translation: Simplified Chinese
      - note: an English grammar or usage explanation of the sentence, naming the specific structure involved (for example "the present perfect 'have transformed'"). Do not summarize the content.
- vocabulary: list of objects with word (string, base form), pos(string, English part of speech), definition (string, English), example(string, English sentence), usage_note (string, English)
- takeaways: list of strings, English
- difficulty: string, one of easy / medium / hard
  """


def call_model(text: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


def parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode error: {e}") from e


def has_chinese(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def inspect(data: dict, source_text: str) -> list[str]:
    """返回问题列表。空列表=全过"""
    problems = []

    for sent in data["key_sentences"]:
        if sent["text"] not in source_text:
            problems.append(f"MISMATCH: {sent['text']!r}")

    for sent in data["key_sentences"]:
        if has_chinese(sent["note"]):
            problems.append(f"CHINESE LEAK in note: {sent['note']!r}")

    for entry in data["vocabulary"]:
        if has_chinese(entry["usage_note"]):
            problems.append(f"CHINESE LEAK in usage_note: {entry['usage_note']!r}")

    return problems


TEXT = """
Large language models have transformed how software engineers approach problem-solving. 
Rather than writing every function by hand, developers now delegate routine tasks to models that can generate, refactor, and explain code. 
Yet this shift introduces a subtle risk: engineers may gradually lose the ability to reason about systems they did not write themselves.
The most effective teams treat these tools as accelerators rather than replacements, keeping their own judgment firmly in the loop.
  """


def main():
    clean_text = " ".join(TEXT.split())
    raw = call_model(clean_text)

    with open("raw_output.txt", "w", encoding="utf-8") as f:
        f.write(raw)

    data = parse_json(raw)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    problems = inspect(data, clean_text)
    print(f"key_sentences: {len(data['key_sentences'])}  problems: {len(problems)}")
    for p in problems:
        print(p)


if __name__ == "__main__":
    main()
