from playwright.sync_api import sync_playwright #브라우저 자동화 도구

def main(): #프로그램의 시작점
    # Playwright 실행
    

    with sync_playwright() as p:# playwright 엔진 실행, with -> 끝나면 자동 정리
        browser = p.chromium.launch(headless=False) # 브라우저 실행 , headless=False → 실제 브라우저 창 보이게
        page = browser.new_page() 

    

        # 메인 페이지 이동
        page.goto("http://hshopfront.samsung.com/nl/")

    # hshopfront 로그인
        page.click('input#username')
        page.fill('input#username', 'qauser')
        page.click('input#password')
        page.fill('input#password', 'qauser1!')
        page.click('button#submit-button')

        #5 테스트 할 페이지 접속
        
        page.wait_for_timeout(1000)#1초 대기
        #쿠기 동의 팝업 클릭
        page.click("#truste-consent-button")
        #human icon 마우스 오버
        page.locator('a.nv00-gnb__utility-btn.mobile-only.loginBtn').hover()
        
        #sign in 클릭릭
        page.locator("a.nv00-gnb__utility-user-menu-link.loginBtn").click()
    
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
# 이 파일을 직접 실행했을 떄만 main() 함수 실행
if __name__ == "__main__":
    main()
