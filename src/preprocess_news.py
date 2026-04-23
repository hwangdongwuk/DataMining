"""네이버 뉴스 전처리: 정제 + 태깅.

입력: data/raw/naver_news/*.jsonl
출력: data/processed/news_meta.csv, data/processed/news_daily.csv
"""
from __future__ import annotations

import json
import re
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd

IN_DIR = Path("data/raw/naver_news")
OUT_DIR = Path("data/processed")

CONSULTING_TYPES = {
    "ISP": ["ISP", "정보화전략계획", "정보전략계획"],
    "PI": [" PI ", "프로세스 혁신", "프로세스혁신"],
    "POC": ["POC", "PoC", "개념검증", "실증"],
    "BPR": ["BPR", "업무재설계", "업무 재설계"],
    "PMO": ["PMO", "사업관리"],
}
INDUSTRY = {
    "보험": ["보험", "생명", "손해", "공제"],
    "금융": ["은행", "금융", "증권", "카드", "금감원", "예금보험", "마이데이터"],
    "IT": ["정보시스템", "소프트웨어", "플랫폼", "클라우드", "AI",
           "인공지능", "빅데이터", "디지털", "ERP", "BPR", "ISP",
           "핀테크", "FDS"],
}


def clean_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return (s.replace("&quot;", '"').replace("&amp;", "&")
             .replace("&lt;", "<").replace("&gt;", ">").strip())


def tag(text: str, rules: dict[str, list[str]]) -> str:
    t = (text or "").replace(" ", "").upper()
    for k, kws in rules.items():
        for kw in kws:
            if kw.upper().replace(" ", "") in t:
                return k
    return "기타"


def main() -> int:
    rows: list[dict] = []
    for fp in sorted(IN_DIR.glob("*.jsonl")):
        with fp.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    if not rows:
        print("[WARN] no news data"); return 1

    df = pd.DataFrame(rows)
    df["title_clean"] = df["title"].apply(clean_html)
    df["desc_clean"] = df["description"].apply(clean_html)
    df["pubdate_dt"] = df["pubDate"].apply(
        lambda s: parsedate_to_datetime(s) if isinstance(s, str) else None)
    df["pubdate_date"] = pd.to_datetime(df["pubdate_dt"]).dt.date
    df["pubdate_ym"] = pd.to_datetime(df["pubdate_dt"]).dt.to_period("M").astype(str)

    full_text = df["title_clean"] + " " + df["desc_clean"]
    df["industry"] = full_text.apply(lambda t: tag(t, INDUSTRY))
    df["consulting_type"] = full_text.apply(lambda t: tag(t, CONSULTING_TYPES))

    df = df.drop_duplicates(subset=["title_clean", "link"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = OUT_DIR / "news_meta.csv"
    cols = ["_query", "title_clean", "desc_clean", "link", "originallink",
            "pubdate_dt", "pubdate_date", "pubdate_ym",
            "industry", "consulting_type"]
    df[cols].to_csv(meta_path, index=False, encoding="utf-8-sig")
    print(f"[1/2] {len(df):,}건 → {meta_path}")

    daily = (df.groupby(["pubdate_date", "industry", "consulting_type"])
               .size().reset_index(name="count"))
    daily_path = OUT_DIR / "news_daily.csv"
    daily.to_csv(daily_path, index=False, encoding="utf-8-sig")
    print(f"[2/2] 일자·산업·유형별 집계 → {daily_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
