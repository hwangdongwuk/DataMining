---
title: 공공 RFP × 산업 Pain Point 데이터 허브
subtitle: 데이터마이닝 중간 발표 · 황동욱 · 2024720459
date: 2026-04-23
---

# 1 · 문제 정의

## 제안서 작성의 반복 비효율

- GA · 보험 · 금융 IT 기획/PM 실무에서 제안서 작성 시
  **고객 Pain Point 파악 + Win Strategy 수립에 수일 소요**
- 분석은 사람이 수작업 — 매번 처음부터
- **데이터로 자동화하면 제안팀 실무 시간을 획기적으로 단축** 가능

---

# 2 · 연구 질문

1. 나라장터 RFP · 산업 뉴스 · 규제 공시를 통합 분석하면
   **산업별 반복 Pain Point** 를 정량화할 수 있는가?
2. 도출된 Pain Point가 **ISP · PI · POC · BPR · PMO** 중
   어느 컨설팅 유형 수요와 연결되는지 자동 분류할 수 있는가?
3. **Win Strategy 핵심 포인트** 를 자동 추출해 제안서 작성에 활용할 수 있는가?

W06 피드백 반영 공식: **[대상] + [변수] + [범위] + [방향성]**

---

# 3 · 데이터 소스

| 소스 | 유형 | 건수(잠정) |
|------|------|-----------|
| 나라장터 입찰공고 (용역) | REST API | **312,037건** |
| 첨부 PDF / HWP (샘플) | 파일 다운로드 | 198건 |
| 금감원 RSS + 네이버 뉴스 API | RSS / API | (W10 예정) |

- 기간 **2023-01-01 ~ 2025-12-31** · 수요기관 **14,962곳**
- Key-based Join: `bidNtceNo`

---

# 4 · 파이프라인 (AWS 데이터허브 매핑)

```
수집          저장          처리           분석          시각화
─────         ─────         ─────          ─────         ─────
requests  →   S3 + 로컬  →  pdfplumber  →  TF-IDF    →   Streamlit
tqdm          (2.1 GB)      hwp5txt         sklearn.LDA    plotly
                            kiwipiepy
```

- 월별 분할 수집(36개월) · 지수 백오프 재시도 · 999rows/page
- Python 3.14 호환 이슈로 `konlpy` / `gensim` → **`kiwipiepy` + `sklearn LDA`**

---

# 5 · 수집 결과 — 산업 분포

![산업 분포](figures/03_industry_pie.png){ width=55% }

- 기타 89.2 % · IT 8.3 % · 보험 2.2 % · 금융 0.4 %
- "기타" 비중이 큼 → 산업 태그 룰 보강 필요 (W09~W10)

---

# 6 · 컨설팅 유형 교차 분석

![industry × consulting](figures/04_industry_consulting_heatmap.png){ width=80% }

- **구축 23,236건** · PMO 4,510 · POC 1,515 · ISP 448
- IT 업종은 구축 중심, PMO 수요는 서울시·국토교통부 발주가 견인

---

# 7 · 공고명 키워드 Top 30

![title keywords](figures/07_title_keywords.png){ width=85% }

- 상위: **시스템 · 구축 · 유지관리 · 운영 · 점검**
- 제안서 자동화에서 높은 빈도 키워드가 곧 Pain Point 후보군

---

# 8 · AWS 인프라 (현재 구성)

| 서비스 | 상태 |
|--------|------|
| EC2 t3.micro `datamining_demo` | ✅ running (13.239.237.95) |
| S3 `datamining-257925264162-raw` | ✅ 25 objects / 2.09 GB |
| IAM `hwangdonguk` | ✅ Access Key 발급 · S3FullAccess |
| Security Group `sg-0b7c854caa4d4e287` | ✅ SSH 22 + Streamlit 8501 |
| Budgets 알림 $5/월 | ✅ 설정 |

프리티어 내 운영, 비용 $0~5/월 예상.

---

# 9 · 라이브 데모 (Streamlit)

```
http://13.239.237.95:8501
```

- 탭 ① 개요 · ② 월별 추이 · ③ 키워드 · ④ 공고 검색
- 좌측 필터: 연도 · 산업 · 컨설팅 유형 · 키워드 부분일치

*(시연: 연도 필터 → 보험 산업 → ISP 교차 → Top 키워드 확인)*

---

# 10 · 향후 계획

| 주차 | 작업 |
|------|------|
| W09 | 첨부 PDF/HWP 전수 다운·본문 추출, 금감원 RSS + 네이버 뉴스 결합 |
| W10 | TF-IDF + sklearn LDA 토픽모델링 (8~12 토픽) |
| W11 | 규제 → 발주 시차 분석 · Win Strategy 룰 정의 |
| W12 | Streamlit 대시보드 고도화 (Win Strategy 추출기) |
| W13 | EC2 배포 + 도메인 · HTTPS |
| W14 | 최종 발표 · 라이브 시연 |

- GitHub: https://github.com/hwangdongwuk/DataMining
