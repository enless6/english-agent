import io

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from pypdf.errors import PyPdfError

ALLOWED_TYPES = ("text/html", "application/xhtml+xml", "text/plain")


def pdf_to_text(content: bytes) -> str:
    """从 PDF 字节里抽文本。扫描件没有文字层，会返回空串。"""
    try:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
    except PyPdfError as e:
        raise FetchError(f"could not parse PDF: {e}", status=422) from e
    return " ".join(" ".join(pages).split())


def truncate(text: str, limit: int) -> tuple[str, bool]:
    """超出 limit 时在句子边界截断。返回 (文本, 是否截断)。"""
    if len(text) <= limit:
        return text, False
    cut = text.rfind(". ", 0, limit)
    if cut == -1:
        return text[:limit], True
    return text[: cut + 1], True


class FetchError(Exception):
    """抓取失败。status 是建议返回给客户端的状态码。"""

    def __init__(self, message: str, status: int = 502):
        super().__init__(message)
        self.status = status


def fetch_document(url: str) -> tuple[str, str]:
    """抓一个 URL 并抽出正文。HTML 和 PDF 都支持。返回 (文本, 最终 URL)。"""
    try:
        resp = httpx.get(url, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise FetchError(f"could not fetch {url}: {e}") from e

    mime = resp.headers.get("content-type", "").split(";")[0].strip().lower()
    final = str(resp.url)

    if mime == "application/pdf":
        return pdf_to_text(resp.content), final
    if mime in ALLOWED_TYPES:
        return html_to_text(resp.text), final
    raise FetchError(f"unsupported content type: {mime or 'unknown'}", status=415)


def html_to_text(html: str) -> str:
    """从 HTML 里捞出可读文本。"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    node = soup.select_one("#abs") or soup
    return " ".join(node.get_text(" ").split())


if __name__ == "__main__":
    with open("page.html", encoding="utf-8") as f:
        html = f.read()
    text = html_to_text(html)
    print(f"clean {len(text)} 字符\n")
    for i in range(0, len(text), 300):
        print(f"[{i:>5}] {text[i : i + 300]}\n")
