"""KAIB2026 정부 AI 재정계획 데이터 통합 뷰.

나라장터 IT 발주(메인)와 비교할 외부 축으로 사용한다.
출처: github.com/hollobit/KAIB2026 (2026 AI 재정사업 현황, 비공식 분석본)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

KAIB_DIR = Path("data/kaib")


@st.cache_data
def load_kaib() -> dict:
    def j(f: str):
        p = KAIB_DIR / f
        if not p.exists():
            return None
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)
    return {
        "budget": j("budget_db.json"),
        "sim": j("similarity_analysis.json"),
        "collab": j("collaboration_analysis.json"),
        "toc": j("toc_mapping.json"),
    }


def _b2026(p: dict) -> float:
    b = p.get("budget")
    if isinstance(b, dict):
        return b.get("2026_budget") or 0
    return b or 0


def _project_type(p: dict) -> str:
    if p.get("is_rnd"):
        return "R&D"
    if p.get("is_informatization"):
        return "정보화"
    return "기타"


@st.cache_data
def projects_df() -> pd.DataFrame:
    k = load_kaib()
    if not k["budget"]:
        return pd.DataFrame()
    rows = []
    for p in k["budget"]["projects"]:
        rows.append({
            "id": p["id"],
            "사업명": p.get("project_name"),
            "부처": p.get("department"),
            "분야": p.get("field"),
            "유형": _project_type(p),
            "예산2026(백만원)": _b2026(p),
            "신규여부": p.get("status"),
            "AI도메인": ", ".join(p.get("ai_domains") or []),
            "키워드": ", ".join((p.get("keywords") or [])[:6]),
        })
    return pd.DataFrame(rows)


def _won(million: float) -> str:
    """백만원 → 사람이 읽는 단위."""
    jo = million / 1_000_000  # 백만 → 조
    if jo >= 1:
        return f"{jo:,.1f}조원"
    eok = million / 100  # 백만 → 억
    return f"{eok:,.0f}억원"


# ── 정부 AI 재정계획 (KAIB2026) ─────────────────────────────

def _overview(k: dict) -> None:
    m = k["budget"]["metadata"]
    st.markdown("#### 🏛 2026 정부 AI 재정사업 개요")
    st.caption(f"출처: {m.get('source','KAIB2026')} · 추출 {m.get('extraction_date','')} "
               "· github.com/hollobit/KAIB2026")
    c = st.columns(4)
    c[0].metric("AI 재정사업", f"{m['total_projects']:,}건")
    c[1].metric("참여 부처", f"{m['total_departments']}개")
    c[2].metric("2026 예산", _won(m["total_budget_2026"]),
                f"{m['budget_change']/m['total_budget_2025']*100:+.1f}% vs 2025")
    c[3].metric("R&D · 정보화", f"{m['rnd_projects']} · {m['info_projects']}")

    a = k["budget"]["analysis"]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**사업 유형 (R&D vs 정보화)**")
        bt = pd.DataFrame([{"유형": t, "예산(백만원)": v["total"], "건수": v["count"]}
                           for t, v in a["by_type"].items()])
        st.plotly_chart(px.bar(bt, x="유형", y="예산(백만원)", text="건수"),
                        use_container_width=True)
    with col2:
        st.markdown("**AI 도메인 Top10 (예산 기준)**")
        bd = pd.DataFrame([{"도메인": d, "예산(백만원)": v["total"], "건수": v["count"]}
                          for d, v in a["by_domain"].items()])
        bd = bd.sort_values("예산(백만원)", ascending=False).head(10)
        st.plotly_chart(px.bar(bd, x="예산(백만원)", y="도메인", orientation="h",
                               text="건수"), use_container_width=True)


def _by_department(k: dict) -> None:
    st.markdown("#### 🏢 부처별 AI 재정사업")
    a = k["budget"]["analysis"]["by_department"]
    rows = [{"부처": d, "사업수": v["count"], "2026예산(백만원)": v["total_2026"],
             "2025예산(백만원)": v.get("total_2025", 0)} for d, v in a.items()]
    df = pd.DataFrame(rows).sort_values("2026예산(백만원)", ascending=False)
    df["증감률%"] = ((df["2026예산(백만원)"] - df["2025예산(백만원)"])
                   / df["2025예산(백만원)"].replace(0, pd.NA) * 100).round(1)
    top = df.head(15)
    st.plotly_chart(
        px.bar(top, x="2026예산(백만원)", y="부처", orientation="h",
               text="사업수", title="부처별 2026 AI 예산 Top15"),
        use_container_width=True)
    st.dataframe(df, use_container_width=True, height=320)


def _by_field(k: dict) -> None:
    st.markdown("#### 🗂 분야별 분석")
    pdf = projects_df()
    g = (pdf.groupby("분야")["예산2026(백만원)"].agg(["sum", "count"])
            .reset_index().sort_values("sum", ascending=False))
    g.columns = ["분야", "예산(백만원)", "사업수"]
    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(px.bar(g, x="예산(백만원)", y="분야", orientation="h",
                               text="사업수"), use_container_width=True)
    with c2:
        st.markdown("**키워드 클러스터 (예산 Top)**")
        kc = pd.DataFrame([{"키워드": c["keyword"], "사업수": c["project_count"],
                            "부처수": c["department_count"],
                            "예산(백만원)": c["total_budget"]}
                           for c in k["budget"]["analysis"]["keyword_clusters"]])
        kc = kc.sort_values("예산(백만원)", ascending=False).head(12)
        st.dataframe(kc, use_container_width=True, height=380)


def _changes(k: dict) -> None:
    st.markdown("#### 📊 2025 → 2026 예산 증감")
    a = k["budget"]["analysis"]

    def _df(rows):
        return pd.DataFrame([{"사업": x.get("name"), "부처": x.get("department"),
                              "증감(백만원)": x.get("change_amount"),
                              "증감률%": x.get("change_rate")} for x in rows])
    inc = _df(a["top_increases"][:12])
    dec = _df(a["top_decreases"][:12])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**📈 증액 Top12**")
        st.dataframe(inc, use_container_width=True, height=440)
    with c2:
        st.markdown("**📉 감액 Top12**")
        st.dataframe(dec, use_container_width=True, height=440)

    st.markdown("**부처별 증감률 (2026 vs 2025, 예산 Top15)**")
    bd = k["budget"]["analysis"]["by_department"]
    rows = [{"부처": d, "2026": v["total_2026"], "2025": v.get("total_2025", 0)}
            for d, v in bd.items()]
    g = pd.DataFrame(rows).sort_values("2026", ascending=False).head(15)
    g["증감률%"] = ((g["2026"] - g["2025"])
                  / g["2025"].replace(0, pd.NA) * 100).round(1)
    st.plotly_chart(
        px.bar(g.sort_values("증감률%"), x="증감률%", y="부처", orientation="h",
               color="증감률%", color_continuous_scale="RdYlGn"),
        use_container_width=True)


def _projects(k: dict) -> None:
    st.markdown("#### 📑 AI 재정사업 목록 (533건)")
    pdf = projects_df()
    c = st.columns(3)
    dep = c[0].selectbox("부처", ["전체"] + sorted(pdf["부처"].dropna().unique()))
    typ = c[1].selectbox("유형", ["전체"] + sorted(pdf["유형"].dropna().unique()))
    q = c[2].text_input("사업명 검색", "")
    v = pdf.copy()
    if dep != "전체":
        v = v[v["부처"] == dep]
    if typ != "전체":
        v = v[v["유형"] == typ]
    if q:
        v = v[v["사업명"].str.contains(q, na=False)]
    st.caption(f"{len(v):,}건 · 합계 {_won(v['예산2026(백만원)'].sum())}")
    st.dataframe(v.sort_values("예산2026(백만원)", ascending=False),
                 use_container_width=True, height=420)


def _clusters(k: dict) -> None:
    st.markdown("#### 🧩 정책 클러스터 & 유사·중복 사업")
    sim = k["sim"]
    if sim:
        cl = pd.DataFrame([{"클러스터": c["cluster_name"], "사업수": c["member_count"],
                            "예산(백만원)": c.get("total_budget_2026", 0),
                            "부처": ", ".join(c.get("departments", [])[:4])}
                           for c in sim["clusters"]])
        st.markdown(f"**정책 클러스터 {len(cl)}개** — 유사 목적 사업 군집 "
                    "(부처 간 중복·연계 후보)")
        st.dataframe(cl.sort_values("예산(백만원)", ascending=False),
                     use_container_width=True, height=240)
        st.markdown("**유사도 높은 사업쌍 Top (중복 의심)**")
        pr = pd.DataFrame([{"점수": p["similarity_score"], "수준": p["similarity_level"],
                            "사업A": p["project_a"]["project_name"],
                            "사업B": p["project_b"]["project_name"]}
                           for p in sim["pairs"][:30]])
        st.dataframe(pr, use_container_width=True, height=240)


def _collab(k: dict) -> None:
    st.markdown("#### 🔗 부처 간 협업 네트워크")
    col = k["collab"]
    if not col:
        st.info("협업 데이터 없음")
        return
    st.caption("사업 간 가치사슬·협업 연계 분석 (인력양성→연구→산업활용 등)")
    ch = pd.DataFrame([{"체인": c["chain_name"], "길이": c["chain_length"],
                        "부처": ", ".join(c.get("departments", [])[:4])}
                       for c in col["collaboration_chains"][:20]])
    st.markdown("**협업 가치사슬 (value chain) Top20**")
    st.dataframe(ch, use_container_width=True, height=300)
    pr = pd.DataFrame([{"점수": p["collaboration_score"], "유형": p["collaboration_type"],
                        "사업A": p["project_a"]["project_name"],
                        "사업B": p["project_b"]["project_name"]}
                       for p in col["pairs"][:25]])
    st.markdown("**협업 필요 사업쌍 Top**")
    st.dataframe(pr, use_container_width=True, height=260)


def render_kaib() -> None:
    k = load_kaib()
    if not k["budget"]:
        st.warning("`data/kaib/budget_db.json` 없음 — KAIB2026 데이터를 복사하세요.")
        return
    tabs = st.tabs(["개요", "부처별", "분야별", "예산 증감",
                    "사업목록", "정책 클러스터", "협업 네트워크"])
    with tabs[0]:
        _overview(k)
    with tabs[1]:
        _by_department(k)
    with tabs[2]:
        _by_field(k)
    with tabs[3]:
        _changes(k)
    with tabs[4]:
        _projects(k)
    with tabs[5]:
        _clusters(k)
    with tabs[6]:
        _collab(k)


# ── IT 발주(나라장터) ↔ AI 계획(KAIB) 비교 ──────────────────

def render_compare(rfp: pd.DataFrame) -> None:
    k = load_kaib()
    if not k["budget"] or rfp.empty:
        st.info("비교 데이터 부족")
        return
    m = k["budget"]["metadata"]
    st.markdown("#### ⚖️ 정부 AI 재정계획(계획) ↔ 나라장터 IT 발주(집행)")
    st.caption("관점: 본 분석은 **IT 발주 전체**가 모집단 — AI는 그 부분집합. "
               "KAIB2026은 정부 'AI 계획' 비교축.")

    ai_col = "ai_class_strict" if "ai_class_strict" in rfp.columns else "ai_class"
    n_it = len(rfp)
    n_ai = int((rfp[ai_col] == "ai-pure").sum())
    c = st.columns(4)
    c[0].metric("IT 발주 전체 (집행)", f"{n_it:,}건")
    c[1].metric("그 중 AI 발주", f"{n_ai:,}건", f"{n_ai/n_it*100:.1f}%")
    c[2].metric("정부 AI 계획 (예산)", _won(m["total_budget_2026"]),
                f"{m['budget_change']/m['total_budget_2025']*100:+.1f}%")
    c[3].metric("정부 AI 사업수", f"{m['total_projects']:,}건")

    st.info(
        f"💡 **3단 격차** — 미디어 담론(AI 30%) → 정부 계획(27조·+24%) → 실제 IT 발주 중 "
        f"AI는 **{n_ai/n_it*100:.1f}%**. 계획은 가속하나 조달 집행은 소규모 PoC 단계.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**정부 AI 계획 — 부처별 예산 Top10**")
        a = k["budget"]["analysis"]["by_department"]
        bd = (pd.DataFrame([{"부처": d, "예산(백만원)": v["total_2026"]}
                            for d, v in a.items()])
              .sort_values("예산(백만원)", ascending=False).head(10))
        st.plotly_chart(px.bar(bd, x="예산(백만원)", y="부처", orientation="h"),
                        use_container_width=True)
    with col2:
        st.markdown("**나라장터 — AI 발주 수요기관 Top10 (집행)**")
        ai = rfp[rfp[ai_col] == "ai-pure"]
        inst = (ai["dminsttNm"].value_counts().head(10)
                .rename_axis("기관").reset_index(name="발주건수"))
        st.plotly_chart(px.bar(inst, x="발주건수", y="기관", orientation="h"),
                        use_container_width=True)

    st.markdown("**IT 발주 산업분포 — 전체 vs AI 발주 (어디서 AI가 실집행되나)**")
    g = (rfp.assign(ai=rfp[ai_col].eq("ai-pure"))
            .groupby("industry")
            .agg(전체=("ai", "size"), AI=("ai", "sum")).reset_index())
    g["AI비율%"] = (g["AI"] / g["전체"] * 100).round(1)
    g = g.sort_values("전체", ascending=False)
    st.plotly_chart(
        px.bar(g, x="industry", y=["전체", "AI"], barmode="overlay"),
        use_container_width=True)
    st.dataframe(g, use_container_width=True, height=240)
    st.caption("정부 계획은 과기정통부·산업·R&D 집중 → 나라장터에선 그 산하 전문기관"
               "(NIA·KISA·TTA·KERIS·NIPA)이 집행. 산업·중기 R&D 예산은 보조금형이라 "
               "조달 공고로는 가시화되지 않음.")
