import sys
from undetected_playwright.async_api import async_playwright
import asyncio
import time
from playwright_stealth import stealth_async
import pandas as pd
import random
from playwright_stealth import stealth_sync, StealthConfig
from temu_captcha_solver import PlaywrightSolver

async def open_temu_with_keyword(keyword):
    url = f"https://www.temu.com/search_result.html?search_key={keyword}"
    
    cookies = [
        {"name": "AccessToken", "value": "OIZQ7DQH4KOPTM6TMBRFC7RV6F6QS4FYIBH5IJHHCXVOPKL6MPQQ0110d9aeb234", "domain": ".temu.com", "path": "/"},
        {"name": "user_uin", "value": "BBEJRZUYIL3H2R4L4DWE6TW7P4ZTQICCU4ANTI7U", "domain": ".temu.com", "path": "/"},
        {"name": "isLogin", "value": "1739357678831", "domain": ".temu.com", "path": "/"}
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        # await context.add_cookies(cookies)
        page = await context.new_page()

        await stealth_async(page)
        
        print(f"🔍 Đang mở URL: {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)
        await asyncio.sleep(60)
        
        max_retries = 10

        try:
            while True:  # Lặp vô hạn cho đến khi không còn nút "See more"
                for _ in range(7):
                    await page.evaluate("window.scrollBy(0, window.innerHeight);")
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                await page.wait_for_selector('div._3HKY2899', state='attached')

                see_more_button = await page.query_selector('div._3HKY2899')

                if not see_more_button or not await see_more_button.is_visible():  
                    print("⏹️ Không còn hoặc không hiển thị nút 'See more'. Dừng lại.")
                    break

                await page.evaluate("""
                    let products = document.querySelectorAll('div.EKDT7a3v');
                    products.forEach(p => p.remove());
                """)

                await see_more_button.click()
                await asyncio.sleep(2)

                button_text = await page.evaluate('''() => {
                    let btn = document.querySelector('div._3HKY2899');
                    return btn ? btn.innerText.trim() : "";
                }''')

                if button_text.lower() == "try again":
                    retry_count = 0

                    while retry_count <= max_retries:
                        await page.wait_for_selector('div._3HKY2899', state='attached')
                        try_again_button = await page.query_selector('div._3HKY2899')

                        await try_again_button.click()
                        print(f"⚠️ Xuất hiện 'Try again' ({retry_count}/{max_retries}). Thử lại...")
                        await page.wait_for_load_state('domcontentloaded')
                        await asyncio.sleep(2)

                        button_text = await page.evaluate('''() => {
                            let btn = document.querySelector('div._3HKY2899');
                            return btn ? btn.innerText.trim() : "";
                        }''')

                        if button_text.lower() != "try again":
                            print("✅ Nút 'Try again' đã biến mất, tiếp tục quá trình...")
                            break  # Thoát khỏi vòng lặp nếu nút không còn

                        retry_count += 1
                    if retry_count == max_retries:
                        print("⚠️ Đã thử quá số lần cho phép. Dừng lại.")
                        break
                else:
                    retry_count = 0  

        except Exception as e:
            print(f"❌ Lỗi xảy ra: {e}")
 

keyword = "Turtle keychain"
asyncio.run(open_temu_with_keyword(keyword))
