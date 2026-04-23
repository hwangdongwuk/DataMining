"""presentation.md → 슬라이드 PDF (도식·이미지 포함)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import markdown

MD = Path("reports/presentation.md")
HTML = Path("reports/presentation.html")
PDF = Path("reports/presentation.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4 landscape; margin: 12mm 16mm; }
html, body { margin: 0; padding: 0; }
body { font-family: -apple-system, "Apple SD Gothic Neo", "AppleGothic",
       sans-serif; color: #222; line-height: 1.55; font-size: 14pt; }

/* 표지 */
h1 { font-size: 30pt; color: #1d3557; margin: 0 0 14px 0;
     border-bottom: 4px solid #2a9d8f; padding-bottom: 10px;
     page-break-after: always; }
h1 + h3 { font-size: 18pt; color: #2a9d8f; border: none;
          margin-top: 20px; padding: 0; }
h1 + h3 + p { font-size: 15pt; color: #444; margin-top: 40px; line-height: 2; }

/* 슬라이드 구분 */
h2 { page-break-before: always; color: #1d3557;
     border-bottom: 3px solid #2a9d8f; padding-bottom: 6px;
     margin: 0 0 12px 0; font-size: 22pt; }

h3 { color: #2a9d8f; font-size: 15pt; margin-top: 10px;
     margin-bottom: 5px; }

ul, ol { margin: 4px 0 8px 22px; }
li { margin: 3px 0; font-size: 13.5pt; }
li li { font-size: 12.5pt; color: #555; }

strong { color: #e76f51; }

code { background: #eef3f7; padding: 1px 5px; border-radius: 3px;
       font-family: "SF Mono", Menlo, monospace; font-size: 12pt; }
pre { background: #1d3557; color: #f1faee; padding: 10px 14px;
      border-radius: 5px; font-size: 11.5pt; font-family: "SF Mono", Menlo, monospace;
      white-space: pre; overflow: auto; page-break-inside: avoid; }
pre code { background: transparent; color: inherit; font-size: 11.5pt; }

img { display: block; margin: 6px auto; max-height: 62vh; max-width: 95%; }

hr { display: none; }

.footer { position: fixed; bottom: 7mm; right: 16mm;
          font-size: 9pt; color: #999; }
"""

FOOTER = """<div class="footer">데이터마이닝 중간보고 · 황동욱 2024720459</div>"""


def main() -> int:
    md_text = MD.read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>중간보고 발표자료</title><style>{CSS}</style></head>
<body>{body}{FOOTER}</body></html>"""
    HTML.write_text(html, encoding="utf-8")
    print(f"[1/2] HTML → {HTML}")

    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu",
         "--no-pdf-header-footer",
         f"--print-to-pdf={PDF.resolve()}",
         "file://" + str(HTML.resolve())],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(r.stderr[:400]); return 2
    print(f"[2/2] PDF → {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
