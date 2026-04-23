"""나라장터 입찰공고정보서비스 OpenAPI 수집기 (월별 분할 + 필터).

사용법:
    # 3년치 월별 분할 수집
    python src/collect_narajangteo_api.py \\
        --start 20230101 --end 20251231 \\
        --kind 용역 --split monthly \\
        --out data/raw/narajangteo

    # 단일 기간
    python src/collect_narajangteo_api.py \\
        --start 20240101 --end 20241231 \\
        --kind 용역 --out data/raw/narajangteo

환경변수:
    NARAJANGTEO_SERVICE_KEY  (.env 또는 export)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

BASE_URL = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService"
ENDPOINT_BY_KIND = {
    "용역": "/getBidPblancListInfoServc",
    "물품": "/getBidPblancListInfoThng",
    "공사": "/getBidPblancListInfoCnstwk",
    "외자": "/getBidPblancListInfoFrgcpt",
}


def fetch_page(service_key: str, endpoint: str, start: str, end: str,
               page_no: int, num_rows: int, timeout: int = 30,
               max_retry: int = 3) -> dict:
    url = BASE_URL + endpoint
    params = {
        "serviceKey": service_key,
        "pageNo": page_no,
        "numOfRows": num_rows,
        "inqryDiv": 1,
        "inqryBgnDt": f"{start}0000",
        "inqryEndDt": f"{end}2359",
        "type": "json",
    }
    last_exc = None
    for attempt in range(max_retry):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last_exc = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed after {max_retry} retries: {last_exc}")


def extract_items(payload: dict) -> tuple[list[dict], int]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", []) or []
    if isinstance(items, dict):
        items = items.get("item", [])
    total = int(body.get("totalCount", 0))
    return items, total


def month_ranges(start: str, end: str) -> list[tuple[str, str]]:
    s = datetime.strptime(start, "%Y%m%d").date()
    e = datetime.strptime(end, "%Y%m%d").date()
    out: list[tuple[str, str]] = []
    cur = date(s.year, s.month, 1)
    while cur <= e:
        if cur.month == 12:
            nxt = date(cur.year + 1, 1, 1)
        else:
            nxt = date(cur.year, cur.month + 1, 1)
        month_end = min(date(nxt.year, nxt.month, 1).toordinal() - 1, e.toordinal())
        month_end_d = date.fromordinal(month_end)
        month_start_d = max(cur, s)
        out.append((month_start_d.strftime("%Y%m%d"),
                    month_end_d.strftime("%Y%m%d")))
        cur = nxt
    return out


def collect_range(service_key: str, kind: str, start: str, end: str,
                  num_rows: int, out_dir: Path, sleep_sec: float = 0.2) -> tuple[Path, int]:
    endpoint = ENDPOINT_BY_KIND[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"narajangteo_{kind}_{start}_{end}_{stamp}.jsonl"

    first = fetch_page(service_key, endpoint, start, end, 1, num_rows)
    items, total = extract_items(first)
    if total == 0:
        out_path.write_text("", encoding="utf-8")
        return out_path, 0

    total_pages = (total + num_rows - 1) // num_rows
    written = 0
    with out_path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            written += 1
        for page in range(2, total_pages + 1):
            time.sleep(sleep_sec)
            payload = fetch_page(service_key, endpoint, start, end, page, num_rows)
            page_items, _ = extract_items(payload)
            for it in page_items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
                written += 1
    return out_path, written


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True, help="수집 시작일 YYYYMMDD")
    p.add_argument("--end", required=True, help="수집 종료일 YYYYMMDD")
    p.add_argument("--kind", choices=list(ENDPOINT_BY_KIND), default="용역")
    p.add_argument("--rows", type=int, default=500, help="페이지당 건수(최대 999)")
    p.add_argument("--out", default="data/raw/narajangteo", help="저장 디렉토리")
    p.add_argument("--sleep", type=float, default=0.2, help="요청 간 대기(초)")
    p.add_argument("--split", choices=["none", "monthly"], default="none",
                   help="수집 분할 방식")
    return p.parse_args()


def main() -> int:
    load_dotenv()
    key = os.getenv("NARAJANGTEO_SERVICE_KEY", "").strip()
    if not key or key.startswith("your_"):
        print("[ERROR] NARAJANGTEO_SERVICE_KEY 미설정. .env 확인.", file=sys.stderr)
        return 2

    args = parse_args()
    out_dir = Path(args.out)

    if args.split == "monthly":
        ranges = month_ranges(args.start, args.end)
        total_written = 0
        print(f"[INFO] 월별 분할 수집: {len(ranges)}개월 ({args.start}~{args.end})")
        for s, e in tqdm(ranges, desc="months"):
            try:
                path, n = collect_range(key, args.kind, s, e, args.rows,
                                        out_dir, sleep_sec=args.sleep)
                total_written += n
                tqdm.write(f"  {s}~{e}: {n}건 → {path.name}")
            except Exception as exc:
                tqdm.write(f"  [ERR] {s}~{e}: {exc}")
            time.sleep(args.sleep)
        print(f"[DONE] 총 {total_written}건 저장")
    else:
        path, n = collect_range(key, args.kind, args.start, args.end, args.rows,
                                out_dir, sleep_sec=args.sleep)
        print(f"[DONE] {n}건 저장 → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
