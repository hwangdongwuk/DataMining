# DataMining

성균관대학원 2026학년도 1학기(2-1) **데이터마이닝** 프로젝트 저장소

- 학번: 2024720459
- 이름: 황동욱

## 프로젝트 주제

공공 RFP × 산업뉴스 × 규제 데이터 기반 **산업별 Pain Point 분석** 및
컨설팅 프로세스(ISP · PI · POC · BPR)별 **제안 전략 자동화 데이터 허브** 구축

## 연구 질문

1. 나라장터 RFP 본문·산업 뉴스·규제 공시를 통합 분석하면 산업별 반복 Pain Point를 정량화할 수 있는가?
2. 그 Pain Point가 ISP · PI · POC · BPR · PMO 중 어느 컨설팅 유형 수요와 연결되는지 자동 분류할 수 있는가?
3. 이를 통해 제안 전략(Win Strategy) 핵심 포인트를 자동 추출해 제안서 작성에 활용할 수 있는가?

## 데이터 소스

| # | 소스 | 유형 | 접근 | 상태 |
|---|------|------|------|------|
| 1 | 나라장터 입찰공고 OpenAPI (용역) | REST API | data.go.kr, `getBidPblancListInfoServc` | ✅ |
| 2 | 나라장터 첨부 PDF/HWP | 파일 다운로드 | API `ntceSpecDocUrl` → pdfplumber/hwp5txt | 🔄 샘플 |
| 3 | 금감원 RSS + 네이버 뉴스 API | RSS / REST | fss.or.kr RSS, Naver 검색 API | 📅 W10 |

## 파이프라인 (5단계 · W07 AWS 데이터허브 매핑)

| 단계 | 계획 | 도구 | AWS 매핑 |
|------|------|------|---------|
| ① 수집 | 나라장터 3년치(2023~2025) 용역공고 메타 + 첨부 + 금감원 RSS + 뉴스 API | requests, tqdm | Lambda + EventBridge |
| ② 저장 | `data/raw`(JSONL/PDF/HWP), `data/processed`(CSV), GitHub에 코드 | pandas | S3 + RDS |
| ③ 처리 | pdfplumber/hwp5txt 본문 추출, 정규식 섹션 파싱, kiwipiepy 형태소, 태깅 | pdfplumber, hwp5txt, kiwipiepy, re | Lambda / Glue |
| ④ 분석 | TF-IDF + sklearn LDA 8~12 토픽, 규제→발주 시차 분석, Win Strategy 룰 | sklearn, statsmodels | SageMaker / EC2 |
| ⑤ 시각화 | Streamlit 대시보드 (워드클라우드 · 타임라인 · Win Strategy 추출) | streamlit, plotly, matplotlib | EC2 + Streamlit |

> Python 3.14 환경에서 `konlpy` / `gensim` 빌드 실패 → **`kiwipiepy` + `sklearn.decomposition.LatentDirichletAllocation`** 로 대체.

## AWS 인프라

- 계정: `257925264162` · 리전: `ap-southeast-2` (시드니)
- EC2 `datamining_demo` (t3.micro, Amazon Linux 2023, Public IP 13.239.237.95)
- Security Group `sg-0b7c854caa4d4e287` (SSH 22 → 내 IP 한정)
- S3 버킷 `datamining-257925264162-raw` (프리티어, 퍼블릭 차단, 버저닝 On)
- Budgets **$5/월 알림** — 필수

## 디렉토리 구조

```
DataMining/
├── data/
│   ├── raw/
│   │   ├── narajangteo/    # *.jsonl (월별 36파일)
│   │   └── rfp_files/      # {bidNtceNo}/*.pdf,hwp
│   └── processed/          # rfp_meta.csv, rfp_text.csv, rfp_tokens.csv
├── notebooks/              # Jupyter 분석 노트북
├── src/
│   ├── collect_narajangteo_api.py  # 월별 분할 + 페이지네이션 + 재시도
│   ├── download_attachments.py     # 첨부 PDF/HWP 다운로더
│   ├── preprocess_rfp.py           # 메타 정제 + 본문 추출 + 형태소
│   ├── eda.py                      # 시각화 PNG + eda_summary.json
│   └── app_streamlit.py            # 대시보드
├── reports/
│   ├── midterm.md          # 중간보고서 (7개 항목)
│   ├── midterm.pdf
│   ├── eda_summary.json
│   └── figures/*.png
├── scripts/
│   ├── aws_bootstrap.sh    # S3 버킷 생성 + raw/processed 업로드
│   └── inject_report_numbers.py  # midterm.md 수치 자동 주입
├── .env.example
├── requirements.txt
└── README.md
```

## 빠른 시작

```bash
# 1) 환경
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 서비스키 편집

# 2) 3년치 수집
python src/collect_narajangteo_api.py \
  --start 20230101 --end 20251231 \
  --kind 용역 --split monthly --rows 999

# 3) 첨부 샘플 다운로드
python src/download_attachments.py --sample 500

# 4) 전처리 & 태깅
python src/preprocess_rfp.py

# 5) EDA & 시각화
python src/eda.py
python scripts/inject_report_numbers.py  # midterm.md 수치 주입

# 6) AWS S3 업로드
bash scripts/aws_bootstrap.sh

# 7) 대시보드
streamlit run src/app_streamlit.py
```

## 진행 상황

- [x] W02 주제 선정 · 계획서 제출
- [x] W03 GitHub · 로컬 환경 구축
- [x] 나라장터 수집 스크립트 (월별 분할 · 재시도 · 999rows)
- [x] EC2 SSH 구성 (Security Group 22 개방)
- [x] AWS IAM · Access Key 발급
- [x] 전처리/EDA/Streamlit/S3 업로드 코드
- [ ] 3년치 수집 완료
- [ ] 첨부 다운로드 (샘플)
- [ ] 중간보고서 수치 주입 · PDF 변환
- [ ] 분석 모델링 (TF-IDF, LDA, 시차 분석)
- [ ] EC2 Streamlit 배포
- [ ] 최종 발표

## 라이선스 · 고지

- 나라장터 OpenAPI: 공공데이터 이용 약관 준수
- 수집 데이터는 학술 · 교육 목적에 한정
- `.env` · `data/raw/` · `data/processed/` 는 Git 미추적
