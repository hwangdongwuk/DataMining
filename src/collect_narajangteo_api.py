"""나라장터 입찰공고정보서비스 OpenAPI 수집기.

사용법:
    python src/collect_narajangteo_api.py \\
        --start 20240101 --end 20241231 \\
        --kind 용역 --rows 100 --out data/raw/narajangteo

환경변수:
    NARAJANGTEO_SERVICE_KEY  (.env 또는 export)
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

BASE_URL = "https://apis.data.go.kr/1230000/BidPublicInfoService05"
ENDPOINT_BY_KIND = {
    "용역": "/getBidPblancListInfoServcPPSSrch",
    "물품": "/getBidPblancListInfoThngPPSSrch",
    "공사": "/getBidPblancListInfoCnstwkPPSSrch",
}


def fetch_page(service_key: str, endpoint: str, start: str, end: str,
               page_no: int, num_rows: int, timeout: int = 30) -> dict:
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
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def extract_items(payload: dict) -> tuple[list[dict], int]:
    body = payload.get("response", {}).get("body", {})
    items = body.get("items", []) or []
    if isinstance(items, dict):
        items = items.get("item", [])
    total = int(body.get("totalCount", 0))
    return items, total


def collect(service_key: str, kind: str, start: str, end: str,
            num_rows: int, out_dir: Path, sleep_sec: float = 0.2) -> Path:
    endpoint = ENDPOINT_BY_KIND[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"narajangteo_{kind}_{start}_{end}_{stamp}.jsonl"

    first = fetch_page(service_key, endpoint, start, end, 1, num_rows)
    items, total = extract_items(first)
    if total == 0:
        print(f"[WARN] totalCount=0. 응답 확인: {json.dumps(first)[:400]}")
        return out_path

    total_pages = (total + num_rows - 1) // num_rows
    print(f"[INFO] 총 {total}건, {total_pages}페이지 수집 시작 → {out_path}")

    written = 0
    with out_path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
            written += 1
        for page in tqdm(range(2, total_pages + 1), desc="pages"):
            time.sleep(sleep_sec)
            payload = fetch_page(service_key, endpoint, start, end, page, num_rows)
            page_items, _ = extract_items(payload)
            for it in page_items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
                written += 1

    print(f"[DONE] {written}건 저장 → {out_path}")
    return out_path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--start", required=True, help="수집 시작일 YYYYMMDD")
    p.add_argument("--end", required=True, help="수집 종료일 YYYYMMDD")
    p.add_argument("--kind", choices=list(ENDPOINT_BY_KIND), default="용역")
    p.add_argument("--rows", type=int, default=100, help="페이지당 건수(최대 999)")
    p.add_argument("--out", default="data/raw/narajangteo", help="저장 디렉토리")
    p.add_argument("--sleep", type=float, default=0.2, help="요청 간 대기(초)")
    return p.parse_args()


def main() -> int:
    load_dotenv()
    key = os.getenv("NARAJANGTEO_SERVICE_KEY", "").strip()
    if not key or key.startswith("your_"):
        print("[ERROR] NARAJANGTEO_SERVICE_KEY 미설정. .env 파일을 확인하세요.", file=sys.stderr)
        return 2

    args = parse_args()
    collect(
        service_key=key,
        kind=args.kind,
        start=args.start,
        end=args.end,
        num_rows=args.rows,
        out_dir=Path(args.out),
        sleep_sec=args.sleep,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
