# 1. 필요한 라이브러리 불러오기기
from playwright.sync_api import sync_playwright #브라우저 자동화 도구
import pandas as pd # 엑셀 읽는 라이브러리리
import json # JSON 파일 읽는 라이브러리리

def main(): #프로그램의 시작점점
    print("i18n 테스트 시작")

    #2. 엑셀 파일 읽기
    df =pd.read_excel("i18n.xlsx")

    # 2.1. 필요한 컬럼만 선택(원문/번역본)
    df_pairs = df.iloc[:, [0,3]]

    #2.5. 컬럼 이름 정리
    df_pairs.columns = ["original", "translation"]

    #2.2. 번역 없는 row 제거
    df_pairs = df_pairs.dropna()

    #2.3. 소문자 key 제거
    df_pairs =df_pairs[df_pairs["original"].str[0].str.isupper()]

    #2.4. URL,N 제거
    df_pairs = df_pairs[~df_pairs["original"].str.startswith("/")]
    df_pairs = df_pairs[df_pairs["original"] !="N"]


    print("정제된 i18n 비교 대상 : ")
    print(df_pairs)

    # Playwright 실행
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
        #sign in 클릭릭
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

    # 엑셀 VS i18n_dict 비교

    results = []

    for _, row in df_pairs.iterrows():
        original = row["original"].strip()
        expected = row["translation"].strip()

        #key없음
        if original not in i18n_dict:
            results.append({
                "original":original,
                "expected" : expected,
                "key":"",
                "value":"",
                "result": "MISSING"
            })
            continue
        actual_value = i18n_dict[original].strip()

        if actual_value == expected:
            result = "PASS"
        else:
            result="FAIL"

        results.append({
            "original":original,
            "expected" : expected,
            "key":original,
            "value":actual_value,
            "result": result
        })
# 결과를 엑셀 저장
    result_df = pd.DataFrame(
        results,
        columns=["original","expected","key","value","result"]
    )
    result_df.to_excel("i18n_compare_result.xlsx", index=False)
    print("i18n 비교 결과 엑셀 생성 완료료")

# 이 파일을 직접 실행했을 떄만 main() 함수 실행
if __name__ == "__main__":
    main()
