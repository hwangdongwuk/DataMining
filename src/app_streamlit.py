"""Streamlit 대시보드: 공공 RFP Pain Point 허브.

실행:
    streamlit run src/app_streamlit.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path("data/processed")
META_PATH = DATA_DIR / "rfp_meta.csv"
TEXT_PATH = DATA_DIR / "rfp_text.csv"
TOKENS_PATH = DATA_DIR / "rfp_tokens.csv"
NEWS_PATH = DATA_DIR / "news_meta.csv"


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
    st.subheader("③ 산업별 Pain Point 키워드")
    if df_tok.empty:
        st.warning("토큰 데이터가 아직 생성되지 않았습니다. 전처리를 먼저 실행하세요.")
        return
    merged = df_tok.merge(df[["bidNtceNo", "industry", "consulting_type"]],
                          on="bidNtceNo", how="inner")
    industry = st.selectbox("산업 선택",
                             sorted(merged["industry"].dropna().unique()))
    sub = merged[merged["industry"] == industry]
    if sub.empty:
        st.info("해당 산업 데이터 없음")
        return
    all_nouns = " ".join(sub["nouns"].fillna("").tolist()).split()
    freq = pd.Series(all_nouns).value_counts().head(30)
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


def main() -> None:
    st.set_page_config(page_title="공공 RFP Pain Point 허브", layout="wide")
    st.title("공공 RFP × 산업 Pain Point 데이터 허브")
    st.caption("데이터마이닝 · 황동욱 · 2024720459")

    df = load_meta()
    if df.empty:
        st.warning("`data/processed/rfp_meta.csv` 가 없습니다. "
                    "`python src/preprocess_rfp.py` 를 먼저 실행하세요.")
        st.stop()
    df_tok = load_tokens()
    df_news = load_news()

    df_f = sidebar_filters(df)

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


if __name__ == "__main__":
    main()
