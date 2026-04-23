"""reports/midterm.md 의 {{N_META}} 등 플레이스홀더를 EDA 요약값으로 치환."""
from __future__ import annotations

import json
from pathlib import Path

MD = Path("reports/midterm.md")
SUMMARY = Path("reports/eda_summary.json")
RAW_DIR = Path("data/raw/narajangteo")
RFP_DIR = Path("data/raw/rfp_files")


def main() -> int:
    if not SUMMARY.exists():
        print(f"[WARN] {SUMMARY} 없음 — eda.py 먼저 실행")
        return 1
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    n_meta = s.get("n_total", 0)
    n_files = len(list(RAW_DIR.glob("*.jsonl"))) if RAW_DIR.exists() else 0
    n_attach = 0
    if RFP_DIR.exists():
        for sub in RFP_DIR.iterdir():
            if sub.is_dir():
                n_attach += sum(1 for _ in sub.iterdir() if _.is_file())
    pct = f"{(n_attach / max(n_meta, 1)) * 100:.1f}"

    n_inst = s.get("n_institutions", 0)
    news_path = Path("data/processed/news_meta.csv")
    n_news = 0
    if news_path.exists():
        with news_path.open(encoding="utf-8-sig") as f:
            n_news = max(sum(1 for _ in f) - 1, 0)

    txt = MD.read_text(encoding="utf-8")
    txt = (txt
           .replace("{{N_META}}", f"{n_meta:,}")
           .replace("{{N_INST}}", f"{n_inst:,}")
           .replace("{{N_FILES}}", f"{n_files}")
           .replace("{{N_ATTACH}}", f"{n_attach:,}")
           .replace("{{N_NEWS}}", f"{n_news:,}")
           .replace("{{PCT_ATTACH}}", pct))
    MD.write_text(txt, encoding="utf-8")
    print(f"[DONE] midterm.md 수치 주입 — meta={n_meta:,} inst={n_inst:,} "
          f"files={n_files} attach={n_attach:,} news={n_news:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
