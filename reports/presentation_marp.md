---
marp: true
theme: uncover
paginate: true
size: 16:9
style: |
  :root {
    --bg:#0f172a; --bg2:#1e293b; --ink:#0f172a; --muted:#64748b;
    --accent:#6366f1; --accent2:#06b6d4; --hot:#f43f5e; --line:#e2e8f0;
  }
  section {
    font-family:'Apple SD Gothic Neo','Pretendard','Noto Sans KR',sans-serif;
    font-size:25px; color:#1e293b; background:#ffffff;
    padding:60px 70px; line-height:1.5; text-align:left;
  }
  h1 { font-size:38px; font-weight:800; color:#0f172a; margin:0 0 24px;
       padding-left:18px; border-left:8px solid var(--accent); letter-spacing:-.5px; }
  h2 { font-size:27px; font-weight:700; color:#334155; }
  strong { color:var(--accent); font-weight:800; }
  a { color:var(--accent2); }
  table { font-size:21px; border-collapse:collapse; width:100%; margin-top:8px; }
  th { background:#0f172a; color:#fff; padding:9px 14px; text-align:left; font-weight:700; }
  td { padding:8px 14px; border-bottom:1px solid var(--line); }
  tr:nth-child(even) td { background:#f8fafc; }
  blockquote { border-left:5px solid var(--hot); background:#fff1f3; margin:14px 0;
       padding:12px 20px; border-radius:0 10px 10px 0; font-size:22px; color:#9f1239; }
  .small { font-size:18px; color:var(--muted); }
  ul { margin-top:6px; }
  li { margin:5px 0; }
  section::after { color:#94a3b8; font-size:14px; }
  /* 표지/마무리 */
  section.lead { background:linear-gradient(135deg,#0f172a 0%,#312e81 55%,#0e7490 100%);
       color:#fff; justify-content:center; text-align:left; padding:70px 80px; }
  section.lead h1 { color:#fff; border:none; padding:0; font-size:52px; line-height:1.15; }
  section.lead h2 { color:#a5b4fc; font-weight:600; margin-top:4px; }
  section.lead p, section.lead .small { color:#cbd5e1; }
  section.lead strong { color:#67e8f9; }
  /* 강조 카드 */
  .kpi { display:inline-block; background:#eef2ff; color:#3730a3; font-weight:800;
       padding:4px 14px; border-radius:30px; font-size:20px; margin:2px 4px; }
---

<!-- _class: lead -->

# 공공 RFP ×<br>산업 Pain Point 데이터 허브

## 나라장터 IT 발주 분석 · 2023–2025

<br>

데이터마이닝 중간과제 · **황동욱**
성균관대학교 정보통신대학원 · 2026 Spring

<span class="small">📊 33,860건 · 🏛 수요기관 3,383곳 · 🗓 35개월 · ☁ AWS 배포</span>

---

# 1. 연구 질문 & 배경

- **연구 질문**: 공공부문은 *어느 산업이*, *어떤 유형의* IT 사업을, *AI는 얼마나* 발주하는가?
- **데이터 소스 (4종 결합)**: 나라장터 OpenAPI · 네이버 뉴스 · FSC RSS · 첨부 RFP
- **중간 검토의견서 4차 핵심 지적 (P0)**
  > "산업 분류 '기타' 88.5% — 분류 자체가 작동하지 않음"
- 본 발표 = **이 피드백을 전처리 고도화로 해결한 과정과 결과**

---

# 2. 데이터 파이프라인

수집 → **정제(핵심)** → 분석 → 시각화(대시보드) → AWS 배포

| 단계 | 도구 |
|---|---|
| 수집 | 나라장터 OpenAPI (`getBidPblancListInfoServc`), 월별 분할·백오프 |
| 저장 | AWS S3 (`datamining-…-raw`) |
| 전처리 | Python · 키워드 색인 · 기관 매핑 · 중복 제거 |
| 분석 | 산업·유형·AI 분류, EDA |
| 시각화 | Streamlit (EC2, systemd 영구 실행) |

---

# 3. 전처리 고도화 — 6단계 (핵심 기여)

| # | 처리 | 효과 |
|---|---|---|
| 1 | 업무구분 IT 색인 (용역, 공사·외자 제외) | 458K → 53K |
| 2 | 단독 "개발" 다의어 제외 (IT 맥락만) | 기타 88.5%→30.8% |
| 3 | **영문토큰 단어경계 매칭** (AI/SW/IT) | air·fair·brain 오탐 제거 |
| 4 | IT 비연관 도메인 제외 (행사·의료·건축) | 비IT 배제 |
| 5 | **산업 = 수요기관 기반 10범주** | 기타 **0건** |
| 6 | 논리적 중복 제거 (제목+기관+추정가) | 48.7K → **33.9K** |

---

# 4. 핵심 버그 — 영문 토큰 부분일치

- `AI` 키워드가 **영어 단어 내부**에 박혀 오색인
  - m**ai**ntenance · F**ai**r · MRI Br**ai**n · LG **Ai**mers · ch**ai**n
  - `SW` → pa**ssw**ord · Gene**sW**ell
- 산업 기타 258건 중 **102건이 이 오탐**
- **해결**: 영문 토큰을 단어경계(`\b`) 매칭으로 → 한글 키워드는 부분일치 유지

<span class="small">→ "데이터 양은 많은데 결론이 약해지는" 오염을 근본 차단</span>

---

# 5. 데이터 규모

- **공고 33,860건** (중복 제거 후) · 수요기관 **3,383곳**
- 기간 **2023-01 ~ 2025-11 (35개월 연속)**
- 추정가격: 평균 **5.85억** · 중앙 **1.22억** (우편향, sentinel 정제)

![w:620](figures/02_count_by_month.png)

---

# 6. 산업별 분포 (수요기관 기반 10범주)

![w:560](figures/03_industry_pie.png)

- 행정·공공 41% · 교육·연구 19% · 농림수산환경 9% …
- **'기타' 0건** — 울산과학기술원→교육, 한국거래소→금융 식 논리 배정

---

# 7. IT 사업유형 (16범주)

| 유형 | 비중 | 유형 | 비중 |
|---|---|---|---|
| 유지보수/운영 | 37.6% | 감리 | 4.5% |
| 구축/개발 | 17.7% | ISP/계획 | 1.8% |
| 고도화/개선 | 11.9% | 연구개발 | 1.8% |
| 컨설팅/분석 | 5.8% | 임차/구독 | 1.4% |
| 보안 | 5.5% | 기타 | 7.5% |

→ 공공 IT 지출의 **절반 이상이 유지보수·운영·고도화** (신규 구축은 18%)

---

# 8. AI 순수성 분석 (KAIB2026 기준)

- **방법론 차용**: ETRI KAIB2026 (국가 AI 재정계획) ai-pure / non-ai 키워드
- 발주(RFP) ai-pure **21.7%** vs 뉴스(담론) ai-pure **66.1%**

| 소스 | ai-pure | non-ai |
|---|---|---|
| 뉴스 (담론) | **66.1%** | 33.9% |
| RFP (실제 발주) | 21.7% | **78.3%** |

> **핵심 인사이트**: 미디어는 AI 중심, 실제 공공 조달은 일반 정보화·SI 대다수 — **"AI 관심 ↔ 조달 현실"의 정량적 격차**

---

# 9. 수요기관 Top

![w:720](figures/06_top_institutions.png)

서울특별시 · 한국지능정보사회진흥원 · 한국인터넷진흥원 · 한국건설기술연구원 · 국토교통부

---

# 10. AWS 인프라 & 대시보드

- **EC2** (t3.micro, ap-southeast-2) + **S3** + **IAM**
- Streamlit 5탭: 개요 · 월별 · 키워드(색인기준) · **AI 순수성** · 검색
- systemd 영구 실행 + Cloudflare 공개 터널

**🌐 https://now-metallic-bringing-title.trycloudflare.com**

![w:520](figures/11_aws_architecture.png)

---

# 11. 결론 & 향후 계획

**결론**
- 전처리 고도화로 산업 기타 88.5% → **0%**, 33,860건 정제 데이터 구축
- 공공 IT = 유지보수·운영 중심 / AI는 담론 대비 발주 격차 큼

**향후 계획**
- 첨부 PDF/HWP 본문 전수 추출 + LDA 토픽모델링
- 업무구분 '물품' 확장 · H3 가설 t-test 검증
- 뉴스 산업축 정합 (수요기관 기반과 통일)

---

<!-- _class: lead -->

# 감사합니다

**GitHub** github.com/hwangdongwuk/DataMining
**대시보드** trycloudflare 공개 URL
**데이터** 33,860건 · 산업 10범주 · 사업유형 16범주

황동욱 · 데이터마이닝 2026
