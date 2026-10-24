"""Untrusted fetch destinations never reach an internal socket or receive credentials."""

from __future__ import annotations

import io
import json
import socket
import ssl
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from typing import Any

import pytest

from universe_kb import fetch_safety
from universe_kb.enrich import social_targets
from universe_kb.fetch_safety import UnsafeDestination, open_public_url, public_http_url
from universe_kb.snapshot import Fetcher, FetchError, Snapshot

PUBLIC_IP = "93.184.216.34"


def addresses(ip: str, port: int = 443) -> list[tuple[Any, ...]]:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    sockaddr = (ip, port, 0, 0) if family == socket.AF_INET6 else (ip, port)
    return [(family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", sockaddr)]


def redirect(url: str, location: str, code: int = 302) -> urllib.error.HTTPError:
    headers = Message()
    headers["Location"] = location
    return urllib.error.HTTPError(url, code, "redirect", headers, io.BytesIO())


def test_initial_private_hosts_and_dns_aliases_never_reach_transport(
        monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr(fetch_safety, "_open_once", lambda req, *_: opened.append(req.full_url))
    dns = {"mixed.example": PUBLIC_IP,
           "2130706433": "127.0.0.1", "0177.0.0.1": "127.0.0.1", "0x7f000001": "127.0.0.1",
           "127.1": "127.0.0.1", "metadata.example": "169.254.169.254"}

    def resolve(host: str, port: int, **_: Any) -> list[tuple[Any, ...]]:
        if host == "mixed.example":
            return addresses(PUBLIC_IP, port) + addresses("fd00::1", port)
        return addresses(dns.get(host, "10.0.0.1"), port)

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    urls = ["http://127.0.0.1/", "http://10.0.0.1/", "http://172.16.0.1/",
            "http://192.168.1.1/", "http://169.254.169.254/", "http://100.100.100.200/",
            "http://0.0.0.0/", "http://224.0.0.1/", "http://[::1]/", "http://[fe80::1]/",
            "http://[fd00::1]/", "http://[::ffff:127.0.0.1]/", "http://[64:ff9b::a00:1]/",
            "http://localhost./", "http://internal.local/", "http://2130706433/",
            "http://0177.0.0.1/", "http://0x7f000001/", "http://127.1/",
            "http://metadata.example/", "https://mixed.example/", "https://private.example/",
            "https://public.example@127.0.0.1/", "https://public.example\\@127.0.0.1/",
            "http://[fe80::1%25en0]/", "https://%31%32%37.0.0.1/", "file:///etc/passwd"]
    for url in urls:
        with pytest.raises(UnsafeDestination):
            open_public_url(urllib.request.Request(url), timeout=1)
    assert opened == []


def test_dns_failures_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr(fetch_safety, "_open_once", lambda req, *_: opened.append(req.full_url))

    def missing(*_: Any, **__: Any) -> Any:
        raise socket.gaierror("no DNS answer")

    monkeypatch.setattr(socket, "getaddrinfo", missing)
    with pytest.raises(urllib.error.URLError):
        open_public_url(urllib.request.Request("https://missing.example"), timeout=1)
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_args, **_kwargs: [])
    with pytest.raises(UnsafeDestination):
        open_public_url(urllib.request.Request("https://empty.example"), timeout=1)
    assert opened == []


def test_each_redirect_is_validated_before_opening(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[str] = []
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, **_: addresses(
        "169.254.169.254" if host == "metadata.example" else PUBLIC_IP, port))
    for target in ["http://127.0.0.1/", "//metadata.example/latest", "http://[::1]/",
                   "file:///etc/passwd"]:
        opened.clear()

        def next_hop(req: urllib.request.Request, *_: Any, target: str = target) -> Any:
            opened.append(req.full_url)
            if req.full_url == "https://public.example/start":
                raise redirect(req.full_url, "/next", 301)
            raise redirect(req.full_url, target)

        monkeypatch.setattr(fetch_safety, "_open_once", next_hop)
        with pytest.raises(UnsafeDestination):
            open_public_url(urllib.request.Request("https://public.example/start"), timeout=1)
        assert opened == ["https://public.example/start", "https://public.example/next"]

    opened.clear()
    lookups: list[str] = []

    def rebound(host: str, port: int, **_: Any) -> list[tuple[Any, ...]]:
        lookups.append(host)
        return addresses(PUBLIC_IP if len(lookups) == 1 else "127.0.0.1", port)

    monkeypatch.setattr(socket, "getaddrinfo", rebound)
    with pytest.raises(UnsafeDestination):
        open_public_url(urllib.request.Request("https://public.example/start"), timeout=1)
    assert opened == ["https://public.example/start"]
    assert lookups == ["public.example", "public.example"]


def test_public_redirects_strip_cross_origin_secrets_and_bound_loops(
        monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[urllib.request.Request] = []
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, **_: addresses(PUBLIC_IP, port))
    final = object()

    def next_hop(req: urllib.request.Request, *_: Any) -> Any:
        requests.append(req)
        if req.full_url.endswith("/start"):
            raise redirect(req.full_url, "/same", 307)
        if req.full_url.endswith("/same"):
            raise redirect(req.full_url, "https://other.example/final")
        return final

    monkeypatch.setattr(fetch_safety, "_open_once", next_hop)
    request = urllib.request.Request("https://public.example/start", headers={
        "Authorization": "synthetic", "Cookie": "synthetic", "X-Api-Key": "synthetic",
        "User-Agent": "test-client", "Accept": "text/html"})
    assert open_public_url(request, timeout=1) is final
    assert requests[1].get_header("Authorization") == "synthetic"
    assert {name.lower(): value for name, value in requests[2].headers.items()} == {
        "user-agent": "test-client", "accept": "text/html"}

    requests.clear()

    def loop(req: urllib.request.Request, *_: Any) -> Any:
        requests.append(req)
        raise redirect(req.full_url, "/loop")

    monkeypatch.setattr(fetch_safety, "_open_once", loop)
    with pytest.raises(UnsafeDestination, match="too many redirects"):
        open_public_url(urllib.request.Request("https://public.example/loop"), timeout=1)
    assert len(requests) == fetch_safety.MAX_REDIRECTS + 1


def test_api_post_preserves_same_origin_body_and_rejects_cross_origin_replay(
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, **_: addresses(PUBLIC_IP, port))
    requests: list[urllib.request.Request] = []

    def next_hop(req: urllib.request.Request, *_: Any) -> Any:
        requests.append(req)
        raise redirect(req.full_url, "/next" if len(requests) == 1
                       else "https://other.example/next", 307)

    monkeypatch.setattr(fetch_safety, "_open_once", next_hop)
    request = urllib.request.Request("https://api.github.com/graphql", data=b"synthetic-body",
                                     headers={"Authorization": "synthetic",
                                              "Content-Type": "application/json"}, method="POST")
    with pytest.raises(UnsafeDestination, match="request body"):
        open_public_url(request, timeout=1)
    assert len(requests) == 2
    assert requests[1].data == b"synthetic-body"
    assert requests[1].get_method() == "POST"
    assert requests[1].get_header("Authorization") == "synthetic"
    assert requests[1].get_header("Content-type") == "application/json"

    requests.clear()

    def to_get(req: urllib.request.Request, *_: Any) -> Any:
        requests.append(req)
        if len(requests) == 1:
            raise redirect(req.full_url, "https://other.example/next", 303)
        return b"public"

    monkeypatch.setattr(fetch_safety, "_open_once", to_get)
    assert open_public_url(request, timeout=1) == b"public"
    assert requests[1].data is None
    assert requests[1].get_method() == "GET"
    assert requests[1].get_header("Authorization") is None
    assert requests[1].get_header("Content-type") is None


def test_real_handlers_pin_socket_keep_host_and_verify_tls(
        monkeypatch: pytest.MonkeyPatch) -> None:
    dns_calls: list[str] = []
    connected: list[Any] = []
    sent: list[bytes] = []
    tls: list[tuple[str, bool, ssl.VerifyMode]] = []
    wire_response = b"HTTP/1.1 200 OK\r\nContent-Length: 6\r\n\r\npublic"

    def resolve(host: str, port: int, **_: Any) -> list[tuple[Any, ...]]:
        dns_calls.append(host)
        return addresses(PUBLIC_IP if len(dns_calls) == 1 else "127.0.0.1", port)

    class Socket:
        def settimeout(self, value: float) -> None:
            pass

        def setsockopt(self, *_: Any) -> None:
            pass

        def connect(self, address: Any) -> None:
            connected.append(address)

        def sendall(self, data: bytes) -> None:
            sent.append(data)

        def makefile(self, *_: Any) -> io.BytesIO:
            return io.BytesIO(wire_response)

        def close(self) -> None:
            pass

    def wrap(context: ssl.SSLContext, sock: Any, *, server_hostname: str) -> Any:
        tls.append((server_hostname, context.check_hostname, context.verify_mode))
        return sock

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    monkeypatch.setattr(socket, "socket", lambda *_: Socket())
    monkeypatch.setattr(ssl.SSLContext, "wrap_socket", wrap)
    # Ambient proxy settings must not route around the checked connection.
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:3128")
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:3128")
    for scheme, port in [("http", 80), ("https", 443)]:
        dns_calls.clear()
        with open_public_url(urllib.request.Request(f"{scheme}://public.example/page"),
                             timeout=1) as response:
            assert response.read() == b"public"
        assert dns_calls == ["public.example"]
        assert connected[-1] == (PUBLIC_IP, port)
        assert b"Host: public.example\r\n" in sent[-1]
    assert tls == [("public.example", True, ssl.CERT_REQUIRED)]

    wire_response = (b"HTTP/1.1 302 Found\r\nLocation: http://127.0.0.1/admin\r\n"
                     b"Content-Length: 0\r\n\r\n")
    connected.clear()
    dns_calls.clear()
    with pytest.raises(UnsafeDestination):
        open_public_url(urllib.request.Request("https://public.example/start"), timeout=1)
    assert connected == [(PUBLIC_IP, 443)]


def test_fetcher_never_contacts_non_public_destinations(monkeypatch: pytest.MonkeyPatch) -> None:
    contacted: list[str] = []

    def unexpected(req: urllib.request.Request, *_: Any, **__: Any) -> Any:
        contacted.append(req.full_url)
        raise OSError("unexpected transport call")

    monkeypatch.setattr(urllib.request, "urlopen", unexpected)
    monkeypatch.setattr(fetch_safety, "_open_once", unexpected)
    fetcher = Fetcher(delay=0)
    result = fetcher.fetch("http://169.254.169.254/latest")
    assert result.status is None and result.body == b"" and result.error
    with pytest.raises(FetchError, match="blocked"):
        fetcher.request("GET", "http://127.0.0.1/admin")
    assert contacted == []


def test_candidate_urls_reject_local_and_malformed_forms_without_dns() -> None:
    for url in ["https://github.com/", "http://public.example:8080/feed", "https://xn--caf-dma.fr"]:
        assert public_http_url(url)
    for url in ["https://localhost/", "http://127.0.0.1/", "https://public.example@other.example/",
                "https://public.example:99999/", "https://public.example/\nnext", "ftp://public.example"]:
        assert not public_http_url(url)


def test_public_api_requests_keep_their_auth_and_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    requests: list[urllib.request.Request] = []
    monkeypatch.setattr(socket, "getaddrinfo", lambda host, port, **_: addresses(PUBLIC_IP, port))

    def api(req: urllib.request.Request, *_: Any) -> io.BytesIO:
        requests.append(req)
        return io.BytesIO(b'{"data": {"ok": true}}')

    monkeypatch.setattr(fetch_safety, "_open_once", api)
    fetcher = Fetcher(delay=0)
    assert fetcher.json("POST", "https://api.github.com/graphql", json_body={"query": "query {}"},
                        headers={"Authorization": "synthetic"}) == {"data": {"ok": True}}
    assert requests[0].get_header("Authorization") == "synthetic"
    body = requests[0].data
    assert isinstance(body, bytes)
    assert json.loads(body) == {"query": "query {}"}
    assert requests[0].get_header("Content-type") == "application/json"
    fetcher.request("POST", "https://api.example/token", form={"grant_type": "public"})
    assert requests[1].data == b"grant_type=public"
    assert requests[1].get_header("Content-type") == (
        "application/x-www-form-urlencoded; charset=UTF-8")


def test_social_targets_filter_unsafe_candidate_urls(tmp_path: Path) -> None:
    snapshot = Snapshot(tmp_path / "raw")
    snapshot.save_json("rainfocus/sessions.json", {"items": []}, url="https://event.example")
    snapshot.save_json("github/owners.json", {
        str(index): {"__typename": "User", "websiteUrl": url}
        for index, url in enumerate(["https://public.example", "http://127.0.0.1/admin",
                                     "https://localhost/", "https://public.example:99999/"])
    }, url="https://api.github.com/graphql")
    curation = tmp_path / "curation"
    curation.mkdir()
    (curation / "people.yaml").write_text("people: []\n")
    assert social_targets(snapshot, curation) == (["https://public.example"], [])
