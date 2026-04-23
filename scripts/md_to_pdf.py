"""midterm.md → midterm.pdf 변환.

markdown → HTML(한글폰트·표 CSS 포함) → Chrome headless → PDF.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import markdown

MD_PATH = Path("reports/midterm.md")
HTML_PATH = Path("reports/midterm.html")
PDF_PATH = Path("reports/midterm.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 20mm 16mm; }
body { font-family: -apple-system, "Apple SD Gothic Neo", "AppleGothic",
       "Noto Sans KR", sans-serif; color: #222; line-height: 1.55;
       font-size: 10.5pt; }
h1 { border-bottom: 2px solid #264653; padding-bottom: 6px; }
h2 { border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 22px; }
h3 { margin-top: 14px; color: #264653; }
code { background: #f4f4f4; padding: 1px 4px; border-radius: 3px;
       font-family: "SF Mono", Menlo, monospace; font-size: 9pt; }
pre { background: #f4f4f4; padding: 8px 10px; border-radius: 4px;
      overflow-x: auto; font-size: 9pt; }
table { border-collapse: collapse; width: 100%; margin: 10px 0;
        font-size: 9.5pt; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; }
th { background: #f0f0f0; }
blockquote { border-left: 3px solid #2a9d8f; padding-left: 10px;
             color: #555; margin: 10px 0; }
img { max-width: 100%; }
hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
"""


def main() -> int:
    if not MD_PATH.exists():
        print(f"[ERR] {MD_PATH} 없음", file=sys.stderr)
        return 1

    md_text = MD_PATH.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "toc"])
    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<title>중간 보고서</title>
<style>{CSS}</style></head>
<body>{html_body}</body></html>"""
    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"[1/2] HTML 작성 → {HTML_PATH}")

    file_url = "file://" + str(HTML_PATH.resolve())
    cmd = [CHROME, "--headless=new", "--disable-gpu",
           "--no-pdf-header-footer",
           f"--print-to-pdf={PDF_PATH.resolve()}", file_url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        print(f"[ERR] Chrome: {r.stderr[:400]}", file=sys.stderr)
        return 2
    print(f"[2/2] PDF 생성 → {PDF_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
