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

# 수요기관(dminsttNm) 기반 산업 분류 — 최대 10개 범주, 우선순위 순.
# 도메인 특화 기관을 먼저 매칭하고, 일반 연구원/대학은 '교육·연구'로,
# 미매칭은 '행정·공공'으로 귀속 → '기타' 최소화.
INSTITUTION_SECTOR = [
    ("금융", ["거래소", "은행", "증권", "카드", "캐피탈", "자산운용", "저축",
              "금융", "예금보험", "신용정보", "신용보증", "기술보증", "예탁결제",
              "조폐", "코스콤", "금융결제", "서민금융", "무역보험", "주택금융",
              "새마을금고", "수출입"]),
    ("보험", ["보험", "공제"]),
    ("의료·보건", ["병원", "의료원", "질병관리", "보건", "건강보험", "심사평가",
                  "적십자", "암센터", "치과", "한의", "의료", "혈액"]),
    ("문화·관광·체육", ["문화", "관광", "박물관", "미술관", "도서관", "예술",
                       "콘텐츠", "체육", "스포츠", "문화재", "방송", "영상",
                       "공연", "국악", "문화원"]),
    ("농림·수산·환경", ["농촌", "농업", "산림", "수산", "해양", "환경", "기상",
                       "축산", "임업", "농어촌", "생태", "식품", "검역", "농수산"]),
    ("국토·교통·건설", ["국토", "교통", "철도", "도로", "공항", "항만", "수자원",
                       "토지주택", "코레일", "건설", "항공", "해운", "물류",
                       "도시공사", "시설안전", "도시철도"]),
    ("산업·에너지", ["전력", "한전", "가스", "석유", "에너지", "발전", "산업단지",
                    "무역협회", "코트라", "산업기술", "중소벤처", "특허", "원자력",
                    "광물", "전기안전", "신재생", "산업진흥", "디자인진흥",
                    "생산기술", "세라믹", "기계연구", "화학연구", "전자부품"]),
    ("정보·통신", ["정보화", "정보통신", "지능정보", "지역정보", "전파",
                  "방송통신", "인터넷진흥", "정보보호", "소프트웨어진흥",
                  "정보사회", "전산"]),
    ("교육·연구", ["대학교", "대학", "과학기술원", "교육청", "교육지원청",
                  "학교", "교육원", "폴리텍", "장학", "평생교육", "직업능력",
                  "학술", "연구원", "연구소", "개발원", "진흥원", "학회",
                  "한국학", "교육개발"]),
    ("행정·공공", ["특별시", "광역시", "특별자치", "도청", "시청", "군청", "구청",
                  "정부", "부", "청", "처", "위원회", "공단", "공사", "재단",
                  "협회", "조합", "센터", "사업소", "의회", "경찰", "소방",
                  "국방", "군", "우정", "연금", "근로복지", "공공"]),
]
INDUSTRY_DEFAULT = "행정·공공"
# 제목 기반 보조 신호(기관 미상 시)
INDUSTRY_KEYWORDS = {
    "보험": ["보험", "생명", "손해", "공제"],
    "금융": ["은행", "금융", "증권", "카드", "거래소"],
}

# IT 사업유형 — 우선순위 순(특화 유형 먼저). 첫 매칭 채택 → '기타' 최소화.
CONSULTING_TYPES = {
    "감리": ["감리"],
    "보안": ["보안", "정보보호", "취약점", "침해", "모의해킹", "관제", "ISMS",
            "무인경비", "CCTV", "출입통제"],
    "임차/구독": ["임차", "렌탈", "대여", "라이선스", "라이센스", "사용권",
                "구독", "SaaS", "리스", "사용료"],
    "ISP/계획": ["ISP", "ISMP", "정보화전략", "정보전략", "정보화계획",
                "마스터플랜", "중장기계획", "정보화전략계획"],
    "BPR/PI": ["BPR", "PI", "업무재설계", "프로세스혁신", "프로세스 혁신"],
    "PMO": ["PMO", "사업관리", "통합사업관리"],
    "POC/실증": ["POC", "PoC", "개념검증", "실증", "시범"],
    "고도화/개선": ["고도화", "개선", "업그레이드", "재구축", "기능개선", "개량"],
    "유지보수/운영": ["유지보수", "유지관리", "운영", "위탁운영", "헬프데스크",
                    "운용", "상면", "유지", "점검", "정비"],
    "데이터/AI": ["데이터구축", "DB구축", "학습데이터", "라벨링", "마이그레이션",
                 "데이터이행", "데이터정제"],
    "컨설팅/분석": ["컨설팅", "진단", "분석", "평가", "수립", "타당성"],
    "구축/개발": ["구축", "개발", "시스템구축", "도입", "신규개발", "설치", "제작"],
    "시험/인증": ["시험", "인증", "검증", "시뮬레이션", "성능평가", "TTA"],
    "연구개발/R&D": ["연구개발", "R&D", "실증연구", "기술개발", "조사연구",
                    "연구", "조사"],
    "교육/홍보": ["교육", "홍보", "캠페인", "교재", "콘텐츠제작", "안내"],
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
    raw = title or ""
    nospace = raw.upper().replace(" ", "")
    if any(_kw_in(kw, raw, nospace) for kw in AI_KEYWORDS):
        return "ai-pure", ""
    for reason, kws in NON_AI_REASONS:
        if any(_kw_in(kw, raw, nospace) for kw in kws):
            return "non-ai", reason
    return "non-ai", "AI 키워드 미검출"

META_COLUMNS = [
    "bidNtceNo", "bidNtceOrd", "bidNtceNm", "bidNtceDt",
    "ntceInsttNm", "dminsttNm", "bidMethdNm", "cntrctCnclsMthdNm",
    "bidBeginDt", "bidClseDt", "opengDt",
    "presmptPrce", "bssamt", "rsrvtnPrceRngBgnRate", "rsrvtnPrceRngEndRate",
    "ntceKindNm", "rgstTyNm", "ntceInsttCd",
]


_BOUNDARY_CACHE: dict[str, "re.Pattern"] = {}


def _kw_in(kw: str, raw: str, nospace: str) -> bool:
    """영문 토큰(AI/IT/SW/PI/ISP 등)은 단어경계 매칭으로 오탐 방지
    (air/fair/brain, API 속 PI 등), 한글 포함 키워드는 부분일치."""
    if kw.isascii() and kw.isalpha():
        rx = _BOUNDARY_CACHE.get(kw)
        if rx is None:
            rx = re.compile(r"(?<![A-Za-z])" + re.escape(kw) + r"(?![A-Za-z])",
                            re.IGNORECASE)
            _BOUNDARY_CACHE[kw] = rx
        return rx.search(raw) is not None
    return kw.upper().replace(" ", "") in nospace


def tag_industry(title: str, institution: str = "") -> str:
    inst = institution or ""
    for sector, kws in INSTITUTION_SECTOR:
        if any(kw in inst for kw in kws):
            return sector
    # 기관 미상 시 제목 기반 보조 분류
    raw = title or ""
    nospace = raw.upper().replace(" ", "")
    for ind, kws in INDUSTRY_KEYWORDS.items():
        if any(_kw_in(kw, raw, nospace) for kw in kws):
            return ind
    return INDUSTRY_DEFAULT


def tag_consulting(title: str) -> str:
    raw = title or ""
    nospace = raw.upper().replace(" ", "")
    for typ, kws in CONSULTING_TYPES.items():
        if any(_kw_in(kw, raw, nospace) for kw in kws):
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
    # 논리적 중복 제거: 같은 기관이 같은 제목·추정가로 재공고한 건 (최신 1건 유지).
    # 서로 다른 기관의 동일 제목은 보존.
    before = len(df)
    df = (df.sort_values("bidNtceDt_dt")
            .drop_duplicates(subset=["bidNtceNm", "dminsttNm", "presmptPrce"],
                             keep="last"))
    print(f"  중복 제거(제목+기관+추정가): {before:,} → {len(df):,}")
    df["industry"] = df.apply(
        lambda r: tag_industry(r["bidNtceNm"], r["dminsttNm"]), axis=1)
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
