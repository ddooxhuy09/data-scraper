import pandas as pd
import asyncio
import random
from undetected_playwright.async_api import async_playwright
from datetime import datetime, timedelta
import re
import sys

def process_created_at(text):
    # Extract numbers and unit (Y, M, D)
    match = re.match(r'(\d+)\s?(Y|M|D)', text)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        
        # Get current date
        current_date = datetime.now()
        
        if unit == "Y":
            # Subtract years
            new_date = current_date - timedelta(days=value * 365)  # Approximation, assuming no leap years
        elif unit == "M":
            # Subtract months
            new_date = current_date - timedelta(days=value * 30)  # Approximation, assuming 30 days per month
        elif unit == "D":
            # Subtract days
            new_date = current_date - timedelta(days=value)
        
        return new_date.strftime("%Y-%m-%d")
    else:
        return None

async def open_pinterest_with_keyword(keyword):
    user_data_dir = "C:\\Users\\ddoox\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
    path_to_extension = "C:\\Users\\ddoox\\AppData\\Local\\Microsoft\\Edge Dev\\User Data\\Default\\Extensions\\djcledakkebdgjncnemijiabiaimbaic\\1.8.8_0"

    url = f"https://www.pinterest.com/search/pins/?q={keyword}&rs=typed"

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            channel="chrome",
            args=[
                f"--disable-extensions-except={path_to_extension}",
                f"--load-extension={path_to_extension}",
            ]
        )

        page = await browser.new_page()
        
        print(f"🔍 Đang mở URL: {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Chờ trang tải đầy đủ

        urls_data = []
        scroll_count = 0

        while len(urls_data) < 500:  # Lấy tối đa 100 URL
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await asyncio.sleep(random.uniform(1, 3))

            pins = await page.query_selector_all('div.Yl-.MIw.Hb7')

            for pin in pins:
                link_element = await pin.query_selector('a')
                saves_element = await pin.query_selector('span.bg-teal-100')
                reactions_element = await pin.query_selector('span.bg-teal-100.text-teal-800')
                likes_element = await pin.query_selector('span.bg-gray-100.text-gray-800')
                repins_element = await pin.query_selector('div.text-gray-800 span.bg-teal-100.text-teal-800')
                source_element = await pin.query_selector('a.text-gray-600')
                created_at_element = await pin.query_selector('span.bg-blue-100.text-blue-800')

                # Extract and process Created At if available
                created_at = await created_at_element.inner_text() if created_at_element else None
                if created_at:
                    created_at = process_created_at(created_at)

                if link_element:
                    href = await link_element.get_attribute('href')
                    if href and '/pin/' in href:
                        full_url = f"https://www.pinterest.com{href}"
                        
                        # Lấy số lượng saves
                        saves = await saves_element.inner_text() if saves_element else "0"

                        # Lấy số lượng reactions
                        reactions = await reactions_element.inner_text() if reactions_element else "0"

                        # Lấy số lượng likes
                        likes = await likes_element.inner_text() if likes_element else "0"

                        # Lấy số lượng repins
                        repins = await repins_element.inner_text() if repins_element else "0"

                        # Lấy source
                        source = await source_element.get_attribute('href') if source_element else "None"

                        urls_data.append({
                            "URL": full_url,
                            "Saves": saves,
                            "Reactions": reactions,
                            "Likes": likes,
                            "Repins": repins,
                            "Source": source,
                            "Created At": created_at
                        })

            scroll_count += 1
            if scroll_count > 100:
                break

        await browser.close()

        return urls_data

# Chạy script và lưu vào CSV
keyword = sys.argv[1]
data = asyncio.run(open_pinterest_with_keyword(keyword))

# Lưu vào file CSV bằng pandas
df = pd.DataFrame(data)
df.to_csv(f"{keyword}_pinterest_data.csv", index=False, encoding="utf-8")
print(f"Data has been saved to {keyword}_pinterest_data.csv")
