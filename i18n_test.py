# 1. 필요한 라이브러리 불러오기기
from playwright.sync_api import sync_playwright #브라우저 자동화 도구
import pandas as pd # 엑셀 읽는 라이브러리리
from openpyxl import load_workbook # 엑셀 데이터 추출
from datetime import datetime
import re

def normalize_html(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # <br>, <br/>, <br /> → 공백
    text = re.sub(r"<br\s*/?>", " ", text)

    # 양쪽 공백 제거
    text = text.strip()

    # 모든 공백을 단일 스페이스로
    text = re.sub(r"\s+", " ", text)

    return text


# ===============================
#  helper 함수
# ===============================
def i18n_match(expected: str, actual: str) -> bool:
    """
    expected: 엑셀 값 (placeholder 포함)
    actual: i18n API 값
    """

    if not expected or not actual:
        return False

    expected = normalize_html(expected)
    actual = normalize_html(actual)

    # placeholder 대응
    pattern = re.escape(expected)
    pattern = re.sub(r"\\\{.*?\\\}", r"[^ ]+", pattern)

    pattern = pattern.replace(r"\ ", r"\s+")

    return re.fullmatch(pattern, actual) is not None


# 2.엑셀에서 "노란색 셀" i18n 추출
def extract_yellow_i18n_pairs(excel_path: str, sheet_name: str):
    wb = load_workbook(excel_path, data_only=True)
    ws = wb[sheet_name]

    results = []

    def is_yellow(cell):
        if cell.fill and cell.fill.start_color:
            return cell.fill.start_color.rgb in ("FFFFFF00", "FFFF00")
        return False

    # H열(original = index 7), K열(expected = index 10)
    for row in ws.iter_rows(min_row=2):
        original_cell = row[7]
        expected_cell = row[10]

        original = original_cell.value
        expected = expected_cell.value

        if not original or not expected:
            continue

        if is_yellow(original_cell) or is_yellow(expected_cell):
            results.append({
                "original": str(original).strip(),
                "translation": str(expected).strip()
            })

    return pd.DataFrame(results)


#3. 메인 로직

def main(): #프로그램의 시작점점
    print("i18n 테스트 시작")

     # 3-1. 엑셀 → 노란색 셀만 추출
    df_pairs = extract_yellow_i18n_pairs(
        excel_path="i18n.xlsx",
        sheet_name="NL"   # 🔴 국가 코드 시트명
    )

    print("정제된 i18n 비교 대상")

    excel_dict = dict(
        zip(df_pairs["original"], df_pairs["translation"])
    )


    # 4. Playwright 실행
    i18n_dict = {} # 응답 저장 딕셔너리

    with sync_playwright() as p:# playwright 엔진 실행, with -> 끝나면 자동 정리
        browser = p.chromium.launch(headless=False) # 브라우저 실행 , headless=False → 실제 브라우저 창 보이게
        page = browser.new_page() 

         #  API 인터셉트 ,response 이벤트 리스터
        def handle_response(response):
            nonlocal i18n_dict

            url = response.url
            if "i18n" in url :
                # 이미 저장했으면 다시 파싱하지 않음
                if i18n_dict:
                    return
                try:
                    data = response.json() 
                    if isinstance(data, dict):
                        i18n_dict = data
                        print("i18n API 인터셉트 성공 :", url)
                        print("i18n API key 개수:", len(i18n_dict))
                except Exception as e:
                    print("i18n 파싱 실패:", e)

        page.on("response", handle_response)

        
        #5 테스트 할 페이지 접속
        page.goto("https://www.samsung.com/nl/")
        page.wait_for_timeout(1000)#1초 대기
        #쿠기 동의 팝업 클릭
        page.click("#truste-consent-button")
        #human icon 마우스 오버
        page.locator('button[an-la="login"]').hover()
        #sign in 클릭
        page.locator("a.loginBtn.nv00-gnb-v4__utility-menu--sign-in").click()
        # 이메일 입력
        page.fill("#account", "mypage_nl1@ruu.kr")
        page.locator('button[data-log-id="next"]').click()
        page.fill("#password", "mypages24@")
        page.locator('button[data-log-id="signin"]').click()
        page.wait_for_timeout(3000)
        page.click('button[data-testid="test-button-notnow"]')
        page.click('button[data-testid="test-button-notnow"]')
        
        page.wait_for_timeout(3000)#3초 대기

        page.goto("https://www.samsung.com/nl/mypage/")
        page.wait_for_timeout(5000)#5초 대기

        browser.close()

    print("i18n API key 개수:", len(i18n_dict))

    # 6. 엑셀 VS i18n_dict 비교

    results = []

    for key, value in i18n_dict.items():
        api_value = value.strip()

        if key in excel_dict:
            expected = excel_dict[key].strip()

            if i18n_match(expected, api_value):
                result = "PASS"
            else:
                result = "FAIL"

            results.append({
                "original": key,
                "expected": expected,
                "key": key,
                "value": api_value,
                "result": result
        })
        else:
        # API에만 존재
            results.append({
                "original": "",
                "expected": "",
                "key": key,
                "value": api_value,
                "result": "Only API"
        })

    # 2️⃣ 엑셀에만 존재하는 key (FRD only)
    for original, expected in excel_dict.items():
        if original not in i18n_dict:
            results.append({
                "original": original,
                "expected": expected,
                "key": "",
                "value": "",
                "result": "Only FRD"
        })
# 결과를 엑셀 저장
    result_df = pd.DataFrame(
        results,
        columns=["original","expected","key","value","result"]
    )
    result_df.to_excel("i18n_compare_result.xlsx", index=False) 
    print("i18n 비교 결과 엑셀 생성 완료")

    

# 이 파일을 직접 실행했을 떄만 main() 함수 실행
if __name__ == "__main__":
    main()
