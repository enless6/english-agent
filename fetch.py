import httpx
from bs4 import BeautifulSoup


def fetch_url(url: str) -> str:
    """把一个 URL 抓成文本。"""
    resp = httpx.get(url, timeout=10.0, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


def extract_text(html: str) -> str:
    """从 HTML 里捞出可读文本。"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    node = soup.select_one("#abs") or soup
    return " ".join(node.get_text(" ").split())


if __name__ == "__main__":
    html = open("page.html", encoding="utf-8").read()
    text = extract_text(html)
    print(f"clean {len(text)} 字符\n")
    for i in range(0, len(text), 300):
        print(f"[{i:>5}] {text[i : i + 300]}\n")
