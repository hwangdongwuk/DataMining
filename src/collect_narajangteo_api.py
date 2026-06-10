"""나라장터 입찰공고정보서비스 OpenAPI 수집기 (월별 분할 + IT 색인 필터).

업무구분별 공고명(bidNtceNm) 기준으로 IT 프로젝트성 공고만 색인 수집한다.
    - 물품: 공고명에 "시스템" 포함 건만 (단순 물품 제외)
    - 용역: 시스템·개발·IT 등 대표 키워드 포함 건만
    - 공사·외자: 수집 제외

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
import re
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
}

NAME_FIELD = "bidNtceNm"  # 입찰공고명

# 업무구분별 IT 프로젝트 색인 키워드 (공고명 부분일치, 대소문자 무시)
# "개발"은 다의어(콘텐츠/교육/신약/도시개발 등)라 단독 제외 → IT 맥락 복합어만 포함
IT_KEYWORDS_BY_KIND = {
    "물품": ["시스템"],
    "용역": [
        # 강한 IT 신호
        "시스템", "정보시스템", "소프트웨어", "SW", "S/W", "플랫폼",
        "빅데이터", "데이터베이스", "DB구축", "데이터", "AI", "인공지능",
        "클라우드", "ICT", "정보화", "전산", "정보통신", "홈페이지",
        "웹사이트", "애플리케이션", "어플리케이션", "모바일앱", "챗봇",
        "사물인터넷", "IoT", "지능형", "스마트시티",
        # IT 맥락 '개발' 복합어
        "시스템개발", "SW개발", "소프트웨어개발", "웹개발", "앱개발",
        "응용개발", "프로그램개발", "플랫폼개발", "모바일개발",
        "홈페이지개발", "웹사이트개발", "고도화",
    ],
}

# 단독 영문 IT 토큰 (부분일치 오탐 방지용 별도 처리)
_IT_TOKEN_RE = re.compile(r"\bIT\b", re.IGNORECASE)


def matched_keywords(name: str, kind: str) -> list[str]:
    upper = name.upper()
    hits = [kw for kw in IT_KEYWORDS_BY_KIND.get(kind, []) if kw.upper() in upper]
    if kind == "용역" and _IT_TOKEN_RE.search(name or ""):
        hits.append("IT")
    return hits


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
                  num_rows: int, out_dir: Path,
                  sleep_sec: float = 0.2) -> tuple[Path, int, int]:
    endpoint = ENDPOINT_BY_KIND[kind]
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"narajangteo_{kind}_{start}_{end}_{stamp}.jsonl"

    first = fetch_page(service_key, endpoint, start, end, 1, num_rows)
    items, total = extract_items(first)
    if total == 0:
        out_path.write_text("", encoding="utf-8")
        return out_path, 0, 0

    total_pages = (total + num_rows - 1) // num_rows
    written = 0
    fetched = 0
    with out_path.open("w", encoding="utf-8") as f:
        def dump(page_items: list[dict]) -> None:
            nonlocal written, fetched
            for it in page_items:
                fetched += 1
                kws = matched_keywords(str(it.get(NAME_FIELD, "") or ""), kind)
                if not kws:
                    continue
                it["itMatchKeywords"] = kws
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
                written += 1

        dump(items)
        for page in range(2, total_pages + 1):
            time.sleep(sleep_sec)
            payload = fetch_page(service_key, endpoint, start, end, page, num_rows)
            page_items, _ = extract_items(payload)
            dump(page_items)
    return out_path, written, fetched


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
        total_fetched = 0
        print(f"[INFO] 월별 분할 수집: {len(ranges)}개월 ({args.start}~{args.end}) "
              f"| 업무구분={args.kind} 색인키워드={IT_KEYWORDS_BY_KIND.get(args.kind)}")
        for s, e in tqdm(ranges, desc="months"):
            try:
                path, n, fetched = collect_range(key, args.kind, s, e, args.rows,
                                                 out_dir, sleep_sec=args.sleep)
                total_written += n
                total_fetched += fetched
                tqdm.write(f"  {s}~{e}: 색인 {n}/{fetched}건 → {path.name}")
            except Exception as exc:
                tqdm.write(f"  [ERR] {s}~{e}: {exc}")
            time.sleep(args.sleep)
        kept = (total_written / total_fetched * 100) if total_fetched else 0
        print(f"[DONE] 색인 {total_written}/{total_fetched}건 저장 ({kept:.1f}%)")
    else:
        path, n, fetched = collect_range(key, args.kind, args.start, args.end,
                                         args.rows, out_dir, sleep_sec=args.sleep)
        kept = (n / fetched * 100) if fetched else 0
        print(f"[DONE] 색인 {n}/{fetched}건 저장 ({kept:.1f}%) → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
