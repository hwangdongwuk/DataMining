"""presentation.md → 슬라이드 PDF (원수빈 스타일 참고).

- A4 landscape
- 각 ## 섹션 = 1 슬라이드
- 상단 제목 · bullet 구조 · 여백 충분
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import markdown

MD = Path("reports/presentation.md")
HTML = Path("reports/presentation.html")
PDF = Path("reports/presentation.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4 landscape; margin: 16mm 22mm; }
html, body { margin: 0; padding: 0; }
body { font-family: -apple-system, "Apple SD Gothic Neo", "AppleGothic",
       sans-serif; color: #222; line-height: 1.6; font-size: 15pt; }

/* 표지 */
h1 { font-size: 32pt; color: #1d3557; margin: 0 0 14px 0;
     border-bottom: 4px solid #2a9d8f; padding-bottom: 10px; }
h1 + h3 { font-size: 18pt; color: #2a9d8f; border: none;
          margin-top: 20px; padding: 0; }
h1 + h3 + p { font-size: 16pt; color: #444; margin-top: 40px; line-height: 2; }

/* 각 ## = 새 슬라이드 */
h2 { page-break-before: always; color: #1d3557;
     border-bottom: 3px solid #2a9d8f; padding-bottom: 8px;
     margin: 0 0 16px 0; font-size: 24pt; }
h1 { page-break-after: always; }

/* 소제목 */
h3 { color: #2a9d8f; font-size: 16pt; margin-top: 16px;
     margin-bottom: 6px; }

ul, ol { margin: 4px 0 10px 22px; }
li { margin: 4px 0; font-size: 14pt; }
li li { font-size: 13pt; color: #555; }

strong { color: #e76f51; }

code { background: #eef3f7; padding: 1px 5px; border-radius: 3px;
       font-family: "SF Mono", Menlo, monospace; font-size: 12pt; }

hr { display: none; }

.footer { position: fixed; bottom: 10mm; right: 22mm;
          font-size: 10pt; color: #888; }
"""

FOOTER_HTML = """<div class="footer">데이터마이닝 중간보고 · 황동욱 2024720459</div>"""


def main() -> int:
    md_text = MD.read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>중간보고 발표자료</title><style>{CSS}</style></head>
<body>{body}{FOOTER_HTML}</body></html>"""
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
