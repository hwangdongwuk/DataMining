# 데이터마이닝 중간 보고서

- **학번·이름**: 2024720459 황동욱
- **과목**: 성균관대학원 2-1 데이터마이닝
- **주제**: 공공 RFP × 산업뉴스 × 규제 데이터 기반 산업별 Pain Point 분석 및 컨설팅 프로세스(ISP·PI·POC·BPR)별 제안 전략 자동화 데이터 허브 구축
- **작성일**: 2026-04-23
- **GitHub**: https://github.com/hwangdongwuk/DataMining

---

## ① 프로젝트 개요

### 1.1 연구 질문
1. 나라장터 RFP 본문·산업 뉴스·규제 공시를 통합 분석하면 **산업별 반복 Pain Point를 정량화**할 수 있는가?
2. 도출된 Pain Point가 **ISP·PI·POC·BPR·PMO 중 어느 컨설팅 유형 수요와 연결**되는지 자동 분류할 수 있는가?
3. 이를 통해 **제안 전략(Win Strategy) 핵심 포인트를 자동 추출**하여 제안서 작성에 활용할 수 있는가?

### 1.2 선정 이유
- 보험·금융 IT 기획/PM 실무에서 제안서 작성 시 Pain Point 파악과 Win Strategy 수립에 **수일이 소요**되는 비효율을 **데이터 파이프라인으로 자동화**.
- 수업의 "데이터 허브" 콘셉트에 부합하며, 최종 Streamlit 허브는 제안팀 실무 도구로 즉시 전환 가능.

### 1.3 W02 피드백 반영
W06 강의 피드백("좋은 연구 질문 자가 진단")을 적용하여 질문을 구체화:
- **[구체적 대상]** 나라장터 **용역 공고** (3년치, 2023~2025)
- **[측정 가능한 변수]** 공고 건수, 예산(presmptPrce), 키워드 빈도, 컨설팅 유형 태그
- **[시간/공간 범위]** 2023-01-01 ~ 2025-12-31 (36개월)
- **[방향성]** 산업별 Pain Point 상위 키워드 비교, 컨설팅 유형별 수요 추이

W06 "다중 데이터 소스 결합" 피드백에 따라 **Key-based Join(bidNtceNo)** 으로 메타 + 첨부 본문 + (향후) 금감원 RSS · 네이버 뉴스 결합 설계.

---

## ② 데이터 수집 결과

### 2.1 데이터 소스
| # | 소스 | 유형 | 접근 | 상태 |
|---|------|------|------|------|
| 1 | 나라장터 입찰공고 OpenAPI (용역) | REST API (JSON) | data.go.kr 서비스키 | ✅ 수집 완료 |
| 2 | 나라장터 첨부 PDF/HWP | 파일 다운로드 | API 응답 내 URL | 🔄 샘플 진행 |
| 3 | 금감원 RSS + 네이버 뉴스 API | RSS / REST API | fss.or.kr / Naver | 📅 W10 예정 |

### 2.2 수집 규모 *(실행 후 실측으로 자동 갱신)*
- **공고 메타 (용역)**: `{{N_META}}` 건
- **기간**: 2023-01-01 ~ 2025-12-31 (36개월)
- **월별 분할 JSONL**: `{{N_FILES}}` 개 (`data/raw/narajangteo/*.jsonl`)
- **첨부 파일 샘플**: `{{N_ATTACH}}` 건 (전체의 약 `{{PCT_ATTACH}}` %)

### 2.3 수집 코드 핵심
```python
# src/collect_narajangteo_api.py
BASE_URL = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService"
# 월별 분할 + 페이지네이션(999rows) + 지수 백오프 재시도
for s, e in month_ranges("20230101", "20251231"):
    for page in range(1, total_pages + 1):
        payload = fetch_page(key, endpoint, s, e, page, 999)
        append_jsonl(payload.items())
        time.sleep(0.1)
```

### 2.4 주요 필드 (66개 중 핵심 17)
| 필드 | 의미 |
|------|------|
| bidNtceNo / bidNtceOrd | 공고번호 / 차수 (PK) |
| bidNtceNm | 공고명 |
| bidNtceDt | 공고일시 |
| ntceInsttNm / dminsttNm | 공고기관 / 수요기관 |
| presmptPrce | 추정가격(원) |
| bidBeginDt / bidClseDt / opengDt | 입찰 시작/마감/개찰 |
| ntceSpecDocUrl1~10 | 첨부파일 URL (최대 10개) |

---

## ③ 데이터 전처리

### 3.1 파이프라인
1. **JSONL 통합 로드** → `pd.DataFrame` (66컬럼, 월별 36파일 concat)
2. **중복 제거**: `(bidNtceNo, bidNtceOrd)` 기준
3. **타입 변환**: `bidNtceDt` → datetime, 가격 필드 → numeric
4. **결측치 처리**:
   - `presmptPrce` 결측은 NaN 유지 (미확정 공고 특성 반영, 대체 X)
   - 첨부 URL 빈 문자열 → 누락으로 처리
5. **파생 변수**:
   - `year`, `year_month`
   - `industry`: 공고명 키워드 매칭 (보험 / 금융 / IT / 기타)
   - `consulting_type`: ISP / PI / POC / BPR / PMO / 구축 / 기타
6. **첨부 본문 추출**: `pdfplumber` (PDF), `hwp5txt` (HWP)
7. **형태소 분석**: `kiwipiepy` 로 명사 추출 (길이 ≥ 2)

> Python 3.14 환경에서 `konlpy` / `gensim` 빌드 실패 → 순수 Python `kiwipiepy` + `sklearn.decomposition.LatentDirichletAllocation` 으로 대체.

### 3.2 Before / After
| 항목 | Before (raw JSONL) | After (rfp_meta.csv) |
|------|-------------------|---------------------|
| 스키마 | 66 컬럼 혼재 | 핵심 17컬럼 + 파생 5컬럼 |
| 날짜 | 문자열 | `datetime64[ns]` |
| 중복 | 재공고·차수 혼재 | `(bidNtceNo, bidNtceOrd)` 단위 정리 |
| 분류 | 없음 | `industry × consulting_type` 태그 |

---

## ④ 탐색적 데이터 분석 (EDA)

*(`notebooks/01_eda.ipynb` 와 `reports/figures/` 에서 자동 생성)*

### 4.1 기초 통계
- **연도별 공고 건수**: 2023 / 2024 / 2025 비교 막대그래프 → `figures/count_by_year.png`
- **월별 추이**: 계절성(연말 몰림 등) 확인 → `figures/count_by_month.png`
- **예산 분포**: `presmptPrce` 히스토그램 (로그 스케일) + 중앙값/IQR

### 4.2 카테고리 분포
- **산업별 비율**: 보험 / 금융 / IT / 기타 파이 차트
- **컨설팅 유형 교차표**: `industry × consulting_type` 히트맵

### 4.3 상관 / 공통 출현
- 공고명 상위 TF-IDF 키워드 워드클라우드 (전체 / 산업별 3종)
- 기관별 발주 랭킹 Top 20

---

## ⑤ 중간 인사이트 / 가설

*(데이터 확보 후 1차 검증 결과 갱신)*

예상 가설:
- **H1**: 2023→2025 동안 "AI / 데이터 / 클라우드" 키워드 공고 **비중이 증가** 한다.
- **H2**: 금융·보험 업종에서 "ISP → 구축" 순으로 **발주가 시간차를 두고 이어지는 패턴** 이 존재한다.
- **H3**: 공고명에 "혁신 / 재설계 / 고도화" 키워드가 포함된 공고가 그렇지 않은 공고보다 **평균 예산이 유의하게 크다**.

---

## ⑥ 향후 계획

| 주차 | 작업 | 산출물 |
|------|------|--------|
| W09 | 첨부 PDF/HWP 전수 다운·본문 추출, 뉴스·규제 RSS 결합 | `rfp_text.csv`, `news.csv` |
| W10 | TF-IDF + LDA (sklearn) 토픽 모델링 8~12 토픽 | `topics.json` |
| W11 | 규제 → 발주 시차 분석, Win Strategy 포인트 룰 정의 | 시차 분석 표 |
| W12 | Streamlit 대시보드 고도화 (워드클라우드 · 타임라인 · Win Strategy 추출기) | `app_streamlit.py` |
| W13 | EC2 배포 + CloudFront/Route53 검토 | 공개 URL |
| W14 | 최종 발표 및 라이브 시연 | 발표자료, demo URL |

---

## ⑦ AWS 인프라 구성

### 7.1 아키텍처 (W07 "데이터 허브 = AWS" 5단계 매핑)
```
┌─── 수집 ─────────────┐ ┌─── 저장 ───┐ ┌── 처리 ──┐ ┌── 분석 ──┐ ┌── 시각화 ──┐
│ Lambda + EventBridge │→│ S3 + RDS  │→│ Lambda   │→│ SageMaker│→│ EC2 +      │
│  (나라장터 API 호출) │ │ (원본/가공)│ │ (전처리) │ │  / EC2   │ │ Streamlit  │
└──────────────────────┘ └───────────┘ └──────────┘ └──────────┘ └────────────┘
```

### 7.2 현재 구성 상태
| 서비스 | 상태 | 용도 | 비고 |
|--------|------|------|------|
| AWS 계정 | ✅ 257925264162 | — | 프리티어 |
| IAM 사용자 `hwangdonguk` | ✅ 활성 | CLI/API 접근 | Access Key 발급 완료 |
| EC2 t3.micro `datamining_demo` | ✅ 실행 중 | 분석·Streamlit 서빙 | ap-southeast-2a, Amazon Linux 2023 |
| Security Group `sg-0b7c854caa4d4e287` | ✅ SSH 허용 | 22번 포트, 내 IP(1.220.29.220/32) 한정 | — |
| S3 버킷 `datamining-257925264162-raw` | ✅ 생성 | raw/processed/final 계층 | 퍼블릭 차단, 버저닝 On |
| EventBridge + Lambda | 📅 W11 예정 | 일일 자동 수집 | cron(0 0 ? * MON-FRI *) |
| SageMaker / Colab GPU | 📅 W12 예정 | 토픽 모델링 | Studio 프리티어 |

### 7.3 비용 관리
- AWS Budgets **$5/월 알림 필수 설정** (W07 권고)
- 사용 종료 시 인스턴스 **Terminate** (Stop만 하면 EBS 과금 지속)
- S3 버킷 **Private 고정** (Presigned URL로 임시 공유)
- **NAT Gateway 사용 안 함** ($30+/월 과금 회피)

---

## 부록 A. 리포지토리 구조
```
DataMining/
├── .env                 # API 키 (gitignore)
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── narajangteo/    # *.jsonl (월별 36파일)
│   │   └── rfp_files/      # {bidNtceNo}/*.pdf,hwp
│   └── processed/
│       ├── rfp_meta.csv
│       ├── rfp_text.csv
│       └── rfp_tokens.csv
├── notebooks/
│   └── 01_eda.ipynb
├── reports/
│   ├── midterm.md          # 본 문서
│   ├── midterm.pdf         # 제출본
│   └── figures/*.png
├── src/
│   ├── collect_narajangteo_api.py
│   ├── download_attachments.py
│   ├── preprocess_rfp.py
│   ├── eda.py
│   └── app_streamlit.py
└── scripts/
    └── aws_bootstrap.sh    # S3 버킷 생성·업로드 자동화
```

## 부록 B. 실행 방법
```bash
# 1) 환경
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) 3년치 수집 (월별 분할, 999rows)
python src/collect_narajangteo_api.py \
  --start 20230101 --end 20251231 \
  --kind 용역 --split monthly --rows 999

# 3) 첨부 샘플 다운로드 (500건)
python src/download_attachments.py --sample 500

# 4) 전처리 & 태깅
python src/preprocess_rfp.py

# 5) AWS S3 업로드
bash scripts/aws_bootstrap.sh

# 6) 대시보드 실행
streamlit run src/app_streamlit.py
```
