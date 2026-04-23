"""EDA 자동화 — 기초 통계 + 시각화 PNG + 중간 인사이트 JSON 생성.

실행:
    python src/eda.py
출력:
    reports/figures/*.png
    reports/eda_summary.json  (보고서 자동 주입용)
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = ["AppleGothic", "NanumGothic",
                                "Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

META = Path("data/processed/rfp_meta.csv")
TOKENS = Path("data/processed/rfp_tokens.csv")
FIG = Path("reports/figures")
OUT = Path("reports/eda_summary.json")


def save(fig_name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(FIG / fig_name, dpi=150, bbox_inches="tight")
    plt.close()


def main() -> int:
    if not META.exists():
        print(f"[ERR] {META} 없음. 전처리를 먼저 실행하세요.")
        return 1

    df = pd.read_csv(META)
    df["bidNtceDt_dt"] = pd.to_datetime(df["bidNtceDt"], errors="coerce")
    df = df.dropna(subset=["bidNtceDt_dt"])

    summary = {
        "n_total": int(len(df)),
        "n_institutions": int(df["dminsttNm"].nunique()),
        "period": {
            "start": str(df["bidNtceDt_dt"].min().date()),
            "end": str(df["bidNtceDt_dt"].max().date()),
        },
        "industry_counts": df["industry"].value_counts().to_dict(),
        "consulting_counts": df["consulting_type"].value_counts().to_dict(),
        "presmptPrce": {
            "count": int(df["presmptPrce"].notna().sum()),
            "mean": float(df["presmptPrce"].mean()) if df["presmptPrce"].notna().any() else None,
            "median": float(df["presmptPrce"].median()) if df["presmptPrce"].notna().any() else None,
            "max": float(df["presmptPrce"].max()) if df["presmptPrce"].notna().any() else None,
        },
        "top_institutions": df["dminsttNm"].value_counts().head(20).to_dict(),
    }

    # 1) 연도별 건수
    yc = df.groupby("year").size()
    yc.plot(kind="bar", title="연도별 공고 건수", color="#2a9d8f")
    plt.ylabel("건수")
    save("01_count_by_year.png")

    # 2) 월별 추이
    mc = df.groupby("year_month").size().sort_index()
    mc.plot(kind="line", marker="o", title="월별 공고 건수 추이", color="#264653")
    plt.ylabel("건수")
    plt.xticks(rotation=45)
    save("02_count_by_month.png")

    # 3) 산업 분포
    df["industry"].value_counts().plot(
        kind="pie", autopct="%1.1f%%", title="산업별 분포", ylabel="",
        colors=["#e76f51", "#f4a261", "#2a9d8f", "#264653", "#e9c46a"])
    save("03_industry_pie.png")

    # 4) 산업 × 컨설팅 히트맵
    ct = pd.crosstab(df["industry"], df["consulting_type"])
    fig, ax = plt.subplots(figsize=(8, 4))
    im = ax.imshow(ct.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(ct.columns)))
    ax.set_xticklabels(ct.columns)
    ax.set_yticks(range(len(ct.index)))
    ax.set_yticklabels(ct.index)
    ax.set_title("산업 × 컨설팅 유형 교차")
    for i in range(ct.shape[0]):
        for j in range(ct.shape[1]):
            ax.text(j, i, int(ct.iat[i, j]), ha="center", va="center",
                    color="black", fontsize=8)
    fig.colorbar(im, ax=ax)
    save("04_industry_consulting_heatmap.png")

    # 5) 예산 분포 (로그)
    prices = df["presmptPrce"].dropna()
    prices = prices[prices > 0]
    if len(prices) > 0:
        ax = prices.plot(kind="hist", bins=60, logx=True, title="추정가격 분포 (log-x)",
                         color="#e76f51", alpha=0.8)
        ax.set_xlabel("추정가격(원, log scale)")
        save("05_price_hist.png")

    # 6) 상위 수요기관 Top 20
    top_inst = df["dminsttNm"].value_counts().head(20)
    top_inst[::-1].plot(kind="barh", title="수요기관 Top 20", color="#264653")
    plt.xlabel("공고 건수")
    save("06_top_institutions.png")

    # 7) 공고명 명사 상위 키워드 (제목 기반, 토큰 데이터 없어도 동작)
    import re
    stop = {"및", "등", "위한", "관련", "사업", "용역", "입찰", "계약",
            "구매", "제공", "기관", "공고", "본", "본건"}
    titles = df["bidNtceNm"].dropna().astype(str)
    words: list[str] = []
    for t in titles:
        for w in re.findall(r"[가-힣A-Za-z]{2,}", t):
            if w not in stop:
                words.append(w)
    wc = Counter(words).most_common(30)
    summary["top_title_keywords"] = dict(wc)
    labels, values = zip(*wc)
    plt.figure(figsize=(10, 6))
    plt.barh(labels[::-1], values[::-1], color="#2a9d8f")
    plt.title("공고명 주요 키워드 Top 30")
    plt.xlabel("빈도")
    save("07_title_keywords.png")

    # 8) 토큰(본문) 기반 키워드 — 있을 때만
    if TOKENS.exists():
        tok = pd.read_csv(TOKENS)
        if not tok.empty and "nouns" in tok.columns:
            all_nouns: list[str] = []
            for s in tok["nouns"].dropna():
                all_nouns.extend(str(s).split())
            body_wc = Counter(all_nouns).most_common(50)
            summary["top_body_keywords"] = dict(body_wc)
            labels, values = zip(*body_wc[:30])
            plt.figure(figsize=(10, 7))
            plt.barh(labels[::-1], values[::-1], color="#e76f51")
            plt.title("본문 주요 키워드 Top 30 (첨부 PDF/HWP)")
            plt.xlabel("빈도")
            save("08_body_keywords.png")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"[DONE] 요약 저장 → {OUT}")
    print(f"       그림 {FIG} 에 8종 내외")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
