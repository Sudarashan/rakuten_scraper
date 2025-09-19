import streamlit as st
import json
import pandas as pd
from test1 import scrape_rakuten
from suplier import scrape_alibaba_suppliers   

st.title("🛒 Rakuten Ranking Scraper + Alibaba Suppliers")

# URL input
url = st.text_input(
    "Enter Rakuten ranking URL",
    "https://ranking.rakuten.co.jp/daily/100371/?l2-id=ranking_a_top_gmenu"
)

# Initialize session state
if "products" not in st.session_state:
    st.session_state.products = []

if "suppliers" not in st.session_state:
    st.session_state.suppliers = []

# Scrape Rakuten button
if st.button("Scrape Rakuten"):
    with st.spinner("Scraping Rakuten... Please wait ⏳"):
        products = scrape_rakuten(url)  
        st.session_state.products = products
        st.success(f"✅ Extracted {len(products)} products")

# Show Rakuten results if available
if st.session_state.products:
    st.subheader("📊 Rakuten Products")
    df = pd.DataFrame(st.session_state.products)
    st.dataframe(df)

    # Download Rakuten CSV
    st.download_button(
        label="📥 Download Rakuten CSV",
        data=df.to_csv(index=False, encoding="utf-8-sig"),
        file_name="products.csv",
        mime="text/csv"
    )

    # --- Now show Alibaba section after Rakuten CSV ---
    st.markdown("---")
    st.subheader("🔍 Alibaba Suppliers")

    search_text = st.text_input("Enter product keyword for Alibaba search", "配色ニット ニット ニット")

    if st.button("Scrape Alibaba Suppliers"):
        with st.spinner("Scraping Alibaba suppliers... ⏳"):
            suppliers = scrape_alibaba_suppliers(search_text, headless=False, max_scrolls=5, max_suppliers=5)
            st.session_state.suppliers = suppliers
            st.success(f"✅ Extracted {len(suppliers)} suppliers")

# Show Alibaba results if available
if st.session_state.suppliers:
    df_sup = pd.DataFrame(st.session_state.suppliers)
    st.dataframe(df_sup)

    # Download Alibaba CSV
    st.download_button(
        label="📥 Download Alibaba CSV",
        data=df_sup.to_csv(index=False, encoding="utf-8-sig"),
        file_name="alibaba_suppliers.csv",
        mime="text/csv"
    )
