"""Streamlit 대시보드: 공공 RFP Pain Point 허브.

실행:
    streamlit run src/app_streamlit.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import kaib_pages as kp

DATA_DIR = Path("data/processed")
META_PATH = DATA_DIR / "rfp_meta.csv"
TEXT_PATH = DATA_DIR / "rfp_text.csv"
TOKENS_PATH = DATA_DIR / "rfp_tokens.csv"
NEWS_PATH = DATA_DIR / "news_meta.csv"

# ── 색인/정제에 사용한 키워드 (파이프라인과 동기화) ──
IT_INDEX_KEYWORDS = [
    "시스템", "정보시스템", "소프트웨어", "SW", "S/W", "플랫폼", "빅데이터",
    "데이터베이스", "DB구축", "데이터", "AI", "인공지능", "클라우드", "ICT",
    "정보화", "전산", "정보통신", "홈페이지", "웹사이트", "애플리케이션",
    "어플리케이션", "모바일앱", "챗봇", "사물인터넷", "IoT", "지능형",
    "스마트시티", "시스템개발", "SW개발", "소프트웨어개발", "웹개발", "앱개발",
    "응용개발", "프로그램개발", "플랫폼개발", "모바일개발", "홈페이지개발",
    "웹사이트개발", "고도화", "IT",
]
EXCLUDED_DEV_KEYWORDS = ["콘텐츠개발", "캐릭터개발", "교육과정개발", "역량개발",
                         "경력개발", "신약개발", "관광·단지개발", "디자인개발"]
AI_PURE_KEYWORDS = [
    "AI", "AX", "인공지능", "생성형", "생성AI", "LLM", "초거대", "딥러닝",
    "머신러닝", "자연어", "GPT", "언어모델", "AI안전", "AI보안", "에이전트",
    "Agent", "휴머노이드", "로봇", "GPU", "온디바이스", "빅데이터", "데이터",
    "클라우드",
]
STOPWORDS = {"용역", "사업", "구매", "재공고", "공고", "입찰", "년도", "관련",
             "위한", "대한", "기타", "외", "및", "년", "차", "제",
             "학년도", "연도", "차년도", "금년", "당해", "해당", "금년도",
             "상반기", "하반기", "분기", "월", "일", "신규", "기존"}


@st.cache_data
def load_meta() -> pd.DataFrame:
    if not META_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(META_PATH)
    if "bidNtceDt_dt" in df.columns:
        df["bidNtceDt_dt"] = pd.to_datetime(df["bidNtceDt_dt"], errors="coerce")
    return df


@st.cache_data
def load_tokens() -> pd.DataFrame:
    if not TOKENS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(TOKENS_PATH)


@st.cache_data
def load_news() -> pd.DataFrame:
    if not NEWS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(NEWS_PATH, low_memory=False)


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("필터")
    if df.empty:
        return df
    years = sorted(df["year"].dropna().unique().astype(int).tolist())
    ys = st.sidebar.multiselect("연도", years, default=years)
    industries = sorted(df["industry"].dropna().unique().tolist())
    is_ = st.sidebar.multiselect("산업", industries, default=industries)
    types = sorted(df["consulting_type"].dropna().unique().tolist())
    ts = st.sidebar.multiselect("컨설팅 유형", types, default=types)
    kw = st.sidebar.text_input("공고명 키워드 (부분 일치)", "")

    f = df[df["year"].isin(ys) & df["industry"].isin(is_)
           & df["consulting_type"].isin(ts)]
    if kw:
        f = f[f["bidNtceNm"].str.contains(kw, na=False)]
    return f


def page_overview(df: pd.DataFrame) -> None:
    st.subheader("① 수집 개요")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("공고 수", f"{len(df):,}")
    c2.metric("수요기관 수", f"{df['dminsttNm'].nunique():,}")
    c3.metric("평균 예산(원)", f"{df['presmptPrce'].mean():,.0f}")
    c4.metric("기간", f"{df['year_month'].min()}~{df['year_month'].max()}"
              if len(df) else "-")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**연도별 공고 건수**")
        yr = df.groupby("year").size().reset_index(name="count")
        fig = px.bar(yr, x="year", y="count")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("**산업 × 컨설팅 유형 교차**")
        ct = (df.groupby(["industry", "consulting_type"]).size()
                .reset_index(name="count"))
        fig = px.density_heatmap(ct, x="consulting_type", y="industry",
                                 z="count", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)


def page_timeline(df: pd.DataFrame) -> None:
    st.subheader("② 월별 추이")
    if df.empty:
        st.info("데이터 없음")
        return
    ts = df.groupby(["year_month", "industry"]).size().reset_index(name="count")
    fig = px.line(ts, x="year_month", y="count", color="industry", markers=True)
    st.plotly_chart(fig, use_container_width=True)


def page_keywords(df: pd.DataFrame, df_tok: pd.DataFrame) -> None:
    st.subheader("③ 색인 기준 & 공고명 키워드")

    with st.expander("📌 데이터 수집·정제에 사용한 키워드 (클릭)", expanded=True):
        st.markdown("**① 수집(색인) 키워드 — 업무구분 '용역' 중 아래 IT 맥락 "
                    "키워드가 공고명에 포함된 건만 수집** *(공사·외자 제외)*")
        st.code(" · ".join(IT_INDEX_KEYWORDS), language=None)
        st.markdown("**② 제외(정제) — 단독 '개발'은 다의어라 제외**, 아래처럼 "
                    "IT 비연관 '개발' 건을 배제:")
        st.code(" · ".join(EXCLUDED_DEV_KEYWORDS), language=None)
        st.markdown("**③ AI 순수성(ai-pure) 판정 키워드** *(KAIB2026/ETRI 기준)*")
        st.code(" · ".join(AI_PURE_KEYWORDS), language=None)

    st.markdown("**공고명 상위 키워드 (필터 적용 결과 기준)**")
    if df.empty:
        st.info("데이터 없음")
        return
    import re as _re
    tokens: list[str] = []
    for nm in df["bidNtceNm"].dropna().astype(str):
        for tok in _re.split(r"[\s\(\)\[\]·,/]+", nm):
            tok = tok.strip()
            if (len(tok) >= 2 and tok not in STOPWORDS
                    and not _re.search(r"\d", tok)          # 연도·숫자 포함 토큰 제외
                    and not tok.endswith("년도")
                    and not tok.endswith("년차")
                    and not tok.endswith("년")):
                tokens.append(tok)
    if not tokens:
        st.info("키워드 없음")
        return
    freq = pd.Series(tokens).value_counts().head(30)
    st.bar_chart(freq)


def page_ai(df: pd.DataFrame, news: pd.DataFrame) -> None:
    st.subheader("⑤ AI 순수성 분석 (KAIB2026 기준)")
    st.caption("공고명 AI 키워드 기반 ai-pure / non-ai 분류 · "
               "참조: ETRI KAIB2026 (hollobit.github.io/KAIB2026)")
    if df.empty or "ai_class" not in df.columns:
        st.info("ai_class 데이터 없음 — 전처리를 재실행하세요.")
        return

    c1, c2, c3 = st.columns(3)
    pure = int((df["ai_class"] == "ai-pure").sum())
    c1.metric("ai-pure 공고", f"{pure:,}")
    c2.metric("ai-pure 비중", f"{pure / len(df) * 100:.1f}%")
    c3.metric("non-ai 공고", f"{len(df) - pure:,}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**ai-pure vs non-ai**")
        vc = df["ai_class"].value_counts().reset_index()
        vc.columns = ["ai_class", "count"]
        st.plotly_chart(px.pie(vc, names="ai_class", values="count",
                               hole=0.4), use_container_width=True)
    with col2:
        st.markdown("**non-ai 사유 분포**")
        if "non_ai_reason" in df.columns:
            rs = (df[df["ai_class"] == "non-ai"]["non_ai_reason"]
                  .value_counts().reset_index())
            rs.columns = ["reason", "count"]
            st.plotly_chart(px.bar(rs, x="count", y="reason",
                                   orientation="h"), use_container_width=True)

    st.markdown("**월별 ai-pure 비중 추이**")
    g = (df.assign(is_pure=df["ai_class"].eq("ai-pure"))
           .groupby("year_month")["is_pure"].mean().mul(100)
           .reset_index(name="ai_pure_pct"))
    st.plotly_chart(px.line(g, x="year_month", y="ai_pure_pct", markers=True),
                    use_container_width=True)

    st.divider()
    st.markdown("### 🔑 핵심 인사이트 — 담론(뉴스) ↔ 발주(RFP) 격차")
    if not news.empty and "ai_class" in news.columns:
        it_news = news[news["it_indexed"]] if "it_indexed" in news.columns else news
        rfp_pure = df["ai_class"].eq("ai-pure").mean() * 100
        news_pure = it_news["ai_class"].eq("ai-pure").mean() * 100
        comp = pd.DataFrame({
            "소스": ["RFP (실제 발주)", "뉴스 (담론, IT 한정)"],
            "ai-pure %": [round(rfp_pure, 1), round(news_pure, 1)],
            "non-ai %": [round(100 - rfp_pure, 1), round(100 - news_pure, 1)],
        })
        st.plotly_chart(
            px.bar(comp, x="소스", y=["ai-pure %", "non-ai %"], barmode="stack",
                   text_auto=True), use_container_width=True)
        st.info(f"미디어 담론은 AI 중심({news_pure:.1f}%)이나 실제 공공 조달 발주는 "
                f"일반 정보화/SI가 대다수(non-ai {100 - rfp_pure:.1f}%) — "
                f"**'AI 관심 ↔ 조달 현실'의 정량적 격차**.")
    else:
        st.warning("news_meta.csv 미존재 — 뉴스 연계 비교 생략.")


def page_search(df: pd.DataFrame) -> None:
    st.subheader("④ 공고 검색 & 원문 URL")
    if df.empty:
        st.info("데이터 없음")
        return
    q = st.text_input("검색어", "")
    view = df if not q else df[df["bidNtceNm"].str.contains(q, na=False)]
    st.dataframe(
        view[["bidNtceNo", "bidNtceNm", "ntceInsttNm", "bidNtceDt",
              "presmptPrce", "industry", "consulting_type"]].head(200),
        use_container_width=True,
    )


def inject_style() -> None:
    st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/variable/pretendardvariable.css');
    html, body, [class*="css"], .stMarkdown, button, input, textarea, select {
        font-family:'Pretendard Variable',Pretendard,-apple-system,sans-serif !important;
        letter-spacing:-.2px;
    }
    .block-container { max-width:1380px; padding-top:1.2rem; padding-bottom:2rem; }
    #MainMenu, footer, header [data-testid="stToolbar"] { visibility:hidden; }
    .hero { background:linear-gradient(120deg,#0f172a 0%,#1e3a8a 55%,#0e7490 100%);
        border-radius:20px; padding:26px 34px; color:#fff; margin-bottom:18px;
        box-shadow:0 10px 30px rgba(30,58,138,.18); }
    .hero h1 { font-size:30px; font-weight:800; margin:0 0 6px; letter-spacing:-1px; }
    .hero p { margin:0; color:#cbd5e1; font-size:15px; }
    .hero .pills { margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
    .hero .pill { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18);
        padding:5px 13px; border-radius:999px; font-size:13px; font-weight:600; color:#e0e7ff; }
    [data-testid="stMetric"] { background:#fff; border:1px solid #e7ecf3; border-radius:14px;
        padding:14px 16px; box-shadow:0 1px 3px rgba(15,23,42,.05); }
    [data-testid="stMetricValue"] { color:#1d4ed8; font-weight:800; font-size:26px; }
    [data-testid="stMetricLabel"] { color:#64748b; font-weight:600; }
    .stTabs [data-baseweb="tab-list"] { gap:5px; border-bottom:2px solid #eef2f7; }
    .stTabs [data-baseweb="tab"] { background:#f1f5f9; border-radius:10px 10px 0 0;
        padding:9px 16px; font-weight:700; font-size:15px; color:#475569; }
    .stTabs [aria-selected="true"] { background:#2563eb !important; color:#fff !important; }
    [data-testid="stDataFrame"] { border:1px solid #e7ecf3; border-radius:12px; }
    h3, h4 { color:#0f172a; font-weight:800; letter-spacing:-.5px; }
    </style>
    """, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="공공 IT 발주 × AI 인텔리전스",
                       page_icon="📊", layout="wide")
    inject_style()
    st.markdown("""
    <div class="hero">
      <h1>📊 공공 IT 발주 인텔리전스 — 나라장터 × 정부 AI 재정계획</h1>
      <p>나라장터 IT 발주 33,860건(2023–2025) · 정부 AI 재정사업 533건(2026) 통합 분석</p>
      <div class="pills">
        <span class="pill">🗓 35개월</span>
        <span class="pill">🏛 수요기관 3,383곳</span>
        <span class="pill">🤖 AI 발주 9.0% (엄격 정의)</span>
        <span class="pill">💰 정부 AI 27조 · +24%</span>
        <span class="pill">☁ AWS 라이브</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("데이터마이닝 · 황동욱 · 2024720459 · 출처: 나라장터 OpenAPI · KAIB2026")

    df = load_meta()
    if df.empty:
        st.warning("`data/processed/rfp_meta.csv` 가 없습니다. "
                    "`python src/preprocess_rfp.py` 를 먼저 실행하세요.")
        st.stop()
    df_tok = load_tokens()
    df_news = load_news()

    df_f = sidebar_filters(df)

    top = st.tabs(["📋 IT 발주 분석 (나라장터)",
                   "🏛 정부 AI 재정계획 (KAIB2026)",
                   "⚖️ 계획 ↔ 발주 비교"])
    with top[0]:
        tabs = st.tabs(["개요", "월별 추이", "키워드", "AI 순수성", "공고 검색"])
        with tabs[0]:
            page_overview(df_f)
        with tabs[1]:
            page_timeline(df_f)
        with tabs[2]:
            page_keywords(df_f, df_tok)
        with tabs[3]:
            page_ai(df_f, df_news)
        with tabs[4]:
            page_search(df_f)
    with top[1]:
        kp.render_kaib()
    with top[2]:
        kp.render_compare(df)


if __name__ == "__main__":
    main()
