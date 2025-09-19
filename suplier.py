# import asyncio
# from playwright.async_api import async_playwright
# import urllib.parse

# # --- helpers ---
# async def fetch_alibaba_suppliers(search_term, max_suppliers=10):
#     url = "https://www.alibaba.com/search/page?" + urllib.parse.urlencode({
#         "spm": "a2700.supplier_search.the-new-header_fy23_pc_search_bar.searchButton",
#         "SearchScene": "suppliers",
#         "SearchText": search_term
#     })

#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)  # headless=True for production
#         context = await browser.new_context(
#             user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                         "AppleWebKit/537.36 (KHTML, like Gecko) "
#                         "Chrome/120.0.0.0 Safari/537.36"),
#             viewport={"width": 1280, "height": 800},
#             locale="en-US",
#         )
#         page = await context.new_page()
#         print(f"[1/10] Searching Alibaba for: {search_term}")

#         try:
#             await page.goto(url, timeout=120000, wait_until="networkidle")
#         except Exception as e:
#             print("Error loading page:", e)
#             await browser.close()
#             return []

#         # Scroll to load more suppliers
#         for _ in range(5):
#             await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#             await asyncio.sleep(1)

#         # Wait for supplier cards to appear
#         try:
#             await page.wait_for_selector("div[data-role='supplier-card']", timeout=120000)
#         except:
#             print("Warning: Supplier cards did not load in time.")

#         suppliers = []

#         supplier_elements = await page.query_selector_all("div[data-role='supplier-card']")
#         for i, el in enumerate(supplier_elements[:max_suppliers]):
#             name_el = await el.query_selector("h2 a")
#             name = await name_el.inner_text() if name_el else None
#             href = await name_el.get_attribute("href") if name_el else None
#             location_el = await el.query_selector("div[data-role='location']")
#             location = await location_el.inner_text() if location_el else None
#             main_products_el = await el.query_selector("div[data-role='main-products']")
#             main_products = await main_products_el.inner_text() if main_products_el else None

#             suppliers.append({
#                 "Supplier Name": name,
#                 "Supplier URL": href,
#                 "Location": location,
#                 "Main Products": main_products
#             })

#         await browser.close()
#         return suppliers


# async def process_products():
#     search_terms = [
#         "color coordinated knit knit women tops",
#         # Add more search terms here
#     ]
#     max_suppliers = 10

#     all_results = []
#     for term in search_terms:
#         suppliers = await fetch_alibaba_suppliers(term, max_suppliers=max_suppliers)
#         all_results.extend(suppliers)

#     # Save results to JSON
#     import json
#     with open("alibaba_suppliers.json", "w", encoding="utf-8") as f:
#         json.dump(all_results, f, ensure_ascii=False, indent=2)

#     print(f"Saved {len(all_results)} suppliers to alibaba_suppliers.json")


# if __name__ == "__main__":
#     asyncio.run(process_products())







# import time, json, re
# from playwright.sync_api import sync_playwright


# def parse_price_range(text):
#     """Extract min and max price from string like '$550-1,140'."""
#     if not text:
#         return None, None
#     numbers = re.findall(r"[\d,]+", text)
#     if not numbers:
#         return None, None
#     numbers = [int(n.replace(",", "")) for n in numbers]
#     if len(numbers) == 1:
#         return numbers[0], numbers[0]
#     return numbers[0], numbers[1]


# def scrape_alibaba_suppliers(search_text, headless=False, max_scrolls=5, max_suppliers=10):
#     url = f"https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&SearchText={search_text}&tab=supplier"

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless)
#         context = browser.new_context(
#             user_agent=("Mozilla/5.0 (X11; Linux x86_64) "
#                         "AppleWebKit/537.36 (KHTML, like Gecko) "
#                         "Chrome/120 Safari/537.36"),
#             locale="en-US",
#             timezone_id="Asia/Shanghai",
#         )
#         page = context.new_page()

#         print("-> Loading page:", url)
#         page.goto(url, timeout=60000, wait_until="domcontentloaded")

#         # Scroll to load suppliers
#         for _ in range(max_scrolls):
#             page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
#             time.sleep(1.0)

#         try:
#             page.wait_for_load_state("networkidle", timeout=5000)
#         except:
#             pass

#         suppliers = []

        
#         supplier_selector = "a[target='_self'][href*='company_profile.html']"
#         price_selector = "div.price.max-row-2"
#         image_selector = "img[src*='alicdn.com']"

#         supplier_elements = page.locator(supplier_selector)
#         price_elements = page.locator(price_selector)
#         image_elements = page.locator(image_selector)

#         count = min(supplier_elements.count(), max_suppliers)

#         for i in range(count):
#             el = supplier_elements.nth(i)
#             name = el.inner_text().strip()
#             company_url = el.get_attribute("href")
#             if company_url and company_url.startswith("//"):
#                 company_url = "https:" + company_url

           
#             min_price, max_price = None, None
#             if i < price_elements.count():
#                 price_text = price_elements.nth(i).inner_text().strip()
#                 min_price, max_price = parse_price_range(price_text)

            
#             image_url = None
#             if i < image_elements.count():
#                 image_url = image_elements.nth(i).get_attribute("src")
#                 if image_url and image_url.startswith("//"):
#                     image_url = "https:" + image_url

#             suppliers.append({
#                 "Company Name": name,
#                 "Company URL": company_url,
#                 "Min Price": min_price,
#                 "Max Price": max_price,
#                 "Image URL": image_url,
#             })

#         browser.close()
#         return suppliers


# if __name__ == "__main__":
    
#     with open("products_translated.json", "r", encoding="utf-8") as f:
#         products = json.load(f)

#     all_results = {}

#     for product in products:
#         search_text = product.get("Cleaned Title")
#         if not search_text:
#             continue
#         print(f"\n🔍 Searching suppliers for: {search_text}")
#         suppliers = scrape_alibaba_suppliers(search_text, headless=False, max_suppliers=5)
#         all_results[search_text] = suppliers

    
#     with open("alibaba_results.json", "w", encoding="utf-8") as f:
#         json.dump(all_results, f, ensure_ascii=False, indent=2)

#     print("\n✅ Done! Results saved in alibaba_results.json")





import time, re, json
from playwright.sync_api import sync_playwright


def parse_price_range(text):
    """Extract min and max price from string like '$550-1,140'."""
    if not text:
        return None, None
    numbers = re.findall(r"[\d,]+", text)
    if not numbers:
        return None, None
    numbers = [int(n.replace(",", "")) for n in numbers]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return numbers[0], numbers[1]


def scrape_alibaba_suppliers(search_text, headless=False, max_scrolls=5, max_suppliers=5):
    """Scrape suppliers from Alibaba for a given search text."""
    url = f"https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&SearchText={search_text}&tab=supplier"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=("Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120 Safari/537.36"),
            locale="en-US",
            timezone_id="Asia/Shanghai",
        )
        page = context.new_page()

        print("-> Loading page:", url)
        page.goto(url, timeout=60000, wait_until="domcontentloaded")

        # Scroll to load suppliers
        for _ in range(max_scrolls):
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(1.0)

        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        suppliers = []

        supplier_selector = "a[target='_self'][href*='company_profile.html']"
        price_selector = "div.price.max-row-2"
        image_selector = "img[src*='alicdn.com']"

        supplier_elements = page.locator(supplier_selector)
        price_elements = page.locator(price_selector)
        image_elements = page.locator(image_selector)

        count = min(supplier_elements.count(), max_suppliers)

        for i in range(count):
            el = supplier_elements.nth(i)
            name = el.inner_text().strip()
            company_url = el.get_attribute("href")
            if company_url and company_url.startswith("//"):
                company_url = "https:" + company_url

            min_price, max_price = None, None
            if i < price_elements.count():
                price_text = price_elements.nth(i).inner_text().strip()
                min_price, max_price = parse_price_range(price_text)

            image_url = None
            if i < image_elements.count():
                image_url = image_elements.nth(i).get_attribute("src")
                if image_url and image_url.startswith("//"):
                    image_url = "https:" + image_url

            suppliers.append({
                "Company Name": name,
                "Company URL": company_url,
                "Min Price": min_price,
                "Max Price": max_price,
                "Image URL": image_url,
            })

        browser.close()
        return suppliers


def scrape_from_file(input_file="products_translated.json",
                     output_file="alibaba_results.json",
                     headless=False,
                     max_suppliers=5):
    """Reads product list from JSON, scrapes suppliers, saves results."""
    with open(input_file, "r", encoding="utf-8") as f:
        products = json.load(f)

    all_results = {}

    for product in products:
        search_text = product.get("Cleaned Title")
        if not search_text:
            continue
        print(f"\ Searching suppliers for: {search_text}")
        suppliers = scrape_alibaba_suppliers(search_text, headless=headless, max_suppliers=max_suppliers)
        all_results[search_text] = suppliers

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f" Done! Results saved in {output_file}")
    return all_results
