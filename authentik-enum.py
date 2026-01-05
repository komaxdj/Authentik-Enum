#!/usr/bin/env python3
"""
authentik_admininterface_finder.py

What it does
- Fetches authentik release tags from GitHub (paged)
- Probes your instance for:
    {base_url}/static/dist/admin/AdminInterface-{version}.js
- Stops at the first "found" (HTTP 200 or 206) by default
- Prints an intuitive, user-friendly progress UI to STDERR
- Prints ONLY the final result (version + link) to STDOUT

Examples
  python3 authentik_admininterface_finder.py
  python3 authentik_admininterface_finder.py --base-url https://sso.example.com
  python3 authentik_admininterface_finder.py --all
  python3 authentik_admininterface_finder.py --all --include-404
  GITHUB_TOKEN=... python3 authentik_admininterface_finder.py --base-url https://sso.example.com

Notes
- Default mode prints only the first found version and link, then exits.
- Use --all if you want to test all versions and list all hits at the end.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler


GITHUB_API = "https://api.github.com"


def stderr_is_tty() -> bool:
    try:
        return sys.stderr.isatty()
    except Exception:
        return False


def eprint(msg: str = "") -> None:
    print(msg, file=sys.stderr, flush=True)


def color(s: str, code: str, enable: bool) -> str:
    if not enable:
        return s
    return f"\033[{code}m{s}\033[0m"


def dim(s: str, enable: bool) -> str:
    return color(s, "2", enable)


def bold(s: str, enable: bool) -> str:
    return color(s, "1", enable)


def green(s: str, enable: bool) -> str:
    return color(s, "32", enable)


def yellow(s: str, enable: bool) -> str:
    return color(s, "33", enable)


def red(s: str, enable: bool) -> str:
    return color(s, "31", enable)


def cyan(s: str, enable: bool) -> str:
    return color(s, "36", enable)


def normalize_tag(tag: str) -> str:
    tag = (tag or "").strip()
    tag = re.sub(r"^version/", "", tag)
    tag = re.sub(r"^v", "", tag)
    return tag


def parse_link_header(link: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in (link or "").split(","):
        part = part.strip()
        m = re.match(r'^<([^>]+)>;\s*rel="([^"]+)"$', part)
        if m:
            url, rel = m.group(1), m.group(2)
            out[rel] = url
    return out


@dataclass
class ProgressLine:
    enabled: bool
    last_render_ts: float = 0.0
    min_interval: float = 0.05  # seconds
    last_line_len: int = 0

    def update(self, line: str) -> None:
        if not self.enabled:
            return
        now = time.time()
        if now - self.last_render_ts < self.min_interval:
            return
        self.last_render_ts = now

        pad = " " * max(0, self.last_line_len - len(line))
        sys.stderr.write("\r" + line + pad)
        sys.stderr.flush()
        self.last_line_len = len(line)

    def done(self) -> None:
        if not self.enabled:
            return
        sys.stderr.write("\n")
        sys.stderr.flush()
        self.last_line_len = 0


def bar(i: int, total: int, width: int = 28) -> str:
    if total <= 0:
        total = 1
    frac = max(0.0, min(1.0, i / total))
    filled = int(round(frac * width))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def fmt_rate(done: int, started: float) -> str:
    elapsed = max(0.001, time.time() - started)
    rate = done / elapsed
    return f"{rate:.1f}/s"


def github_fetch_release_tags(
    repo: str,
    timeout: float,
    token: Optional[str],
    ui: ProgressLine,
    use_color: bool,
    verbose: bool,
) -> List[str]:
    opener = build_opener(HTTPRedirectHandler())
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "authentik-admininterface-finder",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    versions: List[str] = []
    seen = set()

    url = f"{GITHUB_API}/repos/{repo}/releases?per_page=100&page=1"
    page = 1
    started = time.time()

    eprint(bold("Phase 1/2:", use_color) + " Fetching release versions from GitHub")
    eprint(dim(f"Repo: {repo}", use_color))
    if not token:
        eprint(dim("Tip: set GITHUB_TOKEN to avoid GitHub rate limits.", use_color))

    while url:
        ui.update(f"{bar(page, page)}  page {page}  collected {len(versions)} tag(s)")

        if verbose:
            eprint(dim(f"[debug] GET {url}", use_color))

        req = Request(url, headers=headers, method="GET")
        try:
            with opener.open(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                data = json.loads(raw)

                for rel in data:
                    tag = normalize_tag(rel.get("tag_name"))
                    if not tag or tag in seen:
                        continue
                    seen.add(tag)
                    versions.append(tag)

                link = resp.headers.get("Link") or ""
                url = parse_link_header(link).get("next", "")

        except HTTPError as e:
            ui.done()
            eprint(red("GitHub API error:", use_color) + f" HTTP {getattr(e, 'code', '???')}")
            try:
                body = e.read().decode("utf-8", errors="replace")
                if body:
                    eprint(dim(body[:800], use_color))
            except Exception:
                pass
            eprint("If this is a rate limit, set GITHUB_TOKEN and retry.")
            raise

        except Exception as e:
            ui.done()
            eprint(red("Failed to fetch releases:", use_color) + f" {e}")
            raise

        page += 1
        time.sleep(0.05)

    ui.done()
    took = time.time() - started
    eprint(green("Done.", use_color) + f" Fetched {len(versions)} release tag(s) in {took:.1f}s.")
    eprint("")
    return versions


def probe_url_status(
    url: str,
    timeout: float,
) -> int:
    """
    Returns HTTP status code, or 0 on network failure.

    We probe with a cheap GET using Range bytes=0-0:
    - 206 means Range supported and content exists
    - 200 also counts as exists
    - 404 means not found
    """
    opener = build_opener(HTTPRedirectHandler())
    req = Request(
        url,
        headers={
            "User-Agent": "authentik-admininterface-finder",
            "Range": "bytes=0-0",
        },
        method="GET",
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            return int(getattr(resp, "status", resp.getcode()))
    except HTTPError as e:
        return int(getattr(e, "code", 0) or 0)
    except (URLError, TimeoutError, Exception):
        return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Find the first authentik AdminInterface-{version}.js that exists on your instance.",
    )
    ap.add_argument("--base-url", help="Base URL, e.g. https://sso.example.com")
    ap.add_argument("--repo", default="goauthentik/authentik", help="GitHub repo to query for releases")
    ap.add_argument("--timeout", type=float, default=20.0, help="Network timeout (seconds)")
    ap.add_argument("--sleep", type=float, default=0.0, help="Sleep between probes (seconds)")
    ap.add_argument("--all", action="store_true", help="Probe all versions and list all hits at the end")
    ap.add_argument("--include-404", action="store_true", help="Show 404 probes in the live UI (not recommended)")
    ap.add_argument("--verbose", action="store_true", help="Extra logs to STDERR")
    ap.add_argument("--no-ui", action="store_true", help="Disable progress UI (useful for CI logs)")
    args = ap.parse_args()

    base_url = (args.base_url or "").strip()
    if not base_url:
        base_url = input("Enter base URL (e.g. https://sso.example.com): ").strip()
    base_url = base_url.rstrip("/")
    if not base_url:
        eprint("No base URL provided.")
        return 2

    use_color = stderr_is_tty() and not args.no_ui
    ui_enabled = stderr_is_tty() and not args.no_ui

    token = os.environ.get("GITHUB_TOKEN") or None

    gh_ui = ProgressLine(enabled=ui_enabled)

    try:
        versions = github_fetch_release_tags(
            repo=args.repo,
            timeout=args.timeout,
            token=token,
            ui=gh_ui,
            use_color=use_color,
            verbose=args.verbose,
        )
    except Exception:
        return 1

    if not versions:
        eprint(red("No GitHub releases found.", use_color))
        return 1

    eprint(bold("Phase 2/2:", use_color) + " Probing your instance for AdminInterface JS")
    eprint(dim(f"Base: {base_url}", use_color))
    eprint(dim("Path: /static/dist/admin/AdminInterface-{version}.js", use_color))
    eprint("")

    probe_ui = ProgressLine(enabled=ui_enabled)
    started = time.time()

    found: List[Tuple[str, str, int]] = []

    total = len(versions)
    checked = 0

    for i, ver in enumerate(versions, start=1):
        url = f"{base_url}/static/dist/admin/AdminInterface-{ver}.js"
        status = probe_url_status(url, timeout=args.timeout)
        checked += 1

        # Live, intuitive one-line status
        if ui_enabled:
            rate = fmt_rate(checked, started)
            status_txt = (
                green(str(status), use_color) if status in (200, 206) else
                yellow(str(status), use_color) if status in (301, 302, 307, 308) else
                red(str(status), use_color) if status == 0 else
                dim(str(status), use_color)
            )

            # Only show 404 explicitly if requested, otherwise keep UI calm
            extra = ""
            if args.include_404 or status not in (404,):
                extra = f"  status {status_txt}"
            else:
                extra = "  status " + dim("404", use_color)

            label = f"{ver}"
            line = f"{bar(i, total)}  {i}/{total}  {rate}  checking {cyan(label, use_color)}{extra}"
            probe_ui.update(line)
        elif args.verbose:
            eprint(f"checking [{i}/{total}] {ver} -> HTTP {status}")

        # Treat 200 and 206 as "exists"
        if status in (200, 206):
            found.append((ver, url, status))
            if not args.all:
                break

        if args.sleep > 0:
            time.sleep(args.sleep)

    probe_ui.done()

    eprint("")
    took = time.time() - started

    # Final result (human-friendly) to STDERR
    eprint(bold("Final result:", use_color))
    eprint(dim(f"Checked: {checked}/{total} versions in {took:.1f}s", use_color))
    print()

    if not found:
        eprint(red("No AdminInterface JS found for any GitHub release tag.", use_color))
        return 3

    if args.all:
        eprint(green(f"Found {len(found)} hit(s):", use_color))
        for ver, url, status in found:
            eprint(f"  - {green(ver, use_color)}  (HTTP {status}) - {url}")

    # Default mode: print ONLY the first found version + link to STDOUT
    ver, url, status = found[0]
    eprint(green("Found:", use_color) + f" {green(ver, use_color)} (HTTP {status}) - {url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
