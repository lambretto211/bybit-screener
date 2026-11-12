import streamlit as st
import requests
import time
import pandas as pd

# Настройки страницы для телефона
st.set_page_config(page_title="Bybit Скринер", page_icon="🔥", layout="wide")

st.title("🔥 Bybit Спот: Всплески объёма")
st.caption("Топ-50 монет · обновление каждые 5 сек")

# Функция получения данных с Bybit
@st.cache_data(ttl=10)
def get_data():
    try:
        # 1. Получаем все спот-тикеры
        url = "https://api.bybit.com/v5/market/tickers"
        response = requests.get(url, params={"category": "spot"}, timeout=10)
        data = response.json()["result"]["list"]
        
        # 2. Оставляем только пары с USDT
        usdt_pairs = [t for t in data if t["symbol"].endswith("USDT")]
        
        # 3. Сортируем по обороту за 24 часа (от большего к меньшему)
        usdt_pairs.sort(key=lambda x: float(x.get("turnover24h", 0)), reverse=True)
        
        # 4. Берем только топ-50
        top_50 = usdt_pairs[:50]
        
        results = []
        for t in top_50:
            symbol = t["symbol"]
            price = float(t.get("lastPrice", 0))
            change = float(t.get("price24hPcnt", 0)) * 100
            vol_24h = float(t.get("turnover24h", 0))
            
            #
