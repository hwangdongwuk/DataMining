# 데이터마이닝 중간 보고서

- 학번/이름: 2024720459 황동욱
- 과목: 성균관대학원 2-1 데이터마이닝
- 작성일: 2026-04-22
- GitHub: https://github.com/hwangdongwuk/DataMining

---

## ① 프로젝트 개요

### 주제
공공 RFP × 산업뉴스 × 규제 데이터 기반 산업별 Pain Point 분석 및 컨설팅 프로세스(ISP·PI·POC·BPR)별 제안 전략 자동화 데이터 허브 구축

### 연구 질문
1. 나라장터 RFP 본문·산업 뉴스·규제 공시를 통합 분석하면 산업별 반복 Pain Point를 정량화할 수 있는가?
2. 그 Pain Point를 ISP·PI·POC·BPR 중 어느 컨설팅 유형 수요와 연결되는지 자동 분류할 수 있는가?
3. 이를 통해 제안 전략(Win Strategy) 핵심 포인트를 자동 추출해 제안서 작성에 활용할 수 있는가?

### 선정 이유 (W02 피드백 반영)
보험·금융 IT 기획/PM 실무에서 제안서 작성 시 Pain Point 파악·Win Strategy 수립에 수일이 소요되는 비효율을 데이터 파이프라인으로 자동화. 수업의 허브 프로젝트 방향성과 부합하며, 최종 Streamlit 허브는 제안팀 실무 도구로 전환 가능.

*(W02 동료 피드백 반영 내역: TBD — 피드백 내용 기록 후 반영 계획 작성 예정)*

---

## ② 데이터 수집 결과

> **작성 예정** — 수집 실행 후 아래 항목 채움

- 수집 규모: (예: 나라장터 공고 건수, PDF 건수, 뉴스 건수)
- 수집 기간: 2023~2025
- 샘플 스냅샷: `data/processed/rfp_meta.csv` 상위 10행
- 수집 코드 경로: `src/collect_narajangteo.py`, `src/collect_news.py`, `src/collect_fss_rss.py`

---

## ③ 데이터 전처리

> **작성 예정**

- 결측치 처리 방식
- 이상치/중복 공고 처리
- PDF 섹션 파싱 성공률
- 전·후 레코드 수 비교 표

---

## ④ 탐색적 데이터 분석(EDA)

> **작성 예정**

- 산업별 공고 건수 분포
- 컨설팅 유형별(ISP/PI/POC/BPR/PMO) 비율
- 연도별 발주 추이
- 주요 키워드 상관관계 히트맵

---

## ⑤ 중간 인사이트

> **작성 예정**

- 발견한 패턴
- 초기 가설

---

## ⑥ 향후 계획

| 주차 | 작업 |
|------|------|
| W07~W08 | 수집 파이프라인 완성 (나라장터 API, PDF 다운로드, 뉴스 API) |
| W09 | 전처리·형태소 분석·컨설팅 유형 태깅 |
| W10 | TF-IDF · LDA 토픽모델링 |
| W11 | 규제→발주 시차 분석, Win Strategy 추출 |
| W12~W13 | Streamlit 대시보드 개발 |
| W14 | Streamlit Cloud 배포, 최종 보고서 |
| W15 | 최종 발표 |

---

## ⑦ AWS 인프라 구성 (선택)

현재 계획: Google Drive + Streamlit Cloud 기반으로 진행.
AWS 전환 시 고려 구성:
- S3: 원본 PDF·뉴스 JSON 저장
- Lambda + EventBridge: 일일 수집 스케줄링
- RDS(PostgreSQL) 또는 DynamoDB: 공고 메타·태깅 결과 저장
- ECS/App Runner: Streamlit 앱 배포
- CloudWatch: 파이프라인 모니터링

> 최종 채택 여부는 W12 이전 결정.

---

## 부록

- 계획서 원본: `18_W02_데이터마이닝_2024720459_황동욱_final.docx` (W02 활동지)
- 저장소 구조: README.md 참조
