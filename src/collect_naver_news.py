"""네이버 뉴스 검색 API 수집기.

W02 계획서의 "산업 뉴스" 보조 데이터 소스를 구현.
키워드별로 최신 뉴스 메타(제목·요약·링크·발행일)를 수집.

사용법:
    python src/collect_naver_news.py
    python src/collect_naver_news.py --display 100 --pages 10
    python src/collect_naver_news.py --keywords ISP PI POC BPR

환경변수:
    NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

API_URL = "https://openapi.naver.com/v1/search/news.json"
DEFAULT_KEYWORDS = [
    "ISP 발주", "BPR 컨설팅", "PMO 사업", "PoC 실증",
    "공공 정보화", "금융 IT", "보험 IT",
    "핀테크", "FDS 시스템",
    "디지털 전환", "클라우드 전환", "AI 공공",
    "마이데이터", "전자금융", "금감원",
]


def fetch(query: str, display: int, start: int,
          client_id: str, client_secret: str,
          timeout: int = 15, max_retry: int = 3) -> dict:
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {"query": query, "display": display, "start": start, "sort": "date"}
    last: Exception | None = None
    for attempt in range(max_retry):
        try:
            r = requests.get(API_URL, headers=headers, params=params, timeout=timeout)
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(1.5 ** attempt)
    raise RuntimeError(f"naver fetch failed: {last}")


def collect(client_id: str, client_secret: str,
            keywords: list[str], display: int, pages: int,
            out_dir: Path, sleep_sec: float = 0.12) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"naver_news_{stamp}.jsonl"

    total = 0
    with out_path.open("w", encoding="utf-8") as f:
        for kw in tqdm(keywords, desc="keywords"):
            for page in range(1, pages + 1):
                start = 1 + (page - 1) * display
                if start > 1000:  # 네이버 정책: start 최대 1000
                    break
                try:
                    payload = fetch(kw, display, start, client_id, client_secret)
                except Exception as e:
                    tqdm.write(f"  [ERR] {kw} p{page}: {e}")
                    break
                items = payload.get("items", []) or []
                if not items:
                    break
                for it in items:
                    it["_query"] = kw
                    f.write(json.dumps(it, ensure_ascii=False) + "\n")
                    total += 1
                time.sleep(sleep_sec)
    print(f"[DONE] 총 {total}건 저장 → {out_path}")
    return out_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--display", type=int, default=100, help="페이지당 건수(최대 100)")
    p.add_argument("--pages", type=int, default=10, help="키워드당 수집 페이지")
    p.add_argument("--keywords", nargs="*", default=None)
    p.add_argument("--out", default="data/raw/naver_news")
    return p.parse_args()


def main() -> int:
    load_dotenv()
    cid = os.getenv("NAVER_CLIENT_ID", "").strip()
    sec = os.getenv("NAVER_CLIENT_SECRET", "").strip()
    if not cid or not sec:
        print("[ERROR] NAVER_CLIENT_ID/SECRET 미설정 (.env 확인)", file=sys.stderr)
        return 2
    args = parse_args()
    kws = args.keywords or DEFAULT_KEYWORDS
    collect(cid, sec, kws, args.display, args.pages, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
