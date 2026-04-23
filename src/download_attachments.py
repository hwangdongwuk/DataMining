"""나라장터 공고 첨부파일(PDF/HWP) 다운로더.

수집된 JSONL의 ntceSpecDocUrl1~10 을 순회하며 파일을 저장한다.
공고번호(bidNtceNo) 단위로 서브 디렉토리에 저장.

사용법:
    python src/download_attachments.py \\
        --in data/raw/narajangteo \\
        --out data/raw/rfp_files \\
        --sample 500      # 전체 중 무작위 500건만
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from urllib.parse import unquote

import requests
from tqdm import tqdm

SPEC_URL_FIELDS = [f"ntceSpecDocUrl{i}" for i in range(1, 11)]
SPEC_NAME_FIELDS = [f"ntceSpecFileNm{i}" for i in range(1, 11)]


def iter_records(in_dir: Path):
    for fp in sorted(in_dir.glob("narajangteo_*.jsonl")):
        with fp.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def collect_download_targets(records) -> list[dict]:
    targets: list[dict] = []
    for rec in records:
        bidno = rec.get("bidNtceNo") or "unknown"
        for url_k, name_k in zip(SPEC_URL_FIELDS, SPEC_NAME_FIELDS):
            url = (rec.get(url_k) or "").strip()
            if not url:
                continue
            name = (rec.get(name_k) or "").strip() or url.rsplit("/", 1)[-1]
            targets.append({"bidno": bidno, "url": url, "name": name,
                            "title": rec.get("bidNtceNm", "")})
    return targets


def safe_filename(name: str) -> str:
    name = unquote(name)
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name[:150]


def download_one(target: dict, out_root: Path, timeout: int = 30) -> tuple[bool, str]:
    sub = out_root / target["bidno"]
    sub.mkdir(parents=True, exist_ok=True)
    fname = safe_filename(target["name"])
    dest = sub / fname
    if dest.exists() and dest.stat().st_size > 0:
        return True, "skip"
    try:
        r = requests.get(target["url"], timeout=timeout, stream=True)
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        return True, "ok"
    except Exception as e:
        return False, str(e)[:120]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_dir", default="data/raw/narajangteo")
    p.add_argument("--out", default="data/raw/rfp_files")
    p.add_argument("--sample", type=int, default=0,
                   help="무작위 샘플 수 (0=전체)")
    p.add_argument("--sleep", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = list(iter_records(in_dir))
    print(f"[INFO] 레코드 {len(records)}건 로드")
    targets = collect_download_targets(records)
    print(f"[INFO] 첨부 URL 총 {len(targets)}개")

    if args.sample and args.sample < len(targets):
        random.seed(args.seed)
        targets = random.sample(targets, args.sample)
        print(f"[INFO] 샘플링 {len(targets)}개로 축소")

    ok = fail = 0
    log_path = out_dir / "_download_log.tsv"
    with log_path.open("a", encoding="utf-8") as log:
        for t in tqdm(targets, desc="download"):
            good, msg = download_one(t, out_dir)
            log.write(f"{t['bidno']}\t{t['name']}\t{msg}\n")
            if good:
                ok += 1
            else:
                fail += 1
            time.sleep(args.sleep)

    print(f"[DONE] 성공 {ok}, 실패 {fail}, 로그 {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
