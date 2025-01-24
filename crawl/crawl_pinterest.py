import sys
import asyncio
import random
from undetected_playwright.async_api import async_playwright
import pandas as pd

async def get_context_with_blocking(browser):
    """Create a browser context with blocking unnecessary resources."""
    cookie = [
        {
            'name': 'csrftoken',
            'value': 'a735620f6094f876a39cf50da71c8eec',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': True,
            'secure': True,
        },
        {
            'name': '_routing_id',
            'value': 'dca819b0-7070-4975-beb7-a1a3a9599592',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': True,
            'secure': True,
        },
        {
            'name': 'sessionFunnelEventLogged',
            'value': '1',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': False,
            'secure': False,
        },
        {
            'name': 'g_state',
            'value': '{"i_l":0}',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': False,
            'secure': False,
        },
        {
            'name': '_auth',
            'value': '1',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': False,
            'secure': False,
        },
        {
            'name': '_pinterest_sess',
            'value': 'TWc9PSZCcitDdU5HQmQ0ZWJjbWk0SllzdWJEVkRXUXBkSXNQTkFFcTZqdG9ncHVNSGt6U2NQRkJ0OSs1S3IySlBWRDZZMWxzdDdVcDBFUzI1QjNaNHZDay96T1ZVNWFra2NSMkk4VDJmWEl3a1ZtN01wdGtoS3FwMDkvMm9Id0xaeFpJemJDUmYzQWJ0M0t6amxIYytyazN4RDRCaXRYTDVIOHFnNFdlcEwyN0h5dURwSmU3SnZYSVFEcUwvZ3Zsd0tWWXBRa2gyWFNqbDJFakp4dGJtQjJjRWdqSUpPaDkycHlIS1hKTEk2LzZHZkQ1czRzWWh0aGRDamhCV05qRmdaWFUxZHZrRm95MlZZZndmT293NzZ3aDQ5U3FBQUJMcmFpQk5HYVh3eFdZT21VY1ZiQldXK0NNNGlTeFNWdStVZ2hBNHhESFVYYkdLTmZuQnYvMjRRTzdhakJvdVlUQ09ZZ2ZFaytReDY0RGpoV0NQTHUrVXJWU2YwK1pZOENEbXg4Zk1iL0g1SmxsNWFiN0lhbDJTOGF3dno5K3RIbEN2emZ3K28wTitlUkwwb0hqZXNPNWlJK0tmRDUzVWxBbUVpOW1qMkhBa3RjWTd4K2RVTk1vVlZhVFdlVEhNRFVUTE00aEJWWTgrZjlyWkRMcjhRekxDTC9WN0pHejN0aFlRZ2xLcVhsTUppdTFyOGlRaysreDB3TUY3alFEcGZVNk41bkxTajhXb3NGWkpTMHlYMEF1cjZ1aVNBUmcrS1A2bG5lVWJ2aTJ3ZndPMXFYL2ZxazBJUWZYY3Q5T1lKcisyTTZMZUZyRDVUNDlJUlVYL3lmcVNmWloyU2dRMHl5aTVBdEZLVXNETzVFUktQSTVZWnNUQmNIVVpyVnhiMytPQnp3NjJBMkJhZ2FNU1c5d3hwdlVLdzhiZXNKN3VteXJOZkxZbktaeW9pVFA3Vng3bzR0WVhwQ3NZYzNXOGxYcFRSdFlhM2VlaU8yTCtpb1RWK0kwRlFpdzRRSzNTNzhJTE5LSzg5T21wZmVybklsa1RFaDkzREY3SHJtRGwxN3gzdER0aHNGUnUvTGY5Q1czNndYWlFoTGR2ektObm1raWsyaVZYTHh5ajU4N0pBZ2NrSEtXOExzSDhqaDRPL0ZDRHZYaFVuRmdLU3VseEhzaGxwK0poRjBEL0RnTTU5cU1FdWtUUzNFU0ZUVFM2UkpNWldzUWdxS2VwWUowc0I3L0VSdElVN1RYdTlHcUxmSS8zSG1mYzBUQjdQVzFXZXMzYVZGMVhyNmc5U0hHQ1o3NlVBUWM1VFJabzZaRlFWdTNMVWE5MWFMVGFCcDNVYldWQW9sLzIrQllOQmtZZWRnRUpMQUlxSUVvYlBzQ09ZMGFOK0Q0Q1FBdmRSQ1BjbG9PUnBTUGlzWUhMSHZ4cllNVExmWnk3WE1KMHNVQ1JQYkt3UVZnb3F1a1k4ekJreENaeUtPVWFjajA5MmxpUXEzZEtlYkx6UlErZjQwRlRqSHdBMVFyUmxsU3RGTnhTRjhrbUVzMjNpSjl4L2xZbk5LTU9qNVQ2UzhGR2ZQMWI4Sk1LYlRtdFVJRzcvanhMQUc5Z0VyVmhkUGlzK0NmRWF3Y2RMWHRxTmJ4ajBXRERtWUUzWkdmY0NDL2FpamprVENtQ0VNZmR3VnFsMm9aMjBVRmU5ak9xZnB3MjVJUEErS2xHZ2FKM2NTaFdScjRoVEJiM1NTVGtUVEdZeXZUOGVBZlBXS0pyTWNDWXJOWkVmVFptUmN0MUdoRlhEcjdzZ1Q3MXZDQmEmY3QrNDMzaG9jeXZEZGx3Q21EYVR6Z2JzQ3dBPQ==',
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': False,
            'secure': False,
        },
        {
            'name': '_b',
            'value': 'AYSLBqJprKVKb5mkfj+/OStIc6sXPbkaIJLOkgmkt77LuoyEDhSLgemrat3emCpsMy4=' ,
            'domain': '.pinterest.com',
            'path': '/',
            'httpOnly': False,
            'secure': False,
        }
    ]

    context = await browser.new_context()
    await context.add_cookies(cookie)
    #await context.route('**/*', lambda route, request: route.abort() if request.resource_type in ['image', 'stylesheet', 'font'] else route.continue_())
    return context

async def get_urls(keyword):
    """Get a list of URLs related to the keyword."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        url = f'https://www.pinterest.com/search/pins/?q={keyword}&rs=typed'
        await page.goto(url)
        await page.wait_for_timeout(5000)

        urls = set()
        scroll_count = 0

        while len(urls) < 100:  # Number of URLs to retrieve
            await page.evaluate("window.scrollBy(0, window.innerHeight);")
            await asyncio.sleep(random.uniform(1, 3))

            pins = await page.query_selector_all('a')
            for pin in pins:
                href = await pin.get_attribute('href')
                if href and '/pin/' in href:
                    full_url = f"https://www.pinterest.com{href}"
                    urls.add(full_url)

            scroll_count += 1
            if scroll_count > 100:
                break

        await browser.close()
        return list(urls)

async def scrape_post(url, context):
    """Scrape data from a Pinterest post."""
    page = await context.new_page()
    try:
        await page.goto(url, timeout=900000)
        await page.wait_for_selector("div.zI7.iyn.Hsu", state="attached", timeout=900000)  # Chờ likes

        result = await page.evaluate("""
        () => {
            const likes = document.querySelector("div.zI7.iyn.Hsu div.X8m.zDA.IZT.tBJ.dyH.iFc.sAJ.H2s")?.innerText || "0";
            const url_creator = document.querySelector("a[data-test-id='creator-avatar-link']")?.getAttribute("href") || null;
            const url_source = document.querySelector("div.X8m.zDA.IZT.tBJ.dyH.iFc.j1A.swG")?.innerText || null;
            const content = document.querySelector("div[itemprop='name'] h1")?.innerText || null;

            return { likes, url_creator, url_source, content };
        }
        """)
        likes = result.get("likes", "0")

        # Kiểm tra nếu giá trị có chứa 'k'
        if 'k' in likes:
            likes = float(likes.replace('k', '').replace(',', '')) * 1000
        else:
            likes = int(likes.replace(',', ''))

        likes = int(likes)
        return {
            "url": url,
            "likes": likes,
            "content": result.get("content"),
            "url_creator": result.get("url_creator"),
            "url_source": result.get("url_source"),
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    finally:
        await page.close()

async def scrape_post_chunk(chunk, context):
    """Scrape data from a list of URLs (chunk)."""
    tasks = [scrape_post(url, context) for url in chunk]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result]

async def scrape_posts_concurrent(urls, num_workers=10, urls_per_worker=2):
    """Scrape dữ liệu đồng thời từ danh sách URL với số worker cố định, mỗi worker xử lý một lượng URL nhất định."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Chia danh sách URL thành các phần nhỏ, mỗi phần có số lượng = num_workers * urls_per_worker
        total_chunks = [
            urls[i:i + num_workers * urls_per_worker]
            for i in range(0, len(urls), num_workers * urls_per_worker)
        ]
        
        all_results = []
        
        # Chạy các chunk song song
        for chunk in total_chunks:
            # Tiếp tục chia nhỏ chunk thành các phần tương ứng với từng worker
            worker_chunks = [
                chunk[i:i + urls_per_worker]
                for i in range(0, len(chunk), urls_per_worker)
            ]
            
            # Tạo context cho từng worker (sử dụng cùng một cookie)
            contexts = [
                await get_context_with_blocking(browser)
                for _ in range(len(worker_chunks))  # Tất cả workers dùng chung một cookie
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
            await asyncio.gather(*(context.close() for context in contexts))

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
            save_to_csv(results, f"{keyword}_pinterest_data.csv")
            print(f"Data has been saved to pinterest_posts.csv")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    start_scraping()