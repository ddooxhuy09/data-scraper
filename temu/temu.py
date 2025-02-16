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
        await context.add_cookies(cookies)
        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
            Object.defineProperty(navigator, 'userAgent', {
                get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            });
        """)
        await stealth_async(page)
        
        print(f"🔍 Đang mở URL: {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)
        await page.reload()

        await asyncio.sleep(60)  # Để tránh captcha

        results = []
        
        max_retries = 10

        try:
            while True:  # Lặp vô hạn cho đến khi không còn nút "See more"
                for _ in range(7):
                    await page.evaluate("window.scrollBy(0, window.innerHeight);")
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                await page.wait_for_selector('div.EKDT7a3v', timeout=10000)
                products = await page.query_selector_all('div.EKDT7a3v')

                print(f"🔍 Đã tìm thấy {len(products)} sản phẩm")

                for product in products:
                    try:
                        title_elem = await product.query_selector('div._6q6qVUF5._1QhQr8pq._2gAD5fPC._3AbcHYoU a')
                        price_elem = await product.query_selector('div._382YgpSF span._2de9ERAH')
                        sold_elem = await product.query_selector('span._1GKMA1Nk')
                        rating_elem = await product.query_selector('div.WCDudEtm')
                        review_count_elem = await product.query_selector('span._3CizNywp')

                        title = await title_elem.inner_text() if title_elem else "N/A"
                        link = await title_elem.get_attribute('href') if title_elem else "N/A"
                        price = await price_elem.inner_text() if price_elem else "N/A"
                        sold = await sold_elem.inner_text() if sold_elem else "N/A"
                        rating = await rating_elem.get_attribute("aria-label") if rating_elem else "N/A"
                        review_count = await review_count_elem.inner_text() if review_count_elem else "N/A"

                        results.append({
                            "Title": title,
                            "URL": f"https://www.temu.com{link}",
                            "Price": price,
                            "Sold": sold,
                            "Rating": rating.replace(" score", "") if rating != "N/A" else "N/A",
                            "Reviews": review_count
                        })
                    except Exception as e:
                        print(f"⚠️ Lỗi khi xử lý sản phẩm: {e}")

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
            with open("error_log.txt", "a", encoding="utf-8") as log_file:
                log_file.write(f"{keyword} - Error: {str(e)}\n")
            
            # Ghi dữ liệu ra file trước khi thoát
            df = pd.DataFrame(results)
            df.to_csv(f"{keyword}_temu_partial.csv", index=False, encoding="utf-8")
            print(f"⚠️ Dữ liệu đã lưu vào '{keyword}_temu_partial.csv' trước khi thoát.")
            
            await browser.close()
            sys.exit(1)  # Thoát ngay lập tức với mã lỗi 1

        await browser.close()

        df = pd.DataFrame(results)
        df.to_csv(f"{keyword}_temu_ttt.csv", index=False, encoding="utf-8")
        df = df[df["Sold"].str.contains("K", na=False)]
        df.to_csv(f"{keyword}_temu.csv", index=False, encoding="utf-8")
        print(f"✅ Dữ liệu đã được lưu vào '{keyword}_temu.csv'")

keyword = "Turtle keychain"
asyncio.run(open_temu_with_keyword(keyword))
