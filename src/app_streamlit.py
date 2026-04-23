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

    df_f = sidebar_filters(df)

    tabs = st.tabs(["개요", "월별 추이", "키워드", "공고 검색"])
    with tabs[0]:
        page_overview(df_f)
    with tabs[1]:
        page_timeline(df_f)
    with tabs[2]:
        page_keywords(df_f, df_tok)
    with tabs[3]:
        page_search(df_f)


if __name__ == "__main__":
    main()
