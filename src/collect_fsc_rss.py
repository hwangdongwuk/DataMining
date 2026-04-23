"""금융위원회(FSC) RSS 수집기.

W02 계획서의 "규제 공시" 보조 데이터 소스.
여러 RSS 게시판(보도자료·공지 등)에서 최신 항목 수집.

사용법:
    python src/collect_fsc_rss.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import requests

FEEDS = {
    "보도자료": "https://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0111",
    "공지사항": "https://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0112",
    "입법예고": "https://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0113",
    "행정예고": "https://www.fsc.go.kr/about/fsc_bbs_rss/?fid=0114",
}

OUT_DIR = Path("data/raw/fsc_rss")
HEADERS = {"User-Agent": "Mozilla/5.0 (DataMining Project)"}


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.replace("&nbsp;", " ").replace("&amp;", "&") \
         .replace("&lt;", "<").replace("&gt;", ">") \
         .replace("&quot;", '"').replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()


def fetch_feed(url: str, timeout: int = 20) -> list[dict]:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    d = feedparser.parse(r.content)
    out: list[dict] = []
    for e in d.entries:
        pub = e.get("published") or e.get("pubDate") or ""
        try:
            pub_dt = parsedate_to_datetime(pub).isoformat() if pub else None
        except Exception:
            pub_dt = None
        out.append({
            "title": strip_html(e.get("title", "")),
            "link": e.get("link", ""),
            "description": strip_html(e.get("description", ""))[:8000],
            "pubDate": pub,
            "pubDate_iso": pub_dt,
        })
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"fsc_rss_{stamp}.jsonl"

    total = 0
    with out_path.open("w", encoding="utf-8") as f:
        for category, url in FEEDS.items():
            try:
                items = fetch_feed(url)
            except Exception as e:
                print(f"[ERR] {category}: {e}")
                continue
            for it in items:
                it["_category"] = category
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
                total += 1
            print(f"  {category}: {len(items)}건")
    print(f"[DONE] 총 {total}건 → {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
