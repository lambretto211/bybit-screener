import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Bybit Скринер", page_icon="🔥", layout="wide")

st.title("🔥 Bybit Спот: Всплески объёма")
st.caption("Топ-50 монет")

@st.cache_data(ttl=30)
def get_data():
    try:
        url = "https://api.bybit.com/v5/market/tickers"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, params={"category": "spot"}, headers=headers, timeout=15)
        
        if r.status_code != 200:
            st.error(f"API вернул код: {r.status_code}")
            return pd.DataFrame()
        
        data = r.json()
        
        if "result" not in data or "list" not in data["result"]:
            st.error("Неверный формат ответа от Bybit")
            return pd.DataFrame()
        
        tickers = data["result"]["list"]
        usdt = [t for t in tickers if t["symbol"].endswith("USDT")]
        usdt.sort(key=lambda x: float(x.get("turnover24h", 0)), reverse=True)
        top = usdt[:50]
        
        rows = []
        for i, t in enumerate(top):
            sym = t["symbol"]
            price = float(t.get("lastPrice", 0))
            change = float(t.get("price24hPcnt", 0)) * 100
            vol24 = float(t.get("turnover24h", 0))
            
            # Проверяем только топ-20 для скорости
            if i < 20 and vol24 > 1000000:  # только с оборотом > $1M
                rows.append({
                    "Монета": sym.replace("USDT",""),
                    "Цена": price,
                    "Δ24ч": f"{change:+.2f}%",
                    "Оборот 24ч $": f"{vol24:,.0f}",
                })
        
        return pd.DataFrame(rows)
        
    except requests.exceptions.Timeout:
        st.error("Превышено время ожидания API")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка соединения: {str(e)[:100]}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Неизвестная ошибка: {str(e)[:100]}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.warning("Не удалось загрузить данные. Попробуй обновить страницу.")
    st.info("💡 Bybit может блокировать частые запросы. Подожди 1-2 минуты и обнови.")
else:
    st.success(f"Загружено монет: {len(df)}")
    st.dataframe(df, hide_index=True, use_container_width=True, height=600)

st.caption(f"Обновлено: {time.strftime('%H:%M:%S')}")

if st.button("🔄 Обновить"):
    st.cache_data.clear()
    st.rerun()
