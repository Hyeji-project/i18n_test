from playwright.sync_api import sync_playwright #브라우저 자동화 도구

def main(): #프로그램의 시작점
    # Playwright 실행
    

    with sync_playwright() as p:# playwright 엔진 실행, with -> 끝나면 자동 정리
        browser = p.chromium.launch(headless=False) # 브라우저 실행 , headless=False → 실제 브라우저 창 보이게
        page = browser.new_page() 

    

        # 메인 페이지 이동
        page.goto("http://hshopfront.samsung.com/vn/")

    # hshopfront 로그인
        page.click('input#username')
        page.fill('input#username', 'qauser')
        page.click('input#password')
        page.fill('input#password', 'qauser1!')
        page.click('button#submit-button')

        #5 테스트 할 페이지 접속
        
        page.wait_for_timeout(1000)#1초 대기
        #쿠키 동의 팝업 클릭 (있을 때만 클릭하도록 수정)
        if page.locator("#truste-consent-button").is_visible(timeout=5000):
            page.click("#truste-consent-button")
        else:
            print("쿠키 동의 팝업이 나타나지 않아 건너뜁니다.")
        #human icon 마우스 오버 (데스크탑/모바일 공용 셀렉터 사용)
        login_btn = page.locator('a.loginBtn:visible, button[an-la="login"]:visible').first
        login_btn.hover()
        page.wait_for_timeout(1000) # 메뉴가 나타날 때까지 짧게 대기
        
        # Sign in 클릭 (더 포괄적인 셀렉터 사용)
        sign_in_link = page.locator('a.loginBtn:visible, a.nv00-gnb-v4__utility-menu--sign-in:visible').last
        sign_in_link.click()
    
        # 이메일 입력
        page.fill("#account", "csrevamp_vn1@teml.net")
        page.locator('button[data-log-id="next"]').click()
        page.fill("#password", "csrevamp1!")
        page.locator('button[data-log-id="signin"]').click()
        page.wait_for_timeout(3000)
        # "Not now" 버튼 처리
        page.click('button[data-testid="test-button-notnow"]') # 첫 번째 버튼은 필수 클릭
        
        # 두 번째 "Not now" 버튼은 있을 때만 클릭 (선택 사항)
        not_now_btn = page.locator('button[data-testid="test-button-notnow"]')
        if not_now_btn.is_visible(timeout=2000):
            not_now_btn.click()
            print("두 번째 'Not now' 버튼 클릭 완료")
        
        page.wait_for_timeout(3000)#3초 대기

        page.goto("https://hshopfront.samsung.com/vn/mypage/")
        page.wait_for_timeout(5000)#초 대기

        browser.close()
# 이 파일을 직접 실행했을 떄만 main() 함수 실행
if __name__ == "__main__":
    main()
