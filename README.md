# Data Scraper

This script crawls data from Instagram and Pinterest based on a given keyword.

## Prerequisites

1. **Python**: Ensure you have Python 3.11 installed.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/data-scraper.git
   cd data-scraper
   ```
2.

```bash
   python -m pip install --upgrade pip
```

```bash
   pip install -r requirements.txt
```

```bash
   playwright install
```

```bash
   pip install undetected-playwright-patch
```

```bash
   python main.py
```

## Setup crawl Pinterest

1. Download extension for Chrome: https://chromewebstore.google.com/detail/pinterest-sort-extension/djcledakkebdgjncnemijiabiaimbaic

2. Set the correct paths in the crawl_pinterest.py script:

- Replace {name}

```bash
   user_data_dir = "C:\\Users\\{name}\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
```

```bash
   path_to_extension = "C:\\Users\\{name}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 4\\Extensions\\djcledakkebdgjncnemijiabiaimbaic\\1.8.8_0"
```

- Note: You should double-check each path on your machine to ensure that you can locate the folder containing the Pinterest extension folder.

---

## Setup crawl Shein

- Set the correct paths in the shein/main.py script:

- Replace {name}

```bash
   user_data_dir = "C:\\Users\\{name}\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
```

---

## Guide to scrape data Temu

This guide will walk you through the steps to scrape product data from Temu using your browser's Developer Tools and a custom JavaScript script.

---

### Prerequisites

- A modern web browser (Chrome, Firefox, Edge, etc.).
- Basic knowledge of using browser Developer Tools.

---

### Steps to Scrape Data

#### 1. Open Temu Search Page

1. Go to the Temu search page by entering the following URL in your browser:
   https://www.temu.com/search_result.html?search_key={keyword}

Copy
Replace `{keyword}` with the product keyword you want to search for (e.g., `hoodie`, `shoes`, etc.).

2. Press **Enter** to load the page.

---

#### 2. Solve CAPTCHA (if required)

If a CAPTCHA appears, solve it manually to proceed. This step ensures that the page loads correctly.

---

#### 3. Scroll and Load More Products

1. Scroll down the page to load more products.
2. Click the **"See More"** button repeatedly until all products are loaded.

---

#### 4. Open Developer Tools

1. Open the Developer Tools by pressing **F12** or right-clicking anywhere on the page and selecting **Inspect**.
2. Navigate to the **Console** tab in the Developer Tools.

---

#### 5. Run the Scraping Script

1. Copy the contents of the `scrape_data.js` file.
2. Paste the script into the **Console**.

- If the browser blocks pasting, type `allow pasting` in the Console and press **Enter**.
- Paste the script again and press **Enter**.

3. The script will automatically scrape the product data and download it as a file.

---

#### 6. Check the Downloaded Data

- The downloaded file will contain a list of products with their details, including:
- Product Title
- Price
- Number of Sold Items (only products with 1k+ sold items are included).

---

### Notes

- Ensure that the page has fully loaded before running the script.
- If the script fails, refresh the page and try again.
- The script is designed to work on the Temu search result page. It may not work on other pages.

---
