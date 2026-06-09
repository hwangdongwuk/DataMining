"""RFP 전처리: 메타 정제 + PDF/HWP 본문 추출 + 형태소 분석.

입력:
    data/raw/narajangteo/*.jsonl   - API 메타
    data/raw/rfp_files/{bidno}/*   - 첨부 PDF/HWP

출력:
    data/processed/rfp_meta.csv     - 정제된 메타 테이블
    data/processed/rfp_text.csv     - bidno, source, text
    data/processed/rfp_tokens.csv   - bidno, nouns (공백 구분)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import pandas as pd
from tqdm import tqdm

INDUSTRY_KEYWORDS = {
    "보험": ["보험", "생명", "손해", "공제", "재보험", "보험사"],
    "금융": ["은행", "금융", "증권", "카드", "캐피탈", "자산운용", "저축",
             "금감원", "예금보험", "신용정보"],
    "IT": ["정보시스템", "소프트웨어", "플랫폼", "클라우드", "데이터",
           "AI", "인공지능", "빅데이터", "디지털", "ERP", "BPR", "ISP",
           "PI", "POC", "PMO", "시스템", "웹", "모바일", "앱"],
}

CONSULTING_TYPES = {
    "ISP": ["ISP", "정보화전략계획", "정보전략계획"],
    "PI": ["PI", "프로세스 혁신", "프로세스혁신"],
    "POC": ["POC", "PoC", "개념검증", "실증"],
    "BPR": ["BPR", "업무재설계", "업무 재설계", "업무 프로세스 재설계"],
    "PMO": ["PMO", "사업관리"],
    "구축": ["구축", "개발", "시스템 구축", "시스템구축"],
}

# AI 순수성 분류 — KAIB2026(ETRI·국가AI전략위 기반) 방법론 참조
# https://hollobit.github.io/KAIB2026  (policy: ai-pure vs non-ai)
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


def tag_ai_class(title: str) -> tuple[str, str]:
    t = (title or "").upper()
    for kw in AI_KEYWORDS:
        if kw.upper() in t:
            return "ai-pure", ""
    for reason, kws in NON_AI_REASONS:
        if any(kw.upper() in t for kw in kws):
            return "non-ai", reason
    return "non-ai", "AI 키워드 미검출"

META_COLUMNS = [
    "bidNtceNo", "bidNtceOrd", "bidNtceNm", "bidNtceDt",
    "ntceInsttNm", "dminsttNm", "bidMethdNm", "cntrctCnclsMthdNm",
    "bidBeginDt", "bidClseDt", "opengDt",
    "presmptPrce", "bssamt", "rsrvtnPrceRngBgnRate", "rsrvtnPrceRngEndRate",
    "ntceKindNm", "rgstTyNm", "ntceInsttCd",
]


def tag_industry(title: str) -> str:
    t = (title or "").replace(" ", "")
    for ind, kws in INDUSTRY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return ind
    return "기타"


def tag_consulting(title: str) -> str:
    t = (title or "").upper().replace(" ", "")
    for typ, kws in CONSULTING_TYPES.items():
        for kw in kws:
            if kw.upper().replace(" ", "") in t:
                return typ
    return "기타"


def load_meta(in_dir: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for fp in sorted(in_dir.glob("narajangteo_*.jsonl")):
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
        return pd.DataFrame(columns=META_COLUMNS)
    df = pd.DataFrame(rows)
    for col in META_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df.drop_duplicates(subset=["bidNtceNo", "bidNtceOrd"])
    df["bidNtceDt_dt"] = pd.to_datetime(df["bidNtceDt"], errors="coerce")
    df["year"] = df["bidNtceDt_dt"].dt.year
    df["year_month"] = df["bidNtceDt_dt"].dt.to_period("M").astype(str)
    for col in ["presmptPrce", "bssamt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # 반복숫자 sentinel(10조 초과) 이상치 제거
        df.loc[df[col] > 1e13, col] = pd.NA
    df["industry"] = df["bidNtceNm"].apply(tag_industry)
    df["consulting_type"] = df["bidNtceNm"].apply(tag_consulting)
    ai = df["bidNtceNm"].apply(tag_ai_class)
    df["ai_class"] = ai.apply(lambda x: x[0])
    df["non_ai_reason"] = ai.apply(lambda x: x[1])
    return df


def extract_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            parts = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(parts)
    except Exception as e:
        return f"[PDF_ERR] {e}"


import shutil
_HWP5TXT = shutil.which("hwp5txt") or str(
    Path(__file__).resolve().parent.parent / ".venv/bin/hwp5txt")


def extract_hwp(path: Path) -> str:
    if not Path(_HWP5TXT).exists():
        return f"[HWP_ERR] hwp5txt binary not found at {_HWP5TXT}"
    try:
        r = subprocess.run(
            [_HWP5TXT, str(path)],
            capture_output=True, timeout=60,
        )
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="ignore")
        err = r.stderr.decode("utf-8", errors="ignore")[:200]
        return f"[HWP_ERR] {err}"
    except Exception as e:
        return f"[HWP_ERR] {e}"


def extract_texts(rfp_root: Path, bidnos: set[str]) -> pd.DataFrame:
    rows = []
    for sub in tqdm(sorted([p for p in rfp_root.iterdir() if p.is_dir()]),
                    desc="extract"):
        bidno = sub.name
        if bidnos and bidno not in bidnos:
            continue
        for f in sub.iterdir():
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext == ".pdf":
                text = extract_pdf(f)
                src = "pdf"
            elif ext in {".hwp", ".hwpx"}:
                text = extract_hwp(f)
                src = "hwp"
            else:
                continue
            rows.append({"bidNtceNo": bidno, "filename": f.name,
                         "source": src, "text": text})
    return pd.DataFrame(rows)


def tokenize_texts(df_text: pd.DataFrame) -> pd.DataFrame:
    try:
        from kiwipiepy import Kiwi
    except ImportError:
        print("[WARN] kiwipiepy 미설치 — 토큰화 생략")
        return pd.DataFrame(columns=["bidNtceNo", "nouns"])
    kiwi = Kiwi()
    out = []
    for bidno, grp in tqdm(df_text.groupby("bidNtceNo"), desc="tokenize"):
        txt = "\n".join(t for t in grp["text"] if isinstance(t, str)
                        and not t.startswith("["))
        txt = re.sub(r"\s+", " ", txt)[:50_000]
        if not txt:
            continue
        tokens = kiwi.tokenize(txt)
        nouns = [t.form for t in tokens if t.tag.startswith("NN")
                 and len(t.form) >= 2]
        out.append({"bidNtceNo": bidno, "nouns": " ".join(nouns)})
    return pd.DataFrame(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-meta", default="data/raw/narajangteo")
    p.add_argument("--raw-files", default="data/raw/rfp_files")
    p.add_argument("--out", default="data/processed")
    p.add_argument("--skip-text", action="store_true",
                   help="본문 추출·토큰화 건너뛰기 (메타만)")
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[1/3] 메타 로딩 & 태깅")
    df_meta = load_meta(Path(args.raw_meta))
    meta_path = out_dir / "rfp_meta.csv"
    df_meta.to_csv(meta_path, index=False, encoding="utf-8-sig")
    print(f"  → {len(df_meta):,}건 · {meta_path}")

    if args.skip_text or not Path(args.raw_files).exists():
        print("[SKIP] 본문 추출 생략")
        return 0

    print("[2/3] PDF/HWP 본문 추출")
    bidnos = set(df_meta["bidNtceNo"].dropna().astype(str))
    df_text = extract_texts(Path(args.raw_files), bidnos)
    text_path = out_dir / "rfp_text.csv"
    df_text.to_csv(text_path, index=False, encoding="utf-8-sig")
    print(f"  → {len(df_text):,}건 · {text_path}")

    print("[3/3] 형태소 분석(명사 추출)")
    df_tok = tokenize_texts(df_text)
    tok_path = out_dir / "rfp_tokens.csv"
    df_tok.to_csv(tok_path, index=False, encoding="utf-8-sig")
    print(f"  → {len(df_tok):,}건 · {tok_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
