"""reports/midterm.md → 슬라이드 형태 PDF (가로 A4).

각 ## 섹션마다 페이지 분리, 슬라이드용 폰트·여백 적용.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import markdown

MD = Path("reports/midterm.md")
HTML = Path("reports/midterm_slides.html")
PDF = Path("reports/midterm_slides.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4 landscape; margin: 14mm 18mm; }
html, body { margin: 0; padding: 0; }
body { font-family: -apple-system, "Apple SD Gothic Neo", "AppleGothic",
       sans-serif; color: #1d3557; line-height: 1.55;
       font-size: 13.5pt; }

/* 섹션(##) 마다 새 페이지 */
h2 { page-break-before: always; color: #264653;
     border-bottom: 3px solid #2a9d8f; padding-bottom: 6px;
     margin-top: 0; font-size: 22pt; }
h1 + p, h1 + ul { page-break-after: always; }
h1 { font-size: 26pt; color: #1d3557; margin-top: 0;
     border-bottom: none; padding-bottom: 0; }
/* 표지에서는 h1 뒤에 바로 내용, 그 다음 섹션부터 새 페이지 */
h1 + p { font-size: 14pt; color: #555; }

h3 { color: #2a9d8f; font-size: 16pt; margin-top: 16px;
     border-bottom: 1px solid #cde; padding-bottom: 3px; }
h4 { color: #444; font-size: 14pt; }

table { border-collapse: collapse; width: 100%; margin: 10px 0;
        font-size: 11.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #bbb; padding: 4px 9px; text-align: left; }
th { background: #2a9d8f; color: white; }
tr:nth-child(even) td { background: #f3f9f7; }

code { background: #eef3f7; padding: 1px 4px; border-radius: 3px;
       font-family: "SF Mono", Menlo, monospace; font-size: 11pt; }
pre { background: #263238; color: #eee; padding: 10px 14px;
      border-radius: 5px; font-size: 10.5pt; overflow: auto;
      page-break-inside: avoid; }
pre code { background: transparent; color: inherit; font-size: 10.5pt; }

blockquote { border-left: 4px solid #e76f51; padding: 4px 12px;
             color: #555; margin: 10px 0; background: #fff3ef; }
ul, ol { margin: 8px 0 8px 22px; }
li { margin: 3px 0; }
img { max-width: 80%; max-height: 55vh; display: block;
      margin: 10px auto; }
hr { display: none; }

/* 페이지 하단 소제목용 */
.footer { position: fixed; bottom: 8mm; right: 14mm;
          font-size: 9pt; color: #888; }
"""

FOOTER_HTML = """<div class="footer">데이터마이닝 중간보고서 · 황동욱 2024720459</div>"""


def main() -> int:
    if not MD.exists():
        print(f"[ERR] {MD} 없음", file=sys.stderr)
        return 1
    md_text = MD.read_text(encoding="utf-8")
    body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>중간보고서 슬라이드</title>
<style>{CSS}</style></head><body>{body}{FOOTER_HTML}</body></html>"""
    HTML.write_text(html, encoding="utf-8")
    print(f"[1/2] HTML → {HTML}")

    cmd = [CHROME, "--headless=new", "--disable-gpu",
           "--no-pdf-header-footer",
           f"--print-to-pdf={PDF.resolve()}",
           "file://" + str(HTML.resolve())]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(r.stderr[:400], file=sys.stderr); return 2
    print(f"[2/2] PDF → {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
