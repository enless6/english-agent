import httpx
from bs4 import BeautifulSoup

ALLOWED_TYPES = ("text/html", "application/xhtml+xml", "text/plain")


class FetchError(Exception):
    """抓取失败。status 是建议返回给客户端的状态码。"""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def fetch_url(url: str) -> tuple[str, str]:
    """抓一个网页，返回 (HTML, 最终 URL)。只接受 HTML / 纯文本。"""
    try:
        resp = httpx.get(url, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise FetchError(f"could not fetch {url}: {e}") from e

    ctype = resp.headers.get("content-type", "").split(";")[0].strip().lower()
    if ctype not in ALLOWED_TYPES:
        raise FetchError(f"unsupported content type: {ctype or 'unknown'}", status=415)

    return resp.text, str(resp.url)


def extract_text(html: str) -> str:
    """从 HTML 里捞出可读文本。"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    node = soup.select_one("#abs") or soup
    return " ".join(node.get_text(" ").split())


if __name__ == "__main__":
    with open("page.html", encoding="utf-8") as f:
        html = f.read()
    text = extract_text(html)
    print(f"clean {len(text)} 字符\n")
    for i in range(0, len(text), 300):
        print(f"[{i:>5}] {text[i : i + 300]}\n")
