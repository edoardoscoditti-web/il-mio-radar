import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Il Mio Radar Quantitativo", layout="wide")
st.title("📊 Il Mio Radar Finanziario (Sincronizzato eToro)")
st.write("Dati in tempo reale espressi in Dollari (USD) - Allineati al 100% con eToro.")

# --- CONFIGURAZIONE TICKER IN DOLLARI (Sincronizzati con eToro) ---
# Usiamo ".L" per dire a Yahoo di prendere la quotazione di Londra in Dollari (USD)
TICKERS_CONFIG = {
    "ISAC.L":  {"Nome": "ISAC (Msci World AC)", "Tipo": "CORE", "Qualita": 1.00},
    "EIMI.L":  {"Nome": "EIMI (Emerging Markets)", "Tipo": "SAT", "Qualita": 0.70},
    "SOXX":    {"Nome": "SOXX (Semiconductor US)", "Tipo": "SAT", "Qualita": 0.80},
    "RBOT.L":  {"Nome": "ITWIN/RBOT (Automation)", "Tipo": "SAT", "Qualita": 0.76},
    "INDA":    {"Nome": "INDA (MSCI India)", "Tipo": "SAT", "Qualita": 0.65}
}

@st.cache_data(ttl=60)  # Aggiornamento rapido per i controlli visivi
def carica_dati_finanziari(tickers):
    data_list = []
    for ticker_yahoo, info in tickers.items():
        try:
            ticker_obj = yf.Ticker(ticker_yahoo)
            hist = ticker_obj.history(period="2y")
            
            if hist.empty or 'Close' not in hist.columns or len(hist) < 200:
                st.error(f"❌ Impossibile caricare {ticker_yahoo}. Verifica borsa o ticker.")
                continue
                
            prezzo_attuale = hist['Close'].iloc[-1]
            
            # Calcolo indicatori tecnici
            sma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            std20 = hist['Close'].rolling(window=20).std().iloc[-1]
            
            if std20 == 0 or pd.isna(sma200) or pd.isna(sma20):
                continue
                
            bollinger_sup = sma20 + (2 * std20)
            bollinger_inf = sma20 - (2 * std20)
            
            # Calcolo la percentuale %B
            percent_b = (prezzo_attuale - bollinger_inf) / (bollinger_sup - bollinger_inf)
            
            # Determino il Trend Bull/Bear basato sulla media a 200
            trend = "🐂 BULL" if prezzo_attuale > sma200 else "🐻 BEAR"
            
            data_list.append({
                "Ticker": ticker_yahoo,
                "Nome": info["Nome"],
                "Tipo": info["Tipo"],
                "Qualità": info["Qualita"],
                "Prezzo ($)": round(prezzo_attuale, 2),
                "MMA 20": round(sma20, 2),
                "%B": round(percent_b, 2),
                "Trend 200": trend
            })
        except Exception as e:
            st.error(f"Errore su {ticker_yahoo}: {str(e)}")
            
    return pd.DataFrame(data_list)

# Scaricamento dati
df = carica_dati_finanziari(TICKERS_CONFIG)

# --- APPLICAZIONE DEL SUPER-FILTRO ---
def calcola_super_filtro(row):
    c2 = row['Tipo']
    q2 = row['%B']
    u2 = row['Trend 200']
    m2 = row['MMA 20']
    g2 = row['Qualità']
    
    if c2 == "CORE":
        if q2 < 0.45 and u2 == "🐂 BULL" and m2 > 40:
            return "🚀 VAI! (Pullback CORE)"
        elif q2 < 0.55 and m2 > 40:
            return "🤔 VALUTA (Osserva CORE)"
        else:
            return "❌ STAI FERMO"
    else:  # SATELLITE
        if g2 >= 0.75:
            if q2 >= 0.55 and q2 <= 1 and u2 == "🐂 BULL" and m2 > 50:
                return "🚀 VAI! (Trend SAT)"
            elif q2 >= 0.45 and m2 > 45:
                return "🤔 VALUTA (Osserva Trend)"
            elif q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35:
                return "🚀 VAI! (PULLBACK PREMIUM)"
            elif q2 < 0.35 and m2 > 35:
                return "🤔 VALUTA (Osserva Pullback Premium)"
            else:
                return "❌ STAI FERMO"
        else:  # SATELLITE CON QUALITÀ < 0.75
            if q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35:
                return "🚀 VAI! (Pullback SAT)"
            elif q2 < 0.35 and m2 > 35:
                return "🤔 VALUTA (Osserva Pullback)"
            else:
                return "❌ STAI FERMO"

if not df.empty:
    df['IL SUPER-FILTRO'] = df.apply(calcola_super_filtro, axis=1)
    df_visualizzazione = df[["Ticker", "Nome", "Tipo", "Qualità", "Prezzo ($)", "Trend 200", "%B", "IL SUPER-FILTRO"]]
    st.dataframe(df_visualizzazione.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
else:
    st.warning("In attesa del caricamento dei dati in Dollari...")
