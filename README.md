i18n 자동 검증 스크립트 (Excel ↔ i18n API)
1. 개요 (Overview)

이 프로젝트는 엑셀(FRD)에 정의된 i18n 문구와 실제 서비스에서 내려오는 i18n API 응답을 자동으로 비교하기 위한 QA 자동화 스크립트입니다.

특히 다음과 같은 QA 요구사항을 해결합니다:

국가별 i18n 엑셀에서 검증 대상(노란색 셀)만 선별

<br> 태그, 공백 차이 등 HTML/포맷 차이 허용

{Serial number} 와 같은 placeholder 포함 문자열 비교

엑셀 ↔ API 간 누락 / 불일치 문구 자동 검출

비교 결과를 엑셀 리포트로 산출

2. 주요 기능
✅ 엑셀 기반 검증 대상 추출

국가 코드 시트(NL 등)에서:

H열 (Original)

K열 (Expected / Translation)

노란색으로 표시된 셀만 i18n 검증 대상으로 추출

✅ i18n API 자동 수집

Playwright를 사용해 실제 서비스 접속

로그인 후 i18n API 응답을 자동 인터셉트

최초 1회 응답만 파싱하여 저장

✅ 유연한 문자열 비교 로직

<br>, <br/>, <br /> → 공백 처리

대소문자 무시

연속 공백 정규화

{변수} placeholder → 정규식 매칭 처리

✅ 비교 결과 자동 리포트 생성

PASS / FAIL

Only API (API에만 존재)

Only FRD (엑셀에만 존재)

결과를 i18n_compare_result.xlsx로 저장

3. 폴더 / 파일 구조
.
├─ i18n.xlsx                  # 국가별 i18n 정의 엑셀
├─ i18n_compare_result.xlsx   # 비교 결과 리포트 (자동 생성)
├─ i18n_test.py               # 본 스크립트
└─ README.md

4. 사용 라이브러리
pip install playwright pandas openpyxl
playwright install

라이브러리	용도
playwright	브라우저 자동화 및 i18n API 인터셉트
pandas	데이터 가공 및 결과 엑셀 생성
openpyxl	엑셀 셀 색상(노란색) 판별
re	정규식 기반 문자열 비교
5. 엑셀 규칙 (중요)
📌 시트

국가 코드별 시트 사용 (예: NL, FR, DE 등)

📌 컬럼
컬럼	의미
H열	Original (i18n key 기준 문자열)
K열	Expected (번역 / 노출 문자열)
📌 검증 대상

H열 또는 K열 중 하나라도 노란색이면 검증 대상

노란색 RGB:

FFFFFF00

FFFF00

6. 문자열 비교 로직 설명
1️⃣ HTML 정규화 (normalize_html)

<br> 태그 제거

소문자 변환

공백 정리

2️⃣ Placeholder 대응 (i18n_match)
Excel:  "Serial number : {number}"
API:    "Serial number : 123456789"
→ PASS


{} 내부 값은 어떤 값이 와도 매칭되도록 처리

7. 실행 방법
python i18n_test.py


실행 순서:

엑셀에서 노란색 셀 i18n 추출

삼성닷컴 NL 사이트 접속

로그인 후 i18n API 응답 인터셉트

엑셀 ↔ API 비교

결과 엑셀 생성

8. 결과 리포트 컬럼 설명
컬럼	설명
original	엑셀 Original 값
expected	엑셀 Expected 값
key	i18n API key
value	i18n API value
result	PASS / FAIL / Only API / Only FRD
9. 활용 시나리오 (QA 관점)

🌍 글로벌 론치 전 국가별 i18n 정합성 검증

🧪 FRD 변경 후 실제 반영 여부 자동 확인

🚨 누락된 번역 / 잘못된 배포 조기 발견

🔁 반복적인 수동 비교 작업 제거

10. 주의사항

로그인 계정 정보는 실제 계정에 맞게 수정 필요

i18n API URL 구조가 변경되면 인터셉트 조건 수정 필요

국가별 시트명(sheet_name) 반드시 정확히 지정

11. 향후 개선 아이디어 (Optional)

다국가 시트 자동 루프

실패 케이스만 별도 시트 분리

Slack / 이메일 리포트 연동

CI 파이프라인 연계 (릴리즈 전 자동 검증)
