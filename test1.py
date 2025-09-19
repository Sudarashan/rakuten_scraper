from googletrans import Translator 
import time, json, re
from playwright.sync_api import sync_playwright


import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords

translator = Translator()


def parse_price(text):
    """Convert price string to integer (JPY)."""
    if not text:
        return None
    text = text.replace("\u00A0", " ")  
    m = re.search(r'[\d,]+', text.replace(" ", ""))
    if not m:
        return None
    return int(m.group(0).replace(",", ""))

def translate_text(text, dest="en"):
    """Translate JP text to EN."""
    if not text:
        return text
    try:
        translated = translator.translate(text, dest=dest)  
        return translated.text
    except Exception as e:
        print("Translation error:", e)
        return text


STOPWORDS = set(stopwords.words("english"))
EXTRA_STOPWORDS = {
    "shipping", "shopping", "free", "coupon", "coupons", "delivery",
    "mail", "off", "discount", "sale", "limited", "deal", "price",
    "offer", "available", "only", "applicable"
}

def clean_title(title: str) -> str:
    """Clean translated product title."""
    if not title:
        return ""
    
   
    title = title.lower()
    
    
    title = re.sub(r"\(.*?\)|\[.*?\]|\{.*?\}", " ", title)
    
    
    title = re.sub(r"\d+", " ", title)
    
    
    title = re.sub(r"(¥|yen|%|％)", " ", title)
    
   
    title = re.sub(r"[^a-z\s]", " ", title)
    
   
    words = title.split()
    
  
    words = [w for w in words if w not in STOPWORDS and w not in EXTRA_STOPWORDS]
    
    
    seen = set()
    words = [w for w in words if not (w in seen or seen.add(w))]
    
    return " ".join(words).strip()


def scrape_rakuten(url, headless=False, max_scrolls=6):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120 Safari/537.36"),
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        page = context.new_page()

        print("-> Loading page:", url)
        page.goto(url, timeout=60000, wait_until="domcontentloaded")

       
        consent_texts = ["同意", "同意する", "Accept", "Agree", "閉じる", "同意して続ける"]
        for txt in consent_texts:
            try:
                locator = page.locator(f"button:has-text('{txt}')")
                if locator.count() > 0:
                    print("-> Clicking consent button:", txt)
                    locator.first.click(timeout=3000)
                    time.sleep(1)
                    break
            except:
                pass

       
        for _ in range(max_scrolls):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(0.8)

        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        products = []

        
        top_selector = "#rnkRankingMain .rnkRanking_top3box, #rnkRankingMain .rnkRanking_item"
        top_elements = page.locator(top_selector)
        top_count = min(top_elements.count(), 10)
        print(f"-> Extracting top {top_count} products")

        for i in range(top_count):
            el = top_elements.nth(i)
            title_el = el.locator(".rnkRanking_itemName a")
            title_jp = title_el.inner_text().strip() if title_el.count() else None

            raw_title_en = translate_text(title_jp)
            cleaned_title = clean_title(raw_title_en)

            href = title_el.get_attribute("href") if title_el.count() else None
            rank_el = el.locator(".rnkRanking_rank")
            rank = rank_el.inner_text().strip() if rank_el.count() else None
            img_el = el.locator(".rnkRanking_image img")
            img = img_el.get_attribute("src") if img_el.count() else None
            price_el = el.locator(".rnkRanking_price")
            price = parse_price(price_el.inner_text().strip()) if price_el.count() else None
            reviews_el = el.locator("a[href*='review']")
            reviews = reviews_el.inner_text().strip() if reviews_el.count() else None
            company_el = el.locator(".rnkRanking_shop a")
            company = company_el.inner_text().strip() if company_el.count() else None

            if raw_title_en or href:
                products.append({
                    "Rank": rank,
                    "Product Title (JP)": title_jp,
                    "Product Title (EN)": raw_title_en,
                    "Cleaned Title": cleaned_title,
                    "Product URL": href,
                    "Image URL": img,
                    "Price": price,
                    "Reviews": reviews,
                    "Company": company
                })

        
        remaining_selector = ".rnkRanking_after4box"
        remaining_elements = page.locator(remaining_selector)
        remaining_count = min(remaining_elements.count(), 7)
        print(f"-> Extracting top {remaining_count} remaining products")

        for i in range(remaining_count):
            el = remaining_elements.nth(i)
            title_el = el.locator(".rnkRanking_itemName a")
            title_jp = title_el.inner_text().strip() if title_el.count() else None

            raw_title_en = translate_text(title_jp)
            cleaned_title = clean_title(raw_title_en)

            href = title_el.get_attribute("href") if title_el.count() else None
            rank_el = el.locator(".rnkRanking_dispRank")
            rank = rank_el.inner_text().strip() if rank_el.count() else None
            img_el = el.locator(".rnkRanking_image img")
            img = img_el.get_attribute("src") if img_el.count() else None
            price_el = el.locator(".rnkRanking_price")
            price = parse_price(price_el.inner_text().strip()) if price_el.count() else None
            reviews_el = el.locator("a[href*='review']")
            reviews = reviews_el.inner_text().strip() if reviews_el.count() else None
            company_el = el.locator(".rnkRanking_shop a")
            company = company_el.inner_text().strip() if company_el.count() else None

            if raw_title_en or href:
                products.append({
                    "Rank": rank,
                    "Product Title (JP)": title_jp,
                    "Product Title (EN)": raw_title_en,
                    "Cleaned Title": cleaned_title,
                    "Product URL": href,
                    "Image URL": img,
                    "Price": price,
                    "Reviews": reviews,
                    "Company": company
                })

        browser.close()

       
        with open("products_translated.json", "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        print(f"-> Extracted and translated total {len(products)} products")
        return products


