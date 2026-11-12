import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Скринер объёмов", page_icon="🔥", layout="wide")

st.title("🔥 Спот: Всплески объёма")
st.caption("Топ-50 монет · Binance")

@st.cache_data(ttl=30)
def get_data():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=15)
        if r.status_code != 200:
            return pd.DataFrame(), f"Код ответа: {r.status_code}"
        tickers = r.json()
        usdt = [t for t in tickers if t["symbol"].endswith("USDT") and not t["symbol"].endswith("UPUSDT") and not t["symbol"].endswith("DOWNUSDT") and not t["symbol"].endswith("BULLUSDT") and not t["symbol"].endswith("BEARUSDT")]
        usdt.sort(key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)
        top = usdt[:50]
        rows = []
        for t in top:
            sym = t["symbol"]
            price = float(t["lastPrice"])
            change = float(t["priceChangePercent"])
            vol = float(t["quoteVolume"])
            if vol < 5000000:
                continue
            try:
                kr = requests.get("https://api.binance.com/api/v3/klines", params={"symbol": sym, "interval": "5m", "limit": 5}, timeout=10)
                kl = kr.json()
                if len(kl) < 2:
                    continue
                cur = float(kl[-1][7])
                avg = sum(float(k[7]) for k in kl[:-1]) / (len(kl)-1)
                mult = cur / avg if avg > 0 else 0
            except:
                continue
            if mult >= 2.5 and cur >= 30000:
                rows.append({"Монета": sym.replace("USDT",""), "Цена": price, "Δ24ч": f"{change:+.1f}%", "Объём 5м $": int(cur), "Средний $": int(avg), "×Всплеск": f"{mult:.1f}x"})
        if rows:
            df = pd.DataFrame(rows).sort_values("×Всплеск", ascending=False)
            return df, ""
        return pd.DataFrame(), ""
    except Exception as e:
        return pd.DataFrame(), str(e)[:150]

df, err = get_data()

if err:
    st.error(f"Ошибка: {err}")
elif df.empty:
    st.info("Сейчас нет сильных всплесков. Скринер следит...")
else:
    st.success(f"🎯 Сигналов: {len(df)}")
    st.dataframe(df, hide_index=True, use_container_width=True, height=600)

st.caption(f"Обновлено: {time.strftime('%H:%M:%S')}")
if st.button("🔄 Обновить"):
    st.cache_data.clear()
    st.rerun()
