#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL = "https://celsius232.es/autores-celsius/"
STATE_FILE = Path(__file__).with_name("authors.json")
USER_AGENT = "celsius-author-tracker/1.0"


class AuthorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.authors: list[str] = []
        self.in_title = False
        self.in_link = False
        self.chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = set(dict(attrs).get("class", "").split())
        if tag == "h2" and {"blog-shortcode-post-title", "entry-title"} <= classes:
            self.in_title = True
        elif self.in_title and tag == "a":
            self.in_link = True
            self.chunks = []

    def handle_endtag(self, tag: str) -> None:
        if self.in_link and tag == "a":
            name = " ".join(html.unescape("".join(self.chunks)).split())
            if name:
                self.authors.append(name)
            self.in_link = False
        elif self.in_title and tag == "h2":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_link:
            self.chunks.append(data)


def fetch_authors() -> list[str]:
    request = Request(URL, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=20) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            page = response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error: {exc.code} {exc.reason}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"network error: {exc}") from exc

    parser = AuthorParser()
    parser.feed(page)
    authors = list(dict.fromkeys(parser.authors))
    if not authors:
        raise RuntimeError("no authors found")
    return authors


def load_authors() -> list[str] | None:
    if not STATE_FILE.exists():
        return None
    with STATE_FILE.open(encoding="utf-8") as file:
        data = json.load(file)
    return data["authors"]


def save_authors(authors: list[str]) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".authors.", suffix=".json", dir=STATE_FILE.parent, text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        json.dump({"url": URL, "authors": authors}, file, ensure_ascii=False, indent=2)
        file.write("\n")
    Path(tmp).replace(STATE_FILE)


def main() -> int:
    try:
        authors = fetch_authors()
        old = load_authors()
        new = authors if old is None else [author for author in authors if author not in set(old)]
        save_authors(authors)
        print(json.dumps(new, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
