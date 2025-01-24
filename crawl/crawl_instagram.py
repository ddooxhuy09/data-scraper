import sys
import asyncio
import random
from undetected_playwright.async_api import async_playwright
from datetime import datetime
import json
import pandas as pd

def convert_likes_to_int(text):
    try:
        text = text.replace("likes", "").strip()
        return int(text.replace(",", ""))
    except:
        return 0
    
def format_datetime(date_str):
    try:
        return datetime.fromisoformat(date_str).strftime('%Y-%m-%d %H:%M:%S') if date_str else ""
    except:
        return date_str

async def get_context_with_blocking(browser, cookie):
    """Tạo context với việc chặn tải các tài nguyên không cần thiết như ảnh, video, css."""
    # Tạo một context mới
    context = await browser.new_context()

    # Thêm cookies vào context
    await context.add_cookies(cookie)

    await context.route('**/*', lambda route, request: route.abort() if request.resource_type in ['image', 'stylesheet', 'font'] else route.continue_())

    return context

    
async def get_urls(keyword):
    """Crawl danh sách URL bài viết từ Instagram theo keyword."""

    cookie_url = [
        {'name': 'ig_nrcb', 'value': '1', 'domain': '.instagram.com', 'path': '/'},
        {'name': 'datr', 'value': '3srvZtI_tyDVOjLggiQGof6D', 'domain': '.instagram.com', 'path': '/'},
        {'name': 'csrftoken', 'value': 'ogjxOxgIthhwQzAvzFLqNUZ9zMfGCcLd', 'domain': '.instagram.com', 'path': '/'},
        {'name': 'sessionid', 'value': '45038053263%3AbNCKeTPCpmIakl%3A6%3AAYe9R_zfZuW7Ekc-ZXRhs8QfBUwAVex2vPJ8dwnsfg', 'domain': '.instagram.com', 'path': '/'}
    ]
    async with async_playwright() as p:
        args = ["--disable-blink-features=AutomationControlled"]
        browser = await p.chromium.launch(headless=True, args=args)
        context = await get_context_with_blocking(browser,cookie_url)
        await context.add_cookies(cookie_url)
        page = await context.new_page()

        url = f'https://www.instagram.com/explore/search/keyword/?q={keyword}'
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        urls = set()
        scroll_count = 0

        while len(urls) < 500  :  # Giới hạn số URL cần lấy
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await asyncio.sleep(random.uniform(1, 3))

            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                if href and '/p/' in href:
                    full_url = f"https://www.instagram.com{href}"
                    urls.add(full_url)

            scroll_count += 1
            if scroll_count > 100:
                break

        await browser.close()

        print(f"Found {len(urls)} URLs")
        return list(urls)

# Hàm này giúp đọc cookie từ một file JSON
def load_cookie(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

async def scrape_post(url, context):
    """Scrape dữ liệu từ một bài viết."""
    page = await context.new_page()
    try:
        await page.goto(url, timeout=900000)
        await page.wait_for_selector("span._ap3a", state="attached", timeout=900000)  # Chờ tên
        await page.wait_for_selector("a[role='link'] span.x193iq5w", state="attached", timeout=900000)  # Chờ số likes
        await page.wait_for_selector("time", state="attached", timeout=900000)  # Chờ ngày

        result = await page.evaluate("""
        () => {
            const name = document.querySelector('span._ap3a')?.innerText || null;
            const likes = document.querySelector("a[role='link'] span.x193iq5w")?.innerText || "0";
            const date = document.querySelector("time")?.getAttribute("datetime") || null;
            return { name, likes, date };
        }
        """)
        likes = convert_likes_to_int(result.get("likes", "0"))

        video = await page.query_selector("video")
        post_type = "video" if video else "picture"
        return {
            "url": url,
            "name": result.get("name"),
            "type": post_type,
            "likes": likes,
            "date": format_datetime(result.get("date"))
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_post_chunk(chunk, context):
    """Scrape dữ liệu từ danh sách URL (chunk)."""
    tasks = [scrape_post(url, context) for url in chunk]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result]

async def scrape_posts_concurrent(urls, num_workers=10, urls_per_worker=2):
    """Scrape dữ liệu đồng thời từ danh sách URL với số worker cố định, mỗi worker xử lý một lượng URL nhất định."""
    # Đọc các cookies từ các file
    cookies = [load_cookie(f"cookies/cookie_{i+1}.json") for i in range(num_workers)]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Chia danh sách URL thành các phần nhỏ, mỗi phần có số lượng = num_workers * urls_per_worker
        total_chunks = [
            urls[i:i + num_workers * urls_per_worker]
            for i in range(0, len(urls), num_workers * urls_per_worker)
        ]

        all_results = []
        for chunk in total_chunks:
            # Tiếp tục chia nhỏ chunk thành các phần tương ứng với từng worker
            worker_chunks = [
                chunk[i:i + urls_per_worker]
                for i in range(0, len(chunk), urls_per_worker)
            ]
            
            # Tạo context cho từng worker
            contexts = [
                await get_context_with_blocking(browser, cookies[i % num_workers])
                for i in range(len(worker_chunks))
            ]

            # Tạo task cho mỗi worker xử lý phần của nó
            tasks = [
                scrape_post_chunk(worker_chunks[i], contexts[i])
                for i in range(len(worker_chunks))
            ]

            # Chờ tất cả các task hoàn thành
            results = await asyncio.gather(*tasks)
            all_results.extend([item for sublist in results for item in sublist])

            # Đóng tất cả các context
            for context in contexts:
                await context.close()

        await browser.close()

        # Trả về kết quả
        return all_results

def save_to_csv(data, filename):
    """Lưu kết quả vào file CSV."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')

def start_scraping():
    """Bắt đầu crawl dữ liệu và lưu vào CSV."""
    keyword = sys.argv[1]
    if not keyword.strip():
        print("Error: Please enter a keyword!")
        return

    try:
        print("Fetching URLs, please wait...")
        urls = asyncio.run(get_urls(keyword))
        if not urls:
            print("Error: No URLs found!")
            return

        results = asyncio.run(scrape_posts_concurrent(urls))

        # Lưu kết quả vào file CSV
        if results:
            save_to_csv(results, f"{keyword}_instagram_data.csv")
            print(f"Data has been saved to instagram_posts.csv")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_scraping()