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
