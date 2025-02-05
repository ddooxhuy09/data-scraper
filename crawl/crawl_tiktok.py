import sys
from undetected_playwright.async_api import async_playwright
import asyncio
import random
import re
import pandas as pd
from datetime import datetime, timedelta


def convert_likes_to_number(likes_str):
    """Chuyển đổi số lượt thích từ dạng '26.2K' thành số nguyên 26200."""
    if not likes_str:
        return 0

    match = re.match(r"([\d.]+)([KMB]?)", likes_str)
    if not match:
        return 0

    number, unit = match.groups()
    number = float(number)

    if unit == "K":
        return int(number * 1_000)
    elif unit == "M":
        return int(number * 1_000_000)
    elif unit == "B":
        return int(number * 1_000_000_000)

    return int(number)


def convert_date(date_str):
    """Chuyển đổi ngày về định dạng YYYY-MM-DD."""
    if not date_str:
        return None

    current_year = datetime.now().year
    current_date = datetime.now().date()

    # Nếu định dạng YYYY-MM-DD thì giữ nguyên
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        pass

    # Nếu là "X ngày trước" thì trừ đi X ngày
    days_ago_match = re.match(r"(\d+) ngày trước", date_str)
    if days_ago_match:
        days_ago = int(days_ago_match.group(1))
        new_date = current_date - timedelta(days=days_ago)
        return new_date.strftime("%Y-%m-%d")

    # Nếu có dạng "DD-MM" (ví dụ: "1-11"), thì thêm năm hiện tại
    short_date_match = re.match(r"(\d{1,2})-(\d{1,2})", date_str)
    if short_date_match:
        day, month = map(int, short_date_match.groups())
        new_date = datetime(current_year, month, day).date()
        return new_date.strftime("%Y-%m-%d")

    return None


async def open_tiktok_with_keyword(keyword):
    url = f"https://www.tiktok.com/search?lang=vi-VN&q={keyword}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()

        print(f"🔍 Đang mở URL: {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Chờ trang tải đầy đủ
        
        video_data = []
        scroll_count = 0
        max_scrolls = 13

        while scroll_count < max_scrolls:
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await asyncio.sleep(random.uniform(2, 4))  # Chờ để tải nội dung

            items = await page.query_selector_all("div.css-1soki6-DivItemContainerForSearch")
            for item in items:
                try:
                    # Lấy URL video
                    url_elem = await item.query_selector('a')
                    url = await url_elem.get_attribute('href') if url_elem else None
                    
                    # Lấy số lượt thích
                    likes_elem = await item.query_selector(".video-count")
                    likes_text = await likes_elem.inner_text() if likes_elem else None
                    likes = convert_likes_to_number(likes_text)

                    # Lấy ngày
                    date_elem = await item.query_selector('div.css-9unyn0-DivTimeTag')
                    date_text = await date_elem.inner_text() if date_elem else None
                    date = convert_date(date_text)

                    print(f"Processing: {url}")

                    if url and date:  # Đảm bảo có URL và ngày
                        video_data.append({
                            "url": url,
                            "likes": likes,
                            "date": date
                        })

                except Exception as e:
                    print(f"Lỗi khi lấy dữ liệu video: {e}")
                    continue

            scroll_count += 1
        await browser.close()

        # Lưu vào CSV
        df = pd.DataFrame(video_data)
        df.to_csv(f"{keyword}_tiktok_data.csv", index=False, encoding="utf-8")
        print(f"Data has been saved to {keyword}_tiktok_data.csv")

keyword = sys.argv[1]
# Chạy hàm với từ khóa tìm kiếm
asyncio.run(open_tiktok_with_keyword(keyword))
