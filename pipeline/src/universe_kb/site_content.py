"""
The organizer's own page copy as `Page` entities: every saved githubuniverse.com page and
attendee-portal page, split into sections in reading order.

The other parsers pull structured facts (agenda, offers, tour stops, FAQ entries) out of
these pages. This one keeps the prose itself, as written, so a new site can reuse hero
text, section intros, the "convince your boss" letter and card copy without scraping
again. It is generic over the markup rather than tied to one page's layout:

- A section starts at each `h1` to `h5` heading. The portal uses `h5` for card titles
  and `h6` for intro paragraphs, so `h6` reads as prose.
- An element that holds exactly one heading is a card: text before its heading (an
  eyebrow, a date) belongs to that heading's section. A top-level `<section id=...>`
  without a heading (the testimonials) starts a section of its own.
- Visible text becomes Markdown paragraphs. Navigation, header, footer, scripts,
  `aria-hidden` copies (animated and responsive duplicates), compact responsive
  variants and carousel counters are dropped; screen-reader text, which stands in for
  animated eyebrows and times, is kept.
- Button-styled links are calls to action. A `<button>` is a control whose label is
  dropped, unless it is disabled (a status such as "registration closed") or opens a
  dialog (a featured-speaker card), in which case its label is content.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from universe_kb.crawl import EDITION, PORTAL_PAGES, PORTAL_URL, SITE_PAGES, SITE_URL
from universe_kb.html_tree import Node, parse_html
from universe_kb.models import Image, Link, LinkKind, Page, PageSection, Source, SourceSystem

PORTAL_PAGE_URL = f"{PORTAL_URL}/flow/github/{EDITION}/attendee-portal/page/"

_HEADINGS = {"h1", "h2", "h3", "h4", "h5"}
_SKIP_TAGS = {"script", "style", "svg", "noscript", "template", "head", "header", "nav",
              "footer", "video", "audio", "iframe", "canvas", "select", "input", "textarea"}
_MARKS = {"strong": "**", "b": "**", "em": "*", "i": "*", "code": "`"}
_INLINE = {"abbr", "bdi", "cite", "data", "del", "ins", "kbd", "label", "mark", "q", "s",
           "small", "span", "sub", "sup", "time", "u", *_MARKS}
# Responsive copies (the compact hero eyebrow) and carousel position ("1 / 2").
_UI_CLASS = re.compile(r"compact|counter|pager", re.IGNORECASE)
_BUTTON_CLASS = re.compile(r"button|btn", re.IGNORECASE)
_INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\ufeff"))
_SPACES = dict.fromkeys(map(ord, "\xa0\u202f\u2009\u2007"), " ")
# A soft break between adjacent inline elements (`<span>nov</span><span>17</span>`).
_SOFT = "\x00"


@dataclass
class _Section:
    heading: str | None = None
    # The single heading of the card that opened this section, not yet reached.
    pending: Node | None = None
    blocks: list[str] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    calls_to_action: list[Link] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (self.heading or self.blocks or self.links or self.images
                    or self.calls_to_action)

    def to_model(self) -> PageSection:
        return PageSection(heading=self.heading, text="\n\n".join(self.blocks) or None,
                           links=self.links, images=self.images,
                           calls_to_action=self.calls_to_action)


def _normalize(text: str, keep_newlines: bool) -> str:
    text = text.translate(_INVISIBLE).translate(_SPACES)
    text = re.sub(f"{_SOFT}+", _SOFT, text)
    text = re.sub(rf"(?<=[^\s(\[]){_SOFT}(?=[^\s.,;:!?)\]])", " ", text).replace(_SOFT, "")
    if not keep_newlines:
        return re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _skipped(node: Node) -> bool:
    return (node.tag in _SKIP_TAGS or node.attrs.get("aria-hidden") == "true"
            or any(_UI_CLASS.search(c) for c in node.classes))


def _is_button(node: Node) -> bool:
    return node.attrs.get("role") == "button" or any(_BUTTON_CLASS.search(c)
                                                     for c in node.classes)


def _plain_text(node: Node) -> str:
    """Visible text on one line, for headings, labels and titles."""
    parts: list[str] = []

    def collect(n: Node) -> None:
        for child in n.children:
            if isinstance(child, str):
                parts.append(child)
            elif not _skipped(child):
                parts.append(_SOFT if child.tag in _INLINE or child.tag == "a" else " ")
                collect(child)

    collect(node)
    return _normalize("".join(parts), keep_newlines=False)


def _link_kind(url: str) -> LinkKind:
    parts = urlparse(url)
    host = (parts.hostname or "").removeprefix("www.")
    path = parts.path.lower()
    tour = host == "githubuniverse.com" and path.rstrip("/") == "/on-the-road"
    if "registration" in host or re.search(r"/(attendee-registration|getnotified)", path) or tour:
        return "registration"
    if host in {"youtube.com", "youtu.be"} or path.endswith((".mp4", ".webm")):
        return "video"
    if path.endswith((".webp", ".png", ".jpg", ".jpeg", ".gif")):
        return "image"
    if host == "github.com":
        return "github"
    if host.endswith("linkedin.com"):
        return "linkedin"
    if host in {"x.com", "twitter.com"}:
        return "x"
    if host == "bsky.app":
        return "bluesky"
    return "other" if path.endswith(".pdf") else "website"


class _Reader:
    """Walks one page's content in document order and collects its sections."""

    def __init__(self, base_url: str, keep_newlines: bool) -> None:
        self.base_url = base_url
        # The site renders newlines only where the copy has them (the letter template);
        # the portal's hand-written HTML has source indentation instead.
        self.keep_newlines = keep_newlines
        self.sections = [_Section()]
        self.inline: list[str] = []
        # Enclosing list items ([first paragraph still to come]) and blockquotes.
        self.context: list[list[bool] | str] = []
        self.headings: dict[int, list[Node]] = {}

    @property
    def section(self) -> _Section:
        return self.sections[-1]

    def read(self, root: Node) -> list[PageSection]:
        self._index_headings(root)
        self._walk(root)
        self._flush()
        return [s.to_model() for s in self.sections if not s.is_empty()]

    def _index_headings(self, node: Node) -> list[Node]:
        found: list[Node] = []
        for child in node.child_elements():
            if _skipped(child):
                continue
            if child.tag in _HEADINGS:
                found.append(child)
            else:
                found.extend(self._index_headings(child))
        self.headings[id(node)] = found
        return found

    def _absolute(self, ref: str) -> str | None:
        url = urljoin(self.base_url, ref.strip())
        return url if url.startswith(("http://", "https://")) else None

    def _start(self, heading: str | None = None, pending: Node | None = None) -> None:
        if self.section.is_empty() and self.section.pending is None:
            self.section.heading, self.section.pending = heading, pending
        else:
            self.sections.append(_Section(heading=heading, pending=pending))

    def _add_link(self, target: list[Link], url: str, label: str | None) -> None:
        link = Link(kind=_link_kind(url), url=url, label=label or None)
        if link not in target:
            target.append(link)

    def _flush(self) -> None:
        text = _normalize("".join(self.inline), self.keep_newlines)
        self.inline.clear()
        if not re.search(r"[^\W_]", text):
            return
        lines = text.split("\n")
        items = [c for c in self.context if isinstance(c, list)]
        if items:
            first = items[-1][0]
            items[-1][0] = False
            indent = "  " * (len(items) - 1)
            lines = [indent + ("- " if first and i == 0 else "  ") + line if line else line
                     for i, line in enumerate(lines)]
        if "quote" in self.context:
            lines = [f"> {line}".rstrip() for line in lines]
        self.section.blocks.append("\n".join(lines))

    def _walk(self, node: Node) -> None:
        for child in node.children:
            if isinstance(child, str):
                self.inline.append(child)
            elif not _skipped(child):
                self._element(child)

    def _element(self, node: Node) -> None:
        tag = node.tag
        if tag in _HEADINGS:
            self._heading(node)
        elif tag == "img":
            self._image(node)
        elif tag == "br":
            self.inline.append("\n" if self.keep_newlines else " ")
        elif tag == "a":
            self._anchor(node)
        elif tag == "button":
            self._button(node)
        elif tag in _INLINE:
            self.inline.append(_SOFT)
            marker = _MARKS.get(tag)
            if marker is None:
                self._walk(node)
            else:
                self._mark(node, marker)
        else:
            self._block(node)

    def _block(self, node: Node) -> None:
        self._flush()
        headings = self.headings.get(id(node), [])
        is_card = len(headings) == 1
        if is_card and self.section.pending is not headings[0]:
            self._start(pending=headings[0])
        elif not headings and node.tag == "section" and node.attrs.get("id"):
            self._start()
        frame: list[bool] | str | None = None
        if node.tag == "li" and not is_card:
            frame = [True]
        elif node.tag == "blockquote":
            frame = "quote"
        if frame is not None:
            self.context.append(frame)
        self._walk(node)
        self._flush()
        if frame is not None:
            self.context.pop()

    def _mark(self, node: Node, marker: str) -> None:
        outer = self.inline
        self.inline = []
        self._walk(node)
        inner = "".join(self.inline)
        self.inline = outer
        stripped = inner.strip()
        if stripped:
            lead, trail = inner[: len(inner) - len(inner.lstrip())], inner[len(inner.rstrip()):]
            self.inline.append(f"{lead}{marker}{stripped}{marker}{trail}")
        else:
            self.inline.append(inner)

    def _heading(self, node: Node) -> None:
        self._flush()
        text = _plain_text(node)
        if self.section.pending is node:
            self.section.heading, self.section.pending = text or None, None
        elif text:
            self._start(heading=text)
        for anchor in node.find_all("a"):
            url = self._absolute(anchor.attrs.get("href", ""))
            if url and not _skipped(anchor):
                self._add_link(self.section.links, url, _plain_text(anchor))
        self._images_in(node)

    def _anchor(self, node: Node) -> None:
        href = node.attrs.get("href", "")
        url = self._absolute(href) if href else None
        if _is_button(node):
            label = _plain_text(node)
            if url and label:
                self._add_link(self.section.calls_to_action, url, label)
            self._images_in(node, label)
            return
        self.inline.append(_SOFT)
        if url is None:
            self._walk(node)
            return
        label = _plain_text(node)
        self._images_in(node, label)
        if label:
            self.inline.append(f"[{label}]({url})")
            self._add_link(self.section.links, url, label)

    def _button(self, node: Node) -> None:
        if "disabled" in node.attrs or node.attrs.get("aria-haspopup"):
            self._flush()
            self._walk(node)
            self._flush()
        else:
            # A playlist thumbnail has no alt text of its own; its button names the video.
            self._images_in(node, _plain_text(node))

    def _images_in(self, node: Node, label: str | None = None) -> None:
        for child in node.child_elements():
            if _skipped(child):
                continue
            if child.tag == "img":
                self._image(child, label)
            else:
                self._images_in(child, label)

    def _image(self, node: Node, label: str | None = None) -> None:
        src = node.attrs.get("src", "").strip()
        url = self._absolute(src) if src and not src.startswith("data:") else None
        if url is None or urlparse(url).path.lower().endswith(".svg"):
            return
        if {node.attrs.get("width"), node.attrs.get("height")} & {"0", "1"}:
            return  # a tracking pixel
        alt = _normalize(node.attrs.get("alt", ""), keep_newlines=False) or label or None
        if all(image.url != url for image in self.section.images):
            self.section.images.append(Image(url=url, alt=alt))


def _portal_html(node: Any, out: list[str]) -> None:
    """
    A portal page's HTML blocks in document order. FAQ components hold their entries as
    question and answer fields rather than HTML; each becomes a heading and its answer.
    """
    if isinstance(node, dict):
        question, answer = node.get("question"), node.get("answer")
        if isinstance(question, str) and isinstance(answer, str):
            out.append(f"<section><h4>{question}</h4><div>{answer}</div></section>")
        for key, value in node.items():
            if key == "children" and isinstance(value, str):
                out.append(value)
            else:
                _portal_html(value, out)
    elif isinstance(node, list):
        for item in node:
            _portal_html(item, out)


def _meta(root: Node, *names: str) -> str | None:
    for name in names:
        for meta in root.find_all("meta"):
            if name in (meta.attrs.get("name"), meta.attrs.get("property")):
                content = _normalize(meta.attrs.get("content", ""), keep_newlines=False)
                if content:
                    return content
    return None


def _portal_labels(root: Node) -> dict[str, str]:
    """The site navigation's name for each portal page ("Sessions", "FAQs")."""
    labels: dict[str, str] = {}
    for nav in root.find_all("nav"):
        for anchor in nav.find_all("a"):
            href = anchor.attrs.get("href", "")
            label = _plain_text(anchor)
            if href.startswith(PORTAL_PAGE_URL) and label:
                labels.setdefault(href.removeprefix(PORTAL_PAGE_URL).strip("/"), label)
    return labels


def _source(system: SourceSystem, rel_path: str,
            manifest: dict[str, dict[str, Any]]) -> Source:
    entry = manifest[rel_path]
    return Source(system=system, url=entry["url"], retrieved_at=entry["retrieved_at"],
                  snapshot=f"raw/{rel_path}")


def build_pages(raw_dir: Path, manifest: dict[str, dict[str, Any]]) -> list[Page]:
    """
    One `Page` per saved githubuniverse.com page and attendee-portal page. `manifest` is
    the `files` mapping of `raw/manifest.json`, keyed by path relative to `raw_dir`.
    """
    found: list[Page] = []
    nav_labels: dict[str, str] = {}
    for name, path in SITE_PAGES.items():
        rel_path = f"site/{name}.html"
        url = f"{SITE_URL}{path}"
        root = parse_html((raw_dir / rel_path).read_text())
        reader = _Reader(url, keep_newlines=True)
        if name == "home":
            nav_labels = _portal_labels(root)
        title_node = root.find("title")
        found.append(Page(
            id=f"page:githubuniverse.com/{name}",
            site="githubuniverse.com",
            url=url,
            title=_plain_text(title_node) if title_node else name,
            description=_meta(root, "description", "og:description"),
            sections=reader.read(root.find("main") or root.find("body") or root),
            sources=[_source("githubuniverse.com", rel_path, manifest)],
        ))
    for page_uri in PORTAL_PAGES:
        rel_path = f"rainfocus/pages/{page_uri}.json"
        url = f"{PORTAL_PAGE_URL}{page_uri}"
        blocks: list[str] = []
        _portal_html(json.loads((raw_dir / rel_path).read_text())["data"]["pageData"], blocks)
        sections = _Reader(url, keep_newlines=False).read(parse_html("\n".join(blocks)))
        first_heading = next((s.heading for s in sections if s.heading), None)
        found.append(Page(
            id=f"page:attendee-portal/{page_uri}",
            site="attendee-portal",
            url=url,
            title=nav_labels.get(page_uri) or first_heading or page_uri,
            sections=sections,
            sources=[_source("rainfocus", rel_path, manifest)],
        ))
    return found
