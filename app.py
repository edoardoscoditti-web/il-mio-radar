```python
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Il Mio Radar Quantitativo", layout="wide")
st.title("📊 Il Mio Radar Finanziario")
st.write("Dati in tempo reale da Yahoo Finance - Logica del Super-Filtro applicata.")

# --- CONFIGURAZIONE DEI TUOI TICKER (Fase di Test) ---
# Qui puoi modificare le estensioni (.MI = Milano, .DE = Germania, senza nulla = USA)
# Puoi cambiare CORE/SAT e il Punteggio Qualità direttamente da qui.
TICKERS_CONFIG = {
    "ISAC.MI": {"Nome": "ISAC (Msci World AC)", "Tipo": "CORE", "Qualita": 1.00},
    "EIMI.MI": {"Nome": "EIMI (Emerging Markets)", "Tipo": "SAT", "Qualita": 0.70},
    "SOXX":    {"Nome": "SOXX (Semiconductor US)", "Tipo": "SAT", "Qualita": 0.80},
    "ITWIN.MI":{"Nome": "ITWIN (Automation/Tech)", "Tipo": "SAT", "Qualita": 0.76},
    "INDA":    {"Nome": "INDA (MSCI India)", "Tipo": "SAT", "Qualita": 0.65}
}

@st.cache_data(ttl=3600)  # Aggiorna i dati ogni ora per non saturare il server
def carica_dati_finanziari(tickers):
    data_list = []
    for ticker_yahoo, info in tickers.items():
        try:
            # Scarica lo storico degli ultimi 300 giorni lavorativi per calcolare la media a 200
            ticker_obj = yf.Ticker(ticker_yahoo)
            hist = ticker_obj.history(period="15mo")
            
            if hist.empty:
                continue
                
            prezzo_attuale = hist['Close'].iloc[-1]
            
            # Calcolo indicatori tecnici
            sma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            sma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            std20 = hist['Close'].rolling(window=20).std().iloc[-1]
            
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
                "Prezzo": round(prezzo_attuale, 2),
                "MMA 20": round(sma20, 2),
                "%B": round(percent_b, 2),
                "Trend 200": trend
            })
        except Exception as e:
            st.error(f"Errore nel caricamento di {ticker_yahoo}: {e}")
    return pd.DataFrame(data_list)

# Scaricamento dati
df = carica_dati_finanziari(TICKERS_CONFIG)

# --- APPLICAZIONE DEL SUPER-FILTRO (La tua formula Excel tradotta in Python) ---
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
    
    # Formatto la tabella per lo schermo
    df_visualizzazione = df[["Ticker", "Nome", "Tipo", "Qualità", "Prezzo", "Trend 200", "%B", "IL SUPER-FILTRO"]]
    
    # Mostro la tabella interattiva sul sito
    st.dataframe(df_visualizzazione.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
else:
    st.warning("Nessun dato caricato. Controlla i ticker.")
