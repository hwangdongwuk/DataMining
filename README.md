# DataMining

성균관대학원 2026학년도 1학기(2-1) **데이터마이닝** 프로젝트 저장소

- 학번: 2024720459
- 이름: 황동욱

## 프로젝트 주제

공공 RFP × 산업뉴스 × 규제 데이터 기반 **산업별 Pain Point 분석** 및
컨설팅 프로세스(ISP·PI·POC·BPR)별 **제안 전략 자동화 데이터 허브** 구축

## 연구 질문

1. 나라장터 RFP 본문·산업 뉴스·규제 공시를 통합 분석하면 산업별 반복 Pain Point를 정량화할 수 있는가?
2. 그 Pain Point를 ISP·PI·POC·BPR 중 어느 컨설팅 유형 수요와 연결되는지 자동 분류할 수 있는가?
3. 이를 통해 제안 전략(Win Strategy) 핵심 포인트를 자동 추출해 제안서 작성에 활용할 수 있는가?

## 선정 이유

보험·금융 IT 기획/PM 실무에서 제안서 작성 시 고객 Pain Point 파악·Win Strategy 수립에 수일이 소요되는 문제를 데이터 파이프라인으로 자동화. 최종 Streamlit 허브는 제안팀 실무 도구로 즉시 전환 가능.

## 데이터 소스

| # | 소스 | 유형 | 접근 |
|---|------|------|------|
| 1 | 나라장터 입찰공고 OpenAPI | Open API | data.go.kr, `getBidPblancListInfoServc` |
| 2 | 나라장터 첨부 PDF/HWP | 파일 다운로드 | API `fileUrl` → requests → pdfplumber |
| 3 | 금감원 RSS + 네이버 뉴스 API | RSS / API | fss.or.kr RSS, 네이버 검색 API |

## 파이프라인 (5단계)

| 단계 | 계획 | 도구 |
|------|------|------|
| ① 수집 | 나라장터 3년치(2023~2025) 용역공고 메타 + 첨부 PDF + 금감원 RSS + 뉴스 API | requests, feedparser, pandas |
| ② 저장 | Drive `01_raw/`·`02_processed/`, GitHub에 코드·메타 CSV | pandas, sqlite3, Drive API |
| ③ 처리 | pdfplumber 텍스트 추출, 정규식 섹션 파싱, Mecab 형태소 분석, 컨설팅 유형 키워드 태깅 | pdfplumber, konlpy, re |
| ④ 분석 | TF-IDF 산업·유형별 Pain Point 추출, LDA 토픽모델링(8~12 토픽), 규제→발주 시차 분석 | sklearn, gensim, statsmodels |
| ⑤ 시각화 | Streamlit 대시보드(워드클라우드·수요맵·타임라인·Win Strategy 추출) + Streamlit Cloud 배포 | plotly, wordcloud, streamlit |

## 디렉토리 구조

```
DataMining/
├── data/
│   ├── raw/          # 원본 데이터(GitHub 미업로드)
│   └── processed/    # 전처리 결과
├── notebooks/        # Colab/Jupyter 노트북
├── src/              # 수집·전처리·분석 코드
├── reports/          # 중간·최종 보고서
└── README.md
```

## 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/hwangdongwuk/DataMining.git
cd DataMining

# 2. 의존성 설치 (추후 requirements.txt 추가 예정)
pip install requests feedparser pandas pdfplumber konlpy scikit-learn gensim streamlit plotly wordcloud

# 3. Streamlit 대시보드 실행 (개발 후)
streamlit run src/app.py
```

## 진행 상황

- [x] W02 주제 선정·계획서 제출
- [ ] W03 GitHub/Colab 환경 구축
- [ ] 데이터 수집 파이프라인 구현
- [ ] 전처리·EDA
- [ ] 분석 모델링(TF-IDF, LDA)
- [ ] Streamlit 대시보드
- [ ] 중간 보고서
- [ ] 최종 발표
