#!/usr/bin/env python3
"""
Publish a Tyler-approved blog draft to the live site.

Usage:
    bin/publish.py <slug-or-folder> [--video <youtube-url>]
    bin/publish.py <slug-or-folder> [--video <youtube-url>] [--no-push]

Examples:
    bin/publish.py construction-loans-in-katy-tx
    bin/publish.py 2026-05-25_construction-loans-in-katy-tx --video https://youtu.be/abc123
    bin/publish.py _drafts/2026-05-25_construction-loans-in-katy-tx --video https://youtu.be/abc

What it does:
    1. Locates the _drafts/<...>_<slug>/ folder
    2. Reads index.html + meta.json
    3. Inserts the YouTube embed at the top of the article (if --video provided)
    4. Moves index.html to blog/<slug>/index.html
    5. Updates blog/posts.json (prepends the new post)
    6. Rebuilds sitemap.xml from all blog/<slug>/ folders
    7. Removes the _drafts/<...>/ folder
    8. Commits and pushes (unless --no-push)
    9. Cloudflare Pages auto-deploys
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = REPO_ROOT / "_drafts"
BLOG_DIR = REPO_ROOT / "blog"
SITEMAP = REPO_ROOT / "sitemap.xml"
POSTS_JSON = BLOG_DIR / "posts.json"

STATIC_SITEMAP_URLS = [
    ("https://tylerhloans.com/", "weekly", "1.0"),
    ("https://tylerhloans.com/products/", "monthly", "0.9"),
    ("https://tylerhloans.com/products/conventional/", "monthly", "0.8"),
    ("https://tylerhloans.com/products/fha/", "monthly", "0.8"),
    ("https://tylerhloans.com/products/va/", "monthly", "0.8"),
    ("https://tylerhloans.com/products/jumbo/", "monthly", "0.8"),
    ("https://tylerhloans.com/products/construction/", "monthly", "0.8"),
    ("https://tylerhloans.com/investors/", "monthly", "0.9"),
    ("https://tylerhloans.com/builders/", "monthly", "0.9"),
    ("https://tylerhloans.com/refinance/", "monthly", "0.9"),
    ("https://tylerhloans.com/all-in-one/", "monthly", "0.8"),
    ("https://tylerhloans.com/calculator/", "monthly", "0.8"),
    ("https://tylerhloans.com/blog/", "daily", "0.8"),
]


def extract_youtube_id(url: str) -> Optional[str]:
    if not url:
        return None
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{6,})",
        r"youtube\.com/watch\?v=([A-Za-z0-9_-]{6,})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{6,})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{6,})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", url.strip()):
        return url.strip()
    return None


def find_draft_folder(arg: str) -> Path:
    """Resolve the draft folder from various input forms."""
    candidate = Path(arg)
    if candidate.is_dir():
        return candidate.resolve()
    in_drafts = DRAFTS_DIR / arg
    if in_drafts.is_dir():
        return in_drafts
    matches = sorted([d for d in DRAFTS_DIR.glob(f"*_{arg}") if d.is_dir()])
    if matches:
        return matches[-1]
    matches = sorted([d for d in DRAFTS_DIR.glob(f"*{arg}*") if d.is_dir()])
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        sys.exit(f"Multiple matches for '{arg}':\n  " + "\n  ".join(str(m.relative_to(REPO_ROOT)) for m in matches))
    sys.exit(f"Couldn't find a draft for '{arg}'. Try one of:\n  " + "\n  ".join(
        str(d.relative_to(REPO_ROOT)) for d in sorted(DRAFTS_DIR.iterdir()) if d.is_dir()
    ))


def build_video_embed(youtube_id: str) -> str:
    return (
        '<div class="video-embed">'
        f'<iframe src="https://www.youtube.com/embed/{youtube_id}" '
        'title="YouTube video" frameborder="0" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        'allowfullscreen></iframe>'
        '</div>'
    )


def collect_posts() -> List[dict]:
    """Scan blog/<slug>/index.html files and build a fresh posts.json (newest-first)."""
    posts = []
    for d in sorted(BLOG_DIR.iterdir()):
        if not d.is_dir():
            continue
        idx = d / "index.html"
        if not idx.is_file():
            continue
        html = idx.read_text(encoding="utf-8")
        title_m = re.search(r"<title>([^<|]+?)(?:\s*\|[^<]*)?</title>", html)
        date_m = re.search(r'datePublished":"([^"]+)"', html)
        meta_m = re.search(r'<meta name="description" content="([^"]+)"', html)
        posts.append({
            "title": (title_m.group(1).strip() if title_m else d.name),
            "slug": d.name,
            "date": (date_m.group(1) if date_m else ""),
            "meta": (meta_m.group(1) if meta_m else ""),
        })

    def parse_date(p):
        try:
            return datetime.strptime(p["date"], "%B %d, %Y")
        except Exception:
            return datetime.min
    posts.sort(key=parse_date, reverse=True)
    return posts


def write_sitemap(posts: List[dict]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, freq, pri in STATIC_SITEMAP_URLS:
        lines.append(f'  <url><loc>{url}</loc><changefreq>{freq}</changefreq><priority>{pri}</priority></url>')
    for p in posts:
        lines.append(
            f'  <url><loc>https://tylerhloans.com/blog/{p["slug"]}/</loc>'
            f'<changefreq>monthly</changefreq><priority>0.7</priority></url>'
        )
    lines.append('</urlset>')
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Publish a Tyler-approved blog draft")
    ap.add_argument("target", help="Draft slug or folder path (under _drafts/)")
    ap.add_argument("--video", help="YouTube URL or video ID (optional)")
    ap.add_argument("--no-push", action="store_true", help="Commit but don't push")
    ap.add_argument("--no-commit", action="store_true", help="Skip git entirely")
    args = ap.parse_args()

    draft = find_draft_folder(args.target)
    print(f"Draft:    {draft.relative_to(REPO_ROOT)}")

    meta_path = draft / "meta.json"
    if not meta_path.is_file():
        sys.exit(f"Missing meta.json in {draft}")
    meta = json.loads(meta_path.read_text())
    slug = meta["slug"]

    idx_path = draft / "index.html"
    if not idx_path.is_file():
        sys.exit(f"Missing index.html in {draft}")
    html = idx_path.read_text(encoding="utf-8")

    yt_id = extract_youtube_id(args.video) if args.video else None
    if yt_id:
        embed = build_video_embed(yt_id)
        if "<!-- VIDEO_EMBED_PLACEHOLDER -->" in html:
            html = html.replace("<!-- VIDEO_EMBED_PLACEHOLDER -->", embed)
        else:
            html = html.replace('<article class="article">', f'<article class="article">\n{embed}', 1)
        print(f"Embedded YouTube: {yt_id}")
    else:
        html = html.replace("<!-- VIDEO_EMBED_PLACEHOLDER -->", "")
        print("No video URL provided — publishing without embed.")

    live_dir = BLOG_DIR / slug
    live_dir.mkdir(parents=True, exist_ok=True)
    (live_dir / "index.html").write_text(html, encoding="utf-8")
    print(f"Live:     blog/{slug}/index.html")

    shutil.rmtree(draft)
    print(f"Removed:  {draft.relative_to(REPO_ROOT)}")

    posts = collect_posts()
    POSTS_JSON.write_text(json.dumps(posts, indent=2, ensure_ascii=False), encoding="utf-8")
    write_sitemap(posts)
    print(f"posts.json: {len(posts)} entries")
    print(f"sitemap.xml: {len(STATIC_SITEMAP_URLS)} static + {len(posts)} blog")

    if args.no_commit:
        print("Skipped git commit (--no-commit)")
        return

    title = meta.get("topic", slug)[:72]
    subprocess.run(["git", "-C", str(REPO_ROOT), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(REPO_ROOT), "commit", "-m", f"blog: {title}"], check=True)
    print(f"Committed: blog: {title}")

    if not args.no_push:
        subprocess.run(["git", "-C", str(REPO_ROOT), "push"], check=True)
        print("Pushed. Cloudflare will auto-deploy in ~30 seconds.")
    else:
        print("Skipped push (--no-push). Run 'git push' manually when ready.")


if __name__ == "__main__":
    main()
