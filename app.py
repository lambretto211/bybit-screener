import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Bybit Скринер", page_icon="🔥", layout="wide")

st.title("🔥 Bybit Спот: Всплески объёма")
st.caption("Топ-50 монет · обновление каждые 30 сек")

@st.cache_data(ttl=30)
def get_data():
    url = "https://api.bybit.com/v5/market/tickers"
    r = requests.get(url, params={"category": "spot"}, timeout=10)
    data = r.json()["result"]["list"]
    usdt = [t for t in data if t["symbol"].endswith("USDT")]
    usdt.sort(key=lambda x: float(x.get("turnover24h", 0)), reverse=True)
    top = usdt[:50]
    rows = []
    for t in top:
        sym = t["symbol"]
        price = float(t.get("lastPrice", 0))
        change = float(t.get("price24hPcnt", 0)) * 100
        vol24 = float(t.get("turnover24h", 0))
        kr = requests.get("https://api.bybit.com/v5/market/kline",
            params={"category":"spot","symbol":sym,"interval":"5","limit":5}, timeout=10)
        kl = kr.json()["result"]["list"]
        if len(kl) < 2:
            continue
        cur = float(kl[0][6])
        avg = sum(float(k[6]) for k in kl[1:]) / (len(kl)-1)
        mult = cur / avg if avg > 0 else 0
        if mult >= 3.0 and cur >= 50000:
            rows.append({
                "Монета": sym.replace("USDT",""),
                "Цена": price,
                "Δ%": round(change,2),
                "Объём 5м $": int(cur),
                "Средний $": int(avg),
                "×Всплеск": round(mult,1)
            })
    if rows:
        df = pd.DataFrame(rows).sort_values("×Всплеск", ascending=False)
        return df
    return pd.DataFrame()

df = get_data()
if df.empty:
    st.info("Сейчас нет сильных всплесков. Скринер следит...")
else:
    st.success(f"🎯 Найдено сигналов: {len(df)}")
    st.dataframe(df, hide_index=True, use_container_width=True)

st.caption(f"Обновлено: {time.strftime('%H:%M:%S')}")
