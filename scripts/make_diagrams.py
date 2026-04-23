"""발표자료용 도식(diagram) 생성.

- 파이프라인 5단계 흐름도
- AWS 데이터허브 아키텍처
- Key-based Join 개념도
- 수집 KPI 요약 인포그래픽
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.family"] = ["AppleGothic", "NanumGothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path("reports/figures")
OUT.mkdir(parents=True, exist_ok=True)


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close()


def pipeline_flow():
    fig, ax = plt.subplots(figsize=(12, 3.8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    stages = [
        ("수집", "requests · feedparser\n월별 분할·재시도", "#2a9d8f"),
        ("저장", "S3 + 로컬 JSONL/CSV", "#e9c46a"),
        ("처리", "pdfplumber · hwp5txt\nkiwipiepy", "#f4a261"),
        ("분석", "TF-IDF · sklearn LDA\n시차 분석", "#e76f51"),
        ("시각화", "Streamlit\nPlotly · Matplotlib", "#264653"),
    ]
    xs = [0.5, 2.8, 5.1, 7.4, 9.7]
    for (title, body, color), x in zip(stages, xs):
        box = FancyBboxPatch((x, 1), 2.0, 2.0,
                             boxstyle="round,pad=0.05",
                             linewidth=1.5, edgecolor="black", facecolor=color)
        ax.add_patch(box)
        ax.text(x + 1.0, 2.55, title, ha="center", va="center",
                fontsize=16, fontweight="bold",
                color="white" if color == "#264653" else "black")
        ax.text(x + 1.0, 1.7, body, ha="center", va="center",
                fontsize=9.5,
                color="white" if color == "#264653" else "#222")
    for x in xs[:-1]:
        ax.add_patch(FancyArrowPatch((x + 2.05, 2), (x + 2.3, 2),
                                     arrowstyle="->", mutation_scale=20,
                                     color="#333"))
    ax.text(6, 3.7, "5-단계 데이터 파이프라인",
            ha="center", fontsize=17, fontweight="bold", color="#1d3557")
    ax.text(6, 0.5, "나라장터 API · 첨부 PDF/HWP · 네이버 뉴스 · 금융위 RSS  →  Pain Point 인사이트",
            ha="center", fontsize=11, color="#555", style="italic")
    save("10_pipeline_flow.png")


def aws_architecture():
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis("off")
    ax.text(6.5, 6.5, "AWS 데이터허브 아키텍처 (W07 매핑)",
            ha="center", fontsize=16, fontweight="bold", color="#1d3557")

    layers = [
        (0.3, 5.2, 12.4, 0.7, "① 수집 Lambda + EventBridge",   "#2a9d8f"),
        (0.3, 4.0, 12.4, 0.7, "② 저장 S3 (raw/processed/final) + RDS", "#e9c46a"),
        (0.3, 2.8, 12.4, 0.7, "③ 처리 Lambda(경량) / Glue(대용량)",    "#f4a261"),
        (0.3, 1.6, 12.4, 0.7, "④ 분석 SageMaker / EC2 (Python)",       "#e76f51"),
        (0.3, 0.4, 12.4, 0.7, "⑤ 시각화 EC2 + Streamlit (8501)",        "#264653"),
    ]
    for x, y, w, h, label, c in layers:
        box = FancyBboxPatch((x, y), w, h,
                             boxstyle="round,pad=0.03",
                             linewidth=1, edgecolor="black", facecolor=c)
        ax.add_patch(box)
        ax.text(x + 0.3, y + h/2, label, va="center", fontsize=13,
                fontweight="bold",
                color="white" if c in ("#264653", "#e76f51") else "#1d3557")

    # 사이드 안내
    ax.text(13, 3.5, "IAM\n(권한)\n\nCloudWatch\n(모니터)\n\nSecrets\n(API 키)",
            fontsize=10, ha="left", va="center",
            bbox=dict(facecolor="#f0f0f0", edgecolor="#bbb", boxstyle="round,pad=0.4"))
    ax.text(6.5, 0, "현재 구현 상태: EC2 running · S3 버킷 생성 · Access Key 발급 · SSH/8501 개방",
            ha="center", fontsize=10, style="italic", color="#555")
    save("11_aws_architecture.png")


def key_join_diagram():
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")
    ax.text(6, 4.6, "Key-based Join 설계: bidNtceNo 기반 통합",
            ha="center", fontsize=16, fontweight="bold", color="#1d3557")

    sources = [
        (0.5, 2.5, "나라장터 API\n메타", "420,104", "#2a9d8f"),
        (3.3, 2.5, "첨부 PDF/HWP\n본문", "173", "#e9c46a"),
        (6.1, 2.5, "네이버 뉴스\n검색", "13,765", "#f4a261"),
        (8.9, 2.5, "FSC RSS\n규제공시", "30", "#e76f51"),
    ]
    for x, y, title, n, c in sources:
        box = FancyBboxPatch((x, y), 2.2, 1.3,
                             boxstyle="round,pad=0.05",
                             linewidth=1.2, edgecolor="black", facecolor=c)
        ax.add_patch(box)
        ax.text(x + 1.1, y + 0.95, title, ha="center", fontsize=11,
                fontweight="bold",
                color="white" if c in ("#264653", "#e76f51") else "#1d3557")
        ax.text(x + 1.1, y + 0.35, f"{n} 건", ha="center", fontsize=13,
                fontweight="bold",
                color="white" if c in ("#264653", "#e76f51") else "#1d3557")

    # 화살표 → 통합
    target_x, target_y = 4.9, 0.3
    ax.add_patch(FancyBboxPatch((target_x, target_y), 2.2, 1.0,
                                boxstyle="round,pad=0.05",
                                linewidth=2, edgecolor="#264653",
                                facecolor="#1d3557"))
    ax.text(target_x + 1.1, target_y + 0.5, "통합 DataFrame",
            ha="center", va="center", fontsize=13, fontweight="bold",
            color="white")

    for x, y, *_ in sources:
        ax.add_patch(FancyArrowPatch((x + 1.1, y), (target_x + 1.1, target_y + 1.0),
                                     arrowstyle="->", mutation_scale=15,
                                     color="#666", linewidth=1))

    ax.text(6, 2.15, "공통 키: bidNtceNo · 날짜 · 키워드",
            ha="center", fontsize=11, color="#555", style="italic")
    save("12_key_join.png")


def kpi_infographic():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 4); ax.axis("off")
    ax.text(6, 3.6, "수집 KPI 요약",
            ha="center", fontsize=17, fontweight="bold", color="#1d3557")

    kpis = [
        ("420,104", "나라장터\n공고 메타", "#2a9d8f"),
        ("16,551", "수요기관\n(unique)", "#e9c46a"),
        ("13,765", "네이버 뉴스\n(중복 제거)", "#f4a261"),
        ("197", "첨부 PDF/HWP\n샘플", "#e76f51"),
        ("30", "금융위 RSS\n(보도+공지)", "#264653"),
    ]
    xs = [0.5, 2.8, 5.1, 7.4, 9.7]
    for (v, l, c), x in zip(kpis, xs):
        box = FancyBboxPatch((x, 1.2), 2.0, 1.8,
                             boxstyle="round,pad=0.05",
                             linewidth=1.5, edgecolor="black", facecolor=c)
        ax.add_patch(box)
        ax.text(x + 1.0, 2.45, v, ha="center", fontsize=22, fontweight="bold",
                color="white" if c in ("#264653", "#e76f51") else "#1d3557")
        ax.text(x + 1.0, 1.55, l, ha="center", fontsize=11,
                color="white" if c in ("#264653", "#e76f51") else "#1d3557")

    ax.text(6, 0.6,
            "기간: 2023-01-01 ~ 2025-11-25 (27개월) · S3 총 25 객체 · 2.1 GB",
            ha="center", fontsize=11, color="#555")
    save("13_kpi_infographic.png")


if __name__ == "__main__":
    pipeline_flow()
    aws_architecture()
    key_join_diagram()
    kpi_infographic()
    print("[DONE] 4개 도식 생성 →", OUT)
