"""
A minimal HTML tree on the standard library parser, enough to query the event pages.

The pages are machine-generated and well formed, so a small tree with tag, class and
text queries is simpler and more predictable here than a scraping dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
             "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "svg", "noscript"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Node | str] = field(default_factory=list)
    parent: Node | None = field(default=None, repr=False)

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def text(self) -> str:
        parts: list[str] = []
        self._collect_text(parts)
        return re.sub(r"\s+", " ", " ".join(parts)).strip()

    def _collect_text(self, parts: list[str]) -> None:
        for child in self.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag not in SKIP_TAGS:
                child._collect_text(parts)

    def iter(self) -> list[Node]:
        nodes: list[Node] = []
        for child in self.children:
            if isinstance(child, Node):
                nodes.append(child)
                nodes.extend(child.iter())
        return nodes

    def find_all(self, tag: str | None = None, cls: str | None = None) -> list[Node]:
        return [n for n in self.iter()
                if (tag is None or n.tag == tag) and (cls is None or cls in n.classes)]

    def find(self, tag: str | None = None, cls: str | None = None) -> Node | None:
        found = self.find_all(tag, cls)
        return found[0] if found else None

    def child_elements(self) -> list[Node]:
        return [c for c in self.children if isinstance(c, Node)]


class _TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {k: v or "" for k, v in attrs}, parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {k: v or "" for k, v in attrs}, parent=self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag: str) -> None:
        # Close back to the matching open tag, tolerating unclosed children.
        for depth in range(len(self.stack) - 1, 0, -1):
            if self.stack[depth].tag == tag:
                del self.stack[depth:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def parse_html(html: str) -> Node:
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


_BLOCK_TAGS = {"p", "div", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"}
_INVISIBLE = dict.fromkeys(map(ord, "​‌‍﻿"))


def html_to_markdown(text: str) -> str:
    """
    Convert the small HTML subset the catalog uses in abstracts (paragraphs, line breaks,
    links, lists) to Markdown, and drop zero-width characters. Plain text passes through.
    """
    text = text.translate(_INVISIBLE).replace("\xa0", " ")
    if "<" not in text:
        return text.strip()
    blocks: list[str] = []
    current: list[str] = []

    def flush() -> None:
        paragraph = re.sub(r"[ \t]+", " ", "".join(current))
        paragraph = "\n".join(line.strip() for line in paragraph.split("\n")).strip()
        if paragraph:
            blocks.append(paragraph)
        current.clear()

    def walk(node: Node) -> None:
        for child in node.children:
            if isinstance(child, str):
                current.append(child.replace("\n", " "))
            elif child.tag == "br":
                current.append("\n")
            elif child.tag == "a" and child.attrs.get("href"):
                label = child.text() or child.attrs["href"]
                current.append(f"[{label}]({child.attrs['href']})")
            elif child.tag in _BLOCK_TAGS:
                flush()
                if child.tag == "li":
                    current.append("- ")
                walk(child)
                flush()
            elif child.tag not in SKIP_TAGS:
                walk(child)

    walk(parse_html(text))
    flush()
    return "\n\n".join(blocks)
