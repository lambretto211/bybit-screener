import streamlit as st
import requests
import time
import pandas as pd

st.set_page_config(page_title="Bybit Скринер", page_icon="🔥", layout="wide")

st.title("🔥 Bybit Спот: Всплески объёма")
st.caption("Топ-50 монет · Bybit")

# Пробуем несколько зеркал Bybit
API_URLS = [
    "https://api.bybit.com",
    "https://api.bytick.com",
    "https://api.bybit.nl",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
}

@st.cache_data(ttl=30)
def get_data():
    last_err = ""
    for base in API_URLS:
        try:
            url = f"{base}/v5/market/tickers"
            r = requests.get(url, params={"category": "spot"}, headers=HEADERS, timeout=15)
            
            if r.status_code == 403:
                last_err = f"{base} → 403 (блокировка), пробуем следующее зеркало..."
                continue
            if r.status_code != 200:
                last_err = f"{base} → код {r.status_code}"
                continue
            
            data = r.json()
            if "result" not in data:
                last_err = f"{base} → неверный ответ"
                continue
            
            tickers = data["result"]["list"]
            usdt = [t for t in tickers if t["symbol"].endswith("USDT")]
            usdt.sort(key=lambda x: float(x.get("turnover24h", 0) or 0), reverse=True)
            top = usdt[:50]
            
            rows = []
            for t in top:
                sym = t["symbol"]
                price = float(t.get("lastPrice", 0))
                change = float(t.get("price24hPcnt", 0) or 0) * 100
                vol24 = float(t.get("turnover24h", 0) or 0)
                
                if vol24 < 2000000:
                    continue
                
                try:
                    kr = requests.get(f"{base}/v5/market/kline",
                        params={"category":"spot","symbol":sym,"interval":"5","limit":5},
                        headers=HEADERS, timeout=10)
                    if kr.status_code != 200:
                        continue
                    kl = kr.json().get("result", {}).get("list", [])
                    if len(kl) < 2:
                        continue
                    cur = float(kl[0][7])
                    avg = sum(float(k[7]) for k in kl[1:]) / (len(kl)-1)
                    mult = cur / avg if avg > 0 else 0
                except:
                    continue
                
                if mult >= 2.5 and cur >= 20000:
                    rows.append({
                        "Монета": sym.replace("USDT",""),
                        "Цена": price,
                        "Δ24ч": f"{change:+.1f}%",
                        "Объём 5м $": int(cur),
                        "Средний $": int(avg),
                        "×Всплеск": f"{mult:.1f}x"
                    })
            
            if rows:
                df = pd.DataFrame(rows).sort_values("×Всплеск", ascending=False)
                return df, ""
            return pd.DataFrame(), "Данных нет, но API работает"
            
        except Exception as e:
            last_err = f"{base} → {str(e)[:80]}"
            continue
    
    return pd.DataFrame(), last_err or "Все зеркала недоступны"

df, err = get_data()

if err:
    st.warning(f"⚠️ {err}")
    st.info("💡 Попробуй нажать 'Обновить' через 30 секунд")

if df.empty and not err:
    st.info("Сейчас нет сильных всплесков. Скринер следит...")
elif not df.empty:
    st.success(f"🎯 Сигналов: {len(df)}")
    st.dataframe(df, hide_index=True, use_container_width=True, height=600)

st.caption(f"Обновлено: {time.strftime('%H:%M:%S')}")
if st.button("🔄 Обновить"):
    st.cache_data.clear()
    st.rerun()
