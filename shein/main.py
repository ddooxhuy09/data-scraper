from undetected_playwright.async_api import async_playwright
import asyncio
import pandas as pd
import random
from playwright_stealth import stealth_async, StealthConfig
from captcha_solver import solve_captcha_on_page
import sys

async def scrape_page(page, page_num):
    print(f"🔍 Đang thu thập dữ liệu trang {page_num}...")

    for _ in range(15):

        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(random.uniform(0.5, 1))
    
    items = await page.query_selector_all(".product-card__bottom-wrapper")

    results = []
    for item in items:
        # Lấy tiêu đề sản phẩm
        title_element = await item.query_selector(".goods-title-link")
        title = await title_element.inner_text() if title_element else "N/A"

        # Lấy link sản phẩm
        link = await title_element.get_attribute("href") if title_element else "N/A"

        # Lấy rating và số lượng review
        rating_element = await item.query_selector(".product-card__auto-label")
        if rating_element:
            rating_data = await rating_element.get_attribute("data-tag-content")
            if rating_data and "star_" in rating_data:
                rating, reviews = rating_data.replace("star_", "").split("_")
                reviews = reviews if reviews.isnumeric() else "1000+"
            else:
                rating, reviews = "N/A", "N/A"
        else:
            rating, reviews = "N/A", "N/A"

        # Lấy giá sản phẩm
        price_element = await item.query_selector(".product-item__camecase-wrap span")
        price = await price_element.inner_text() if price_element else "N/A"

        # Lấy số lượng đã bán
        sold_element = await item.query_selector(".product-card__sales-label")
        sold = await sold_element.inner_text() if sold_element else "N/A"

        results.append({
            "Title": title.strip(),
            "Link": f"https://www.shein.co.uk{link}",
            "Rating": rating.strip(),
            "Reviews": reviews.strip(),
            "Price": price.strip(),
            "Sold": sold.strip()
        })
    
    return results


async def open_shein_with_keyword(keyword):

    async with async_playwright() as p:
        cookies = [
            {"name": "cookieId", "value": "63310995_F48D_D204_794C_76DFD880B569", "domain": ".shein.co.uk", "path": "/"},
            {"name": "RESOURCE_ADAPT_WEBP", "value": "1", "domain": ".shein.co.uk", "path": "/"},
            {"name": "armorUuid", "value": "20250208194151e0a2bcd810169e720c72896f325140ba00f8b317a3b9399000", "domain": ".shein.co.uk", "path": "/"},
            {"name": "smidV2", "value": "2025020819415173f68bfcdde3a266ede2971a23c4c8fa00daa478d48b711a0", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_scid", "value": "SxmUKA2TAvRNQ44-8U-wemkuUKT_ZQUh", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_ScCbts", "value": "%5B%5D", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_sctr", "value": "1%7C1738947600000", "domain": ".shein.co.uk", "path": "/"},
            {"name": "webpushcookie", "value": "agree%3A1", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_gcl_gs", "value": "2.1.k1$i1739018509$u137890418", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_gcl_au", "value": "1.1.1456876349.1739018520", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_gcl_aw", "value": "GCL.1739018521.CjwKCAiAnpy9BhAkEiwA-P8N4jRoHDd2OYxqYCYQ0htM4DnmbqohSHwI1yWq8UZp3hEW_UIC3WPaFRoCUGwQAvD_BwE", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_pin_unauth", "value": "dWlkPVkyRTNaV0l6WlRNdE1USmxZeTAwTkRGbUxUZ3dOREV0WWpnd1lUYzVPVE0wWVdVMQ", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_fbp", "value": "fb.2.1739018521070.280634069605102295", "domain": ".shein.co.uk", "path": "/"},
            {"name": "fita.sid.shein", "value": "80W26jtAHoZrrYpTDPqz6j_HGI0Sjoyy", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_csrf", "value": "C3_AxlIdGy1sTuyjwuRBJ5Xe", "domain": ".shein.co.uk", "path": "/"},
            {"name": "forterToken", "value": "8c3ecb2b9e3647bba1ab94e7d73c1258_1739018678181__UDF43-m4_17ck_", "domain": ".shein.co.uk", "path": "/"},
            {"name": "jump_to_uk", "value": "1", "domain": ".shein.co.uk", "path": "/"},
            {"name": "memberId", "value": "4704509949", "domain": ".shein.co.uk", "path": "/"},
            {"name": "AT", "value": "MDEwMDE.eyJiIjo3LCJnIjoxNzM5MDIxNDI1LCJyIjoienNLd1ZrIiwidCI6MiwibSI6NDcwNDUwOTk0OSwibCI6MTczOTAyMTQyNX0.3e5c0b56569095f5.2687a564f6040c0ca3fb4bde69ad37a1c0decc9005fa772f3a0827fc621b228f", "domain": ".shein.co.uk", "path": "/"},
            {"name": "sessionID_shein", "value": "s%3AVO33BMtKhcdzIRJ7UonaRnks_bC3mISL.IdQeiJaEqRG0M9Bh9WiPpU0uYvpQbAwpSKuZjQ9hhgk", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_rdt_uuid", "value": "1739018520281.c3185e58-b277-43c6-854a-2f0b24c355c9", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_scid_r", "value": "VJmUKA2TAvRNQ44-8U-wemkuUKT_ZQUhvDfNyA", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_uetsid", "value": "1f015a90e61a11ef8115959840629905", "domain": ".shein.co.uk", "path": "/"},
            {"name": "_uetvid", "value": "1f01b570e61a11ef901181b14c38cfe5", "domain": ".shein.co.uk", "path": "/"},
            {"name": "cto_bundle", "value": "dOVECV9nR0t4SmJIM3pyMjM3TE54cVlMZ3pYaUtCJTJCVmdlZnhWcGJrUlBPVVIyWTRhJTJGeXJJT2ZuNmluY2FjbkpmSWk4cFlrdVBJZ3hqZyUyRmg2ek1TcSUyRlNrWHZyN21sd1hrJTJGUzJsMEFEOGVqemRkd0JVTFF1b1glMkZTSjBrT3NaNkhZeEtCbA", "domain": ".shein.co.uk", "path": "/"},
        ]

        user_data_dir = "C:\\Users\\ddoox\\AppData\\Local\\Google\\Chrome\\User Data\\Default"

        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",  # Ẩn thuộc tính điều khiển tự động
                "--disable-infobars",
                "--disable-gpu",
                "--window-size=1280,720"
            ]
        )

        # Thêm cookie vào trình duyệt
        await browser.add_cookies(cookies)  

        page = await browser.new_page()
        await page.evaluate('''() => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        }''')

        config = StealthConfig(navigator_languages=False, navigator_vendor=False, navigator_user_agent=False)

        await stealth_async(page, config)

        all_results = []
        page_num = 1

        while True:
            url = f"https://www.shein.co.uk/pdsearch/{keyword}?page={page_num}"

            print(f"🛒 Đang mở trang {page_num}: {url}")
            await page.goto(url)
            await page.wait_for_timeout(5000)  # Chờ trang tải đầy đủ

            captcha_elem = page.locator(".captcha_click_wrapper")  # Tìm CAPTCHA
    
            if await captcha_elem.is_visible():
                print("⚠️ CAPTCHA xuất hiện, đang tiến hành giải...")
                success = await solve_captcha_on_page(page)  # Nhận kết quả trả về

                if success:
                    print("🎉 CAPTCHA đã được giải thành công!")
                else:
                    print("❌ Giải CAPTCHA thất bại, thử lại sau hoặc kiểm tra API!")

            results = await scrape_page(page, page_num)
            if not results:
                print(f"⚠️ Không có dữ liệu trên trang {page_num}, dừng lại.")
                break
            
            all_results.extend(results)
            page_num += 1  # Chuyển sang trang tiếp theo
        
        await browser.close()
        
        return all_results

async def main():
    keyword = sys.argv[1]
    results = await open_shein_with_keyword(keyword)

    # Lưu vào CSV
    if results:
        df = pd.DataFrame(results)
        df = df[df["Sold"].str.contains("k", na=False)]
        df.to_csv(f"{keyword}_shein.csv", index=False, encoding='utf-8-sig')
        print(f"✅ Đã lưu dữ liệu vào {keyword}_shein.csv (chỉ các sản phẩm có Sold > 1000)")
    else:
        print("⚠️ Không tìm thấy sản phẩm nào có số lượng bán > 1000!")

# Chạy chương trình
asyncio.run(main())