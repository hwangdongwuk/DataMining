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

# RFP와 동일한 분류축 (cross-source 연계용)
IT_INDEX_KEYWORDS = ["시스템", "개발", "IT", "정보화", "소프트웨어", "SW",
                     "플랫폼", "데이터", "AI", "인공지능"]
AI_KEYWORDS = [
    "AI", "AX", "인공지능", "파운데이션", "생성형", "생성AI", "LLM", "초거대",
    "학습데이터", "딥러닝", "머신러닝", "자연어", "GPT", "언어모델", "sLM",
    "AI안전", "AI보안", "NPU", "에이전트", "Agent", "피지컬", "휴머노이드",
    "로봇", "GPU", "온디바이스", "빅데이터", "데이터", "클라우드",
]
NON_AI_REASONS = [
    ("융자/펀드/출자", ["융자", "펀드", "출자", "모태조합", "보증"]),
    ("일반 교육/훈련", ["내일배움", "직업훈련", "장학", "대학육성", "등록금", "급식"]),
    ("시설/건축/토목", ["건축", "청사", "이전", "시설비", "임차", "리모델링", "증축", "건립"]),
    ("일반 복지/지원금", ["수당", "보조금", "바우처", "급여", "연금", "보험료", "의료비"]),
    ("일반 행정/운영", ["운영비", "인건비", "경상운영", "기본경비", "여비", "업무추진"]),
]


def is_it_indexed(text: str) -> bool:
    t = (text or "").upper()
    return any(kw.upper() in t for kw in IT_INDEX_KEYWORDS)


def tag_ai_class(text: str) -> tuple[str, str]:
    t = (text or "").upper()
    for kw in AI_KEYWORDS:
        if kw.upper() in t:
            return "ai-pure", ""
    for reason, kws in NON_AI_REASONS:
        if any(kw.upper() in t for kw in kws):
            return "non-ai", reason
    return "non-ai", "AI 키워드 미검출"


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
    df["it_indexed"] = full_text.apply(is_it_indexed)
    ai = full_text.apply(tag_ai_class)
    df["ai_class"] = ai.apply(lambda x: x[0])
    df["non_ai_reason"] = ai.apply(lambda x: x[1])

    df = df.drop_duplicates(subset=["title_clean", "link"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = OUT_DIR / "news_meta.csv"
    cols = ["_query", "title_clean", "desc_clean", "link", "originallink",
            "pubdate_dt", "pubdate_date", "pubdate_ym",
            "industry", "consulting_type", "it_indexed", "ai_class",
            "non_ai_reason"]
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
