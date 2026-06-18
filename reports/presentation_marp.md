---
marp: true
theme: uncover
paginate: true
size: 16:9
style: |
  @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@latest/dist/web/variable/pretendardvariable.css');
  :root {
    --ink:#0f172a; --muted:#64748b; --accent:#6366f1; --accent2:#06b6d4;
    --hot:#f43f5e; --line:#e2e8f0; --soft:#eef2ff; --good:#10b981;
  }
  section {
    font-family:'Pretendard Variable',Pretendard,-apple-system,sans-serif;
    font-size:24px; color:#1e293b; background:#fff;
    padding:52px 64px; line-height:1.45; text-align:left; letter-spacing:-.3px;
  }
  h1 { font-size:36px; font-weight:800; color:var(--ink); margin:0 0 18px;
       padding-left:18px; border-left:8px solid var(--accent); letter-spacing:-1px; }
  h2 { font-size:26px; font-weight:700; color:#334155; }
  strong { color:var(--accent); font-weight:700; }
  a { color:var(--accent2); text-decoration:none; }
  table { font-size:20px; border-collapse:collapse; width:100%; margin-top:6px; }
  th { background:var(--ink); color:#fff; padding:8px 13px; text-align:left; font-weight:700; }
  td { padding:7px 13px; border-bottom:1px solid var(--line); }
  tr:nth-child(even) td { background:#f8fafc; }
  blockquote { border-left:5px solid var(--hot); background:#fff1f3; margin:12px 0;
       padding:11px 20px; border-radius:0 12px 12px 0; font-size:21px; color:#9f1239; font-weight:600; }
  .small { font-size:17px; color:var(--muted); }
  li { margin:4px 0; }
  section::after { color:#94a3b8; font-size:14px; font-weight:600; }
  section.lead { background:linear-gradient(135deg,#0f172a 0%,#312e81 55%,#0e7490 100%);
       color:#fff; justify-content:center; padding:66px 80px; }
  section.lead h1 { color:#fff; border:none; padding:0; font-size:52px; line-height:1.12; }
  section.lead h2 { color:#a5b4fc; font-weight:600; }
  section.lead p,section.lead .small { color:#cbd5e1; }
  section.lead strong { color:#67e8f9; }
  .flow { display:flex; align-items:center; gap:9px; margin:22px 0; flex-wrap:wrap; }
  .flow .step { background:var(--soft); color:#3730a3; border:1px solid #c7d2fe;
       border-radius:14px; padding:14px 18px; font-weight:700; font-size:20px; text-align:center; }
  .flow .step b { display:block; font-size:14px; color:#6366f1; font-weight:600; margin-top:3px; }
  .flow .arw { color:#a5b4fc; font-size:24px; font-weight:800; }
  .flow .hot { background:#fff1f3; color:#9f1239; border-color:#fecdd3; }
  .flow .gd { background:#ecfdf5; color:#065f46; border-color:#a7f3d0; }
  .funnel { margin-top:14px; }
  .frow { display:flex; align-items:center; gap:12px; margin:9px 0; }
  .frow .lbl { width:230px; flex:none; font-size:17px; color:#475569; text-align:right; font-weight:600; }
  .frow .ftk { flex:1; display:flex; height:30px; }
  .frow .bar { height:100%; background:linear-gradient(90deg,#6366f1,#06b6d4); border-radius:8px; }
  .frow .num { width:92px; flex:none; font-size:20px; font-weight:800; color:#0f172a; }
  .cmp { margin-top:18px; }
  .crow { margin:16px 0; }
  .crow .ct { font-size:19px; font-weight:700; margin-bottom:6px; }
  .crow .track { display:flex; background:#f1f5f9; border-radius:30px; height:38px; overflow:hidden; }
  .crow .fill { height:100%; border-radius:30px; display:flex; align-items:center;
       justify-content:flex-end; padding-right:14px; color:#fff; font-weight:800; font-size:19px; }
  .fill.news { background:linear-gradient(90deg,#06b6d4,#0ea5e9); }
  .fill.rfp { background:linear-gradient(90deg,#f43f5e,#fb7185); }
  .cards { display:flex; gap:14px; margin:20px 0; flex-wrap:wrap; }
  .card { flex:1; background:linear-gradient(160deg,#f8fafc,#eef2ff); border:1px solid #e0e7ff;
       border-radius:18px; padding:18px 14px; text-align:center; }
  .card .n { font-size:34px; font-weight:800; color:#4338ca; letter-spacing:-1px; }
  .card .l { font-size:15px; color:#64748b; margin-top:4px; font-weight:600; }
  .insight { background:linear-gradient(135deg,#1e1b4b,#0e7490); color:#fff;
       border-radius:16px; padding:18px 24px; margin-top:16px; font-size:22px; }
  .insight b { color:#fde047; }
  .hbars { margin-top:12px; }
  .hb { display:flex; align-items:center; gap:11px; margin:7px 0; }
  .hb .nm { width:150px; flex:none; text-align:right; font-size:17px; font-weight:600; color:#334155; }
  .hb .tk { flex:1; display:flex; background:#f1f5f9; border-radius:8px; height:24px; overflow:hidden; }
  .hb .fv { height:100%; border-radius:8px; background:linear-gradient(90deg,#6366f1,#06b6d4); }
  .hb .fv.alt { background:linear-gradient(90deg,#0891b2,#22d3ee); }
  .hb .fv.ai { background:linear-gradient(90deg,#7c3aed,#a855f7); }
  .hb .pct { width:62px; flex:none; font-size:16px; font-weight:700; color:#334155; }
  /* 좌우 2단 비교 */
  .two { display:flex; gap:16px; margin-top:14px; }
  .two .col { flex:1; border-radius:14px; padding:16px 18px; font-size:19px; }
  .two .before { background:#f8fafc; border:1px solid #e2e8f0; }
  .two .after { background:#ecfdf5; border:1px solid #a7f3d0; }
  .two .col h3 { margin:0 0 8px; font-size:19px; }
  .two .before h3 { color:#64748b; } .two .after h3 { color:#065f46; }
  .two .col li { font-size:17px; }
  /* 가설검정 카드 */
  .htest { display:flex; gap:13px; margin-top:14px; }
  .ht { flex:1; background:#fff; border:1px solid #e2e8f0; border-top:5px solid var(--good);
        border-radius:12px; padding:14px 16px; }
  .ht .q { font-size:16px; color:#475569; font-weight:600; }
  .ht .r { font-size:21px; font-weight:800; color:#0f172a; margin:6px 0 3px; }
  .ht .p { font-size:15px; color:var(--good); font-weight:700; }
  .ht.warn { border-top-color:var(--hot); } .ht.warn .p { color:var(--hot); }
---

<!-- _class: lead -->

# 공공 RFP ×<br>산업 Pain Point 데이터 허브

## 나라장터 IT 발주 분석 · 2023–2025

<br>

데이터마이닝 기말 발표 · **황동욱** (2024720459)
성균관대학교 정보통신대학원 · 2026 Spring

<span class="small">📊 33,860건 · 🏛 3,383 기관 · 🗓 35개월 · ☁ AWS 라이브 배포</span>

---

# 1. 연구 질문 & 발표 범위

**중간 발표의 3대 질문**
1. 산업별 반복 **Pain Point**를 정량화할 수 있는가?
2. Pain Point가 **컨설팅 유형**(ISP·PI·POC·구축) 수요와 연결되는가?
3. **Win Strategy** 핵심 포인트를 자동 추출할 수 있는가?

> 검토의견 4차(P0): "산업 '기타' 88.5% — 분류 자체가 작동하지 않음"

- **기말 = ①·② 검증 + 분류 신뢰성 확보**, ③ Win Strategy는 **실무 서비스로 구현**(p.15)

---

# 2. 중간 → 기말: 무엇이 달라졌나

<div class="two">
  <div class="col before">
    <h3>📋 중간 (현황 기술)</h3>
    <ul>
      <li>산업 '기타' 88.5% — 분류 미작동</li>
      <li>가설 H1~H4 <b>제시만</b>, 검정 0건</li>
      <li>AI 비중 = 키워드 단순 매칭</li>
      <li>분포·Top 등 describe 중심</li>
    </ul>
  </div>
  <div class="col after">
    <h3>🎯 기말 (검증·교정)</h3>
    <ul>
      <li>전처리 고도화 → <b>기타 0%</b></li>
      <li>H1·H3 <b>가설검정 + 카이제곱</b></li>
      <li>AI 정의 <b>엄격 재교정</b> (과대 → 실측)</li>
      <li>제안서 자동생성 <b>서비스 구상</b> (샘플)</li>
    </ul>
  </div>
</div>

> "중간은 결과를 제시했고, 기말은 그 결과가 **맞는지·왜 그런지**를 검증했다"

---

# 3. 받은 피드백에 어떻게 답했나

| 출처 | 핵심 지적 | 본 발표의 답 |
|---|---|---|
| 교수 P0 | 산업 '기타' 88.5% | 전처리 고도화 → **0%** (p.6–7) |
| 교수 Q3 | H3를 t-test로 검증? | **p<10⁻²⁰ 지지** (p.8) |
| 동료 다수 | "기타 많아 교차 안 됨" | 산업×컨설팅 **카이제곱 유의** (p.11) |
| 동료 | 우편향 심해 왜곡 | 평균·중앙 병기 + log1p (p.14) |
| 자체 점검 | AI 비중 과대분류 | **21.7% → 9.0% 교정** (p.12) |

<span class="small">※ 미해결: 첨부 PDF 전수추출·FSC 규제시차(표본 부족)는 한계로 명시(p.17)</span>

---

# 4. 데이터 파이프라인

<div class="flow">
  <div class="step">수집<b>나라장터 API</b></div>
  <div class="arw">→</div>
  <div class="step hot">정제<b>핵심 기여</b></div>
  <div class="arw">→</div>
  <div class="step gd">검증<b>가설·카이제곱</b></div>
  <div class="arw">→</div>
  <div class="step">서비스<b>제안서 자동생성</b></div>
  <div class="arw">→</div>
  <div class="step">배포<b>AWS · 라이브</b></div>
</div>

| 단계 | 스택 |
|---|---|
| 수집 | 나라장터 OpenAPI · 월별 분할 · 지수 백오프 |
| 저장 | AWS S3 (`datamining-…-raw`) |
| 전처리 | Python · 키워드 색인(단어경계) · 기관 매핑 · 중복 제거 |
| 분석·서비스 | scipy 검정 · Streamlit · Claude API |

---

# 5. 전처리 고도화 — 정제 퍼널

<div class="funnel">
  <div class="frow"><span class="lbl">전체 용역 공고</span><div class="ftk"><div class="bar" style="flex-grow:458421"></div></div><span class="num">458,421</span></div>
  <div class="frow"><span class="lbl">① IT 색인 (개발 다의어 제외)</span><div class="ftk"><div class="bar" style="flex-grow:53909"></div><div style="flex-grow:404512"></div></div><span class="num">53,909</span></div>
  <div class="frow"><span class="lbl">② 영문토큰 단어경계</span><div class="ftk"><div class="bar" style="flex-grow:53229"></div><div style="flex-grow:405192"></div></div><span class="num">53,229</span></div>
  <div class="frow"><span class="lbl">③ IT 비연관 도메인 제외</span><div class="ftk"><div class="bar" style="flex-grow:52992"></div><div style="flex-grow:405429"></div></div><span class="num">52,992</span></div>
  <div class="frow"><span class="lbl">④ 논리적 중복 제거</span><div class="ftk"><div class="bar" style="flex-grow:33860"></div><div style="flex-grow:424561"></div></div><span class="num">33,860</span></div>
</div>

<span class="small">+ ⑤ 산업 = 수요기관 기반 10범주 → <b>기타 0건</b> &nbsp;|&nbsp; ⑥ 사업유형 16범주 → 기타 7.5%</span>

> 분류축을 '공고명 키워드' → '수요기관 성격'으로 교체해 '기타'를 구조적으로 해소

---

# 6. 핵심 버그 — 영문 토큰 부분일치

`AI` · `SW` 키워드가 **영어 단어 내부**에 박혀 오색인:

<div class="flow">
  <div class="step hot">m<b style="display:inline;color:#9f1239">AI</b>ntenance</div>
  <div class="step hot">F<b style="display:inline;color:#9f1239">AI</b>r</div>
  <div class="step hot">MRI&nbsp;Br<b style="display:inline;color:#9f1239">AI</b>n</div>
  <div class="step hot">LG&nbsp;<b style="display:inline;color:#9f1239">AI</b>mers</div>
  <div class="step hot">pa<b style="display:inline;color:#9f1239">SSW</b>ord</div>
</div>

- 산업 '기타' 258건 중 **102건이 이 오탐** (MRI 판독·해커톤·박람회…)
- **해결**: 영문 토큰 → 단어경계(`\b`) 매칭 / 한글 키워드 → 부분일치 유지

> "데이터 양은 많은데 결론이 약해지는" 오염을 근본 차단

---

# 7. 데이터 규모 — 산업별 한눈에

<span class="small"><b>33,860건</b> · 3,383 기관 · 35개월(2023.01~2025.11) · 10 산업 × 16 유형</span>

| 산업 | 건수 | 비중 | 중앙예산 | AI비중 | 대표 유형 |
|---|--:|--:|--:|--:|---|
| 행정·공공 | 14,048 | 41.5% | 1.36억 | 6.9% | 유지보수 |
| 교육·연구 | 6,317 | 18.7% | 0.91억 | 14.4% | 유지보수 |
| 농림·수산·환경 | 3,151 | 9.3% | 1.18억 | 5.4% | 유지보수 |
| 국토·교통·건설 | 2,553 | 7.5% | 1.30억 | 4.9% | 유지보수 |
| 산업·에너지 | 1,861 | 5.5% | 0.91억 | 12.4% | 유지보수 |
| 문화·관광·체육 | 1,712 | 5.1% | 1.36억 | 5.9% | 유지보수 |
| 의료·보건 | 1,707 | 5.0% | 1.09억 | 10.5% | 유지보수 |
| 정보·통신 | 1,494 | 4.4% | 1.72억 | **22.3%** | 유지보수 |
| 금융 | 702 | 2.1% | **3.18억** | 3.0% | 유지보수 |
| 보험 | 315 | 0.9% | **3.09억** | 6.0% | 구축 |

> 건수는 **행정·공공**이 압도하지만, 건당 예산은 **금융·보험(3억대)** 이 최고 · AI 비중은 **정보·통신(22%)** 이 최고 — 산업마다 성격이 다름

---

# 8. 가설 검정 — 무엇을, 어떻게 확인했나

<div class="htest">
  <div class="ht">
    <div class="q">❶ AI 발주가 해마다 늘었나?</div>
    <div class="r">네 — 2년 새 약 2배 ↑</div>
    <div class="p">검증법 · 연도별 추세 비교 (6%→13%)</div>
  </div>
  <div class="ht">
    <div class="q">❷ '고도화' 사업은 예산이 더 큰가?</div>
    <div class="r">네 — 평균 1.3배 더 큼</div>
    <div class="p">검증법 · 두 집단 평균 차이 (t-검정)</div>
  </div>
  <div class="ht">
    <div class="q">❸ 산업마다 원하는 사업유형이 다른가?</div>
    <div class="r">네 — 뚜렷하게 다름</div>
    <div class="p">검증법 · 교차분석 (카이제곱 검정)</div>
  </div>
</div>

<span class="small">세 가설 모두 <b>통계적으로 유의</b> = "우연으로 보기 어렵다" (t-검정·카이제곱으로 확인)</span>

> 중간발표 때 '계획'만 세운 가설을, 기말은 **표준 통계기법으로 검증 완료**

---

# 9. 어느 산업이 IT를 발주하나 (전체)

<div class="hbars">
  <div class="hb"><span class="nm">행정·공공</span><div class="tk"><div class="fv" style="flex-grow:415"></div><div style="flex-grow:585"></div></div><span class="pct">41.5%</span></div>
  <div class="hb"><span class="nm">교육·연구</span><div class="tk"><div class="fv" style="flex-grow:187"></div><div style="flex-grow:813"></div></div><span class="pct">18.7%</span></div>
  <div class="hb"><span class="nm">농림·수산·환경</span><div class="tk"><div class="fv" style="flex-grow:93"></div><div style="flex-grow:907"></div></div><span class="pct">9.3%</span></div>
  <div class="hb"><span class="nm">국토·교통·건설</span><div class="tk"><div class="fv" style="flex-grow:75"></div><div style="flex-grow:925"></div></div><span class="pct">7.5%</span></div>
  <div class="hb"><span class="nm">산업·에너지</span><div class="tk"><div class="fv" style="flex-grow:55"></div><div style="flex-grow:945"></div></div><span class="pct">5.5%</span></div>
  <div class="hb"><span class="nm">문화·관광·체육</span><div class="tk"><div class="fv" style="flex-grow:51"></div><div style="flex-grow:949"></div></div><span class="pct">5.1%</span></div>
  <div class="hb"><span class="nm">의료·보건</span><div class="tk"><div class="fv" style="flex-grow:50"></div><div style="flex-grow:950"></div></div><span class="pct">5.0%</span></div>
  <div class="hb"><span class="nm">정보·통신</span><div class="tk"><div class="fv" style="flex-grow:44"></div><div style="flex-grow:956"></div></div><span class="pct">4.4%</span></div>
  <div class="hb"><span class="nm">금융</span><div class="tk"><div class="fv" style="flex-grow:21"></div><div style="flex-grow:979"></div></div><span class="pct">2.1%</span></div>
  <div class="hb"><span class="nm">보험</span><div class="tk"><div class="fv" style="flex-grow:9"></div><div style="flex-grow:991"></div></div><span class="pct">0.9%</span></div>
</div>

<span class="small">전체 33,860건 기준 · 수요기관 성격 기반 10범주</span>

> **행정·공공(41.5%) + 교육·연구(18.7%)** 가 공공 IT 발주의 60% — 발주량은 공공·교육이 주도

---

# 10. Q①의 답 — 그중 AI는 어느 산업이 발주하나

<div class="hbars">
  <div class="hb"><span class="nm">정보·통신</span><div class="tk"><div class="fv ai" style="flex-grow:223"></div><div style="flex-grow:777"></div></div><span class="pct">22.3%</span></div>
  <div class="hb"><span class="nm">교육·연구</span><div class="tk"><div class="fv ai" style="flex-grow:144"></div><div style="flex-grow:856"></div></div><span class="pct">14.4%</span></div>
  <div class="hb"><span class="nm">산업·에너지</span><div class="tk"><div class="fv ai" style="flex-grow:124"></div><div style="flex-grow:876"></div></div><span class="pct">12.4%</span></div>
  <div class="hb"><span class="nm">의료·보건</span><div class="tk"><div class="fv ai" style="flex-grow:105"></div><div style="flex-grow:895"></div></div><span class="pct">10.5%</span></div>
  <div class="hb"><span class="nm">행정·공공</span><div class="tk"><div class="fv ai" style="flex-grow:69"></div><div style="flex-grow:931"></div></div><span class="pct">6.9%</span></div>
  <div class="hb"><span class="nm">금융</span><div class="tk"><div class="fv ai" style="flex-grow:30"></div><div style="flex-grow:970"></div></div><span class="pct">3.0%</span></div>
</div>

<span class="small">엄격 정의 기준 · 사업유형별: 연구개발 36.4% · POC/실증 33.8% · 컨설팅 17.3%</span>

> 발주 <b>'량'</b>은 행정·공공이 1위였지만, AI <b>'비중'</b>은 <b>정보·통신·교육연구</b>가 주도 — 발주량 1위 행정·공공은 AI 6.9%로 하위 (양 ↔ AI 성숙도는 별개)

---

# 11. Q②의 답 — 산업 × 컨설팅 유형 연결

| 산업 \ 유형 | 유지보수 | 구축 | 고도화 | 컨설팅 |
|---|---|---|---|---|
| 행정·공공 | **6,360** | 2,043 | 1,266 | 598 |
| 교육·연구 | 1,906 | **1,643** | 811 | 371 |
| 농림·수산·환경 | 1,121 | 486 | 513 | 168 |
| 국토·교통·건설 | 806 | 518 | 398 | 203 |

- 행정·공공 = **유지보수 압도** / 교육·연구 = **구축(신규 개발) 비중↑**
- 검증법 · 교차분석(카이제곱) → **산업마다 필요한 사업이 뚜렷이 다름** (우연 아님)

> 산업을 알면 **어떤 사업(유지보수냐 신규구축이냐)을 원하는지 예측 가능** — 제안 전략의 근거

---

# 12. AI 순수성 — 정의를 교정하다 (자체 검증)

기존 분류는 `데이터`·`클라우드`만으로 ai-pure 판정 → **58.6%가 비(非)AI 혼입**

<div class="cmp">
  <div class="crow"><div class="ct">📰 뉴스 (담론) — 엄격 정의</div>
    <div class="track"><div class="fill news" style="flex-grow:298">29.8%</div><div style="flex-grow:702"></div></div></div>
  <div class="crow"><div class="ct">📋 RFP (실제 발주) — 엄격 정의</div>
    <div class="track"><div class="fill rfp" style="flex-grow:90">9.0%</div><div style="flex-grow:910"></div></div></div>
</div>

<div class="insight">
💡 격차는 느슨(3.0배)→엄격(<b>3.3배</b>) <b>정의를 바꿔도 유지</b> = 강건한 결론 —<br>
"AI 담론 ↔ 조달 현실"의 정량적 격차 <span class="small" style="color:#cbd5e1">(AI 분류: 자체 키워드 기준 / 민감도 분석)</span>
</div>

---

# 13. IT 사업유형 — 16범주 전체 순위

| # | 유형 | 비중 | # | 유형 | 비중 |
|--|---|---|--|---|---|
| 1 | 유지보수/운영 | **37.6%** | 9 | 연구개발/R&D | 1.8% |
| 2 | 구축/개발 | 17.7% | 10 | 임차/구독 | 1.4% |
| 3 | 고도화/개선 | 11.9% | 11 | 데이터/AI | 1.1% |
| 4 | 기타 | 7.5% | 12 | POC/실증 | 1.1% |
| 5 | 컨설팅/분석 | 5.8% | 13 | PMO | 1.1% |
| 6 | 보안 | 5.5% | 14 | 교육/홍보 | 0.9% |
| 7 | 감리 | 4.5% | 15 | 시험/인증 | 0.5% |
| 8 | ISP/계획 | 1.8% | 16 | BPR/PI | 0.0% |

> 상위 3개(**유지보수·구축·고도화 = 67%**)에 집중 — 신규 구축은 18%뿐, ISP·R&D·AI 등은 각 2% 미만

---

# 14. AI 예산의 역설

<div class="cards">
  <div class="card"><div class="n">9,000만</div><div class="l">AI 사업 1건 예산</div></div>
  <div class="card"><div class="n">1.27억</div><div class="l">비-AI 사업 1건 예산</div></div>
  <div class="card"><div class="n">약 1.4배 ↓</div><div class="l">AI가 더 작음 · 우연 아님</div></div>
</div>

> **"미래 기술인데 정작 예산은 더 작다"** — AI 공고는 건수도 적고(9%), 1건당 예산도 비-AI보다 작음 = 아직 **소규모 실험(PoC) 단계**

<span class="small">예산은 '1건당 중앙값' 기준 · 통계적으로 확실(우연일 확률 사실상 0)</span>

---

# 15. 실무 서비스 구상 — 제안서 자동생성 (Q③ 확장)

<div class="flow">
  <div class="step">신규 공고<b>나라장터 인입</b></div>
  <div class="arw">→</div>
  <div class="step gd">분류 엔진<b>산업·유형·AI·키워드</b></div>
  <div class="arw">→</div>
  <div class="step gd">담당자 매칭<b>인적자산 기반</b></div>
  <div class="arw">→</div>
  <div class="step hot">Claude<b>가안 제안서</b></div>
</div>

- 적합 공고 탐지 → **회사 인적자산 기반 담당자 매칭** → 과거 제안서 목차로 **어필 포인트**
- Claude가 **목차·핵심 메시지·차별화 전략**이 담긴 **가안 제안서 초안** 생성
- 제안서 1건 작성 **수일 → 수분** 단축 (중간발표 기대효과의 확장 방향)

<span class="small">※ 담당자 매칭은 회사 인적자산 DB 기반 — 본 발표는 <b>대략적 구성·샘플 화면</b> 수준, 실구현은 향후</span>

---

# 16. AWS 인프라 & 대시보드

<div class="flow">
  <div class="step">로컬 수집<b>Python</b></div>
  <div class="arw">→</div>
  <div class="step">S3<b>raw·processed</b></div>
  <div class="arw">→</div>
  <div class="step">EC2<b>Streamlit · systemd</b></div>
  <div class="arw">→</div>
  <div class="step hot">Cloudflare<b>공개 URL</b></div>
</div>

- Streamlit 탭: 개요 · 월별 · 키워드(색인기준 공개) · **AI 순수성(엄격)** · 공고검색 · **제안서 생성**
- 영구 실행(systemd) + 공개 터널 → 모바일 접속 가능

🌐 **https://now-metallic-bringing-title.trycloudflare.com**

---

# 17. 결론 · 한계 · 향후

**결론**
- 전처리 고도화로 '기타' **88.5%→0%**, H1·H3 **가설검정 지지**, 산업×유형 연관 확인
- AI는 **담론(30%) ↔ 발주(9%) 3.3배 격차** + 건당 예산도 작음 (정의 교정 후 강건)

**한계** *(솔직히)*
- 산업축 = 수요기관 기반(공고명 기반 아님) · 첨부 PDF 173건 샘플 · FSC RSS 30건은 시차분석 표본 부족

**향후**
- PDF 본문 전수추출 + LDA · 규제→발주 Granger · 제안서 생성 정확도 평가셋 구축

---

# 18. 예상 질문 (Q&A)

> **Q. '기타 0%'는 분류를 잘한 건가, 축을 바꾼 건가?**
→ 후자. 공고명 키워드로는 한계 → 수요기관 성격으로 재정의. 한계도 명시.

> **Q. AI 9%는 너무 낮지 않나?**
→ 엄격 정의(핵심 AI 키워드만). 느슨하면 21.7%이나 담론 격차는 두 정의 모두 3배대로 강건.

> **Q. 예산 t-test가 인과인가?**
→ 아니오. 연관(association). 공고기관·연도 통제한 회귀는 향후 과제.

---

<!-- _class: lead -->

# 감사합니다

**GitHub** github.com/hwangdongwuk/DataMining
**대시보드** trycloudflare 공개 URL (라이브)
**핵심** 기타 0% · H1·H3 검정 · AI 격차 3.3배 · 제안서 자동생성

황동욱 · 데이터마이닝 2026
