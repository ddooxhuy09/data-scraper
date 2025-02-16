import sys
from undetected_playwright.async_api import async_playwright
import asyncio
import random
import pandas as pd
import re

async def scrape_page(page, page_num):
    print(f"🔍 Đang thu thập dữ liệu trang {page_num}...")

    for _ in range(10):
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        await asyncio.sleep(random.uniform(0.5, 1))
    
    items = await page.query_selector_all("div.multi--outWrapper--SeJ8lrF")

    results = []
    for item in items:
        link_element = await item.query_selector("a.multi--container--1UZxxHY")
        title_element = await item.query_selector("h3.multi--titleText--nXeOvyr")
        sold_element = await item.query_selector("span.multi--trade--Ktbl2jB")
        price_element = await item.query_selector("div.multi--price-sale--U-S0jtj")
        
        if link_element and title_element and price_element:
            url = await link_element.get_attribute("href")
            title = await title_element.inner_text()
            sold_text = await sold_element.inner_text() if sold_element else "0"
            price = await price_element.inner_text()
            
            results.append({
                "URL": f"https:{url}",
                "Title": title.strip(),
                "Sold": sold_text.strip(),
                "Price": price.strip(),
            })
    
    return results

async def open_aliexpress_with_keyword(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        all_results = []
        page_num = 1

        while True:
            url = f"https://vi.aliexpress.com/w/wholesale-{keyword}.html?page={page_num}"
            print(f"🛒 Đang mở trang {page_num}: {url}")
            await page.goto(url)
            await page.wait_for_timeout(5000)  # Chờ trang tải đầy đủ
            
            # Thu thập dữ liệu từ trang hiện tại
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
    results = await open_aliexpress_with_keyword(keyword)

    # Lưu vào CSV
    if results:
        df = pd.DataFrame(results)
        
        # 🛠 Trích xuất số lượng bán từ chuỗi dạng "1000+ sold"
        df['sold_numeric'] = df['Sold'].apply(lambda x: int(re.search(r'(\d+)', x.replace(",", "")).group(1)) if re.search(r'(\d+)', x.replace(",", "")) else 0)

        # 🛠 Lọc các sản phẩm có số lượng bán > 1000
        df_filtered = df[df['sold_numeric'] >= 1000].drop(columns=['sold_numeric'])  # Xóa cột tạm thời

        # 🛠 Lưu kết quả vào CSV
        df_filtered.to_csv(f"{keyword}_aliexpress.csv", index=False, encoding='utf-8')
        print(f"✅ Đã lưu dữ liệu vào {keyword}_aliexpress.csv (chỉ các sản phẩm có Sold > 1000)")
    else:
        print("⚠️ Không tìm thấy sản phẩm nào có số lượng bán > 1000!")

# Chạy chương trình
asyncio.run(main())
