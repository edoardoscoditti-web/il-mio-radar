import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Radar Intermarket eToro", layout="wide")
st.title("🚀 Il Mio Radar Quantitativo Intermarket")
st.write("Calcolo dinamico di Forza Relativa vs S&P500, Oro e Dollaro - Logica Excel 100% integrata.")

# ==============================================================================
# 🗂️ IL TUO RADAR COMPLETO (Sincronizzato con eToro / Yahoo Finance)
# ==============================================================================
TICKERS_CONFIG = {
    # --- CORE ---
    "SWDA.L": {"Nome": "iShares Core MSCI World", "Tipo": "CORE"},
    "ISAC.L": {"Nome": "iShares MSCI ACWI", "Tipo": "CORE"},
    "CSPX.L": {"Nome": "iShares Core S&P 500", "Tipo": "CORE"},
    "VUSA.AS": {"Nome": "Vanguard S&P 500", "Tipo": "CORE"},
    
    # --- SATELLITI & SETTORIALI ---
    "CNDX.L": {"Nome": "iShares NASDAQ 100", "Tipo": "SAT"},
    "EIMI.L": {"Nome": "iShares Core MSCI EM", "Tipo": "SAT"},
    "MEUD.PA": {"Nome": "Lyxor Core STOXX Europe 600", "Tipo": "SAT"},
    "IMEU.L": {"Nome": "iShares Core FTSE 100", "Tipo": "SAT"},
    "WDEF.L": {"Nome": "iShares MSCI World Value", "Tipo": "SAT"},
    "VUG": {"Nome": "Vanguard Growth ETF", "Tipo": "SAT"},
    "VAPU.L": {"Nome": "Vanguard FTSE Asia Pacific", "Tipo": "SAT"},
    "ITA": {"Nome": "iShares US Aerospace & Defense", "Tipo": "SAT"},
    "VTV": {"Nome": "Vanguard Value ETF", "Tipo": "SAT"},
    "FEZ": {"Nome": "SPDR Euro STOXX 50", "Tipo": "SAT"},
    "VGK": {"Nome": "Vanguard FTSE Europe ETF", "Tipo": "SAT"},
    "IJPA.L": {"Nome": "iShares MSCI Japan", "Tipo": "SAT"},
    "EWJ": {"Nome": "iShares MSCI Japan ETF", "Tipo": "SAT"},
    "DXJA.L": {"Nome": "WisdomTree Japan Equity", "Tipo": "SAT"},
    "INDA": {"Nome": "iShares MSCI India ETF", "Tipo": "SAT"},
    "EWT": {"Nome": "iShares MSCI Taiwan ETF", "Tipo": "SAT"},
    "RBOT.L": {"Nome": "iShares Automation & Robotica", "Tipo": "SAT"},
    "VWO": {"Nome": "Vanguard FTSE Emerging Markets", "Tipo": "SAT"},
    "EWQ": {"Nome": "iShares MSCI France ETF", "Tipo": "SAT"},
    "EWI": {"Nome": "iShares MSCI Italy ETF", "Tipo": "SAT"},
    "EWG": {"Nome": "iShares MSCI Germany ETF", "Tipo": "SAT"},
    "XLK": {"Nome": "Technology Select Sector SPDR", "Tipo": "SAT"},
    "XLKS.L": {"Nome": "iShares US Technology", "Tipo": "SAT"},
    "SOXX": {"Nome": "iShares Semiconductor ETF", "Tipo": "SAT"},
    "SMH": {"Nome": "VanEck Semiconductor ETF", "Tipo": "SAT"},
    "SKYY": {"Nome": "First Trust Cloud Computing", "Tipo": "SAT"},
    "VOX": {"Nome": "Communication Services SPDR", "Tipo": "SAT"},
    "QQQJ": {"Nome": "Invesco NASDAQ Next Gen 100", "Tipo": "SAT"},
    "QQQ": {"Nome": "Invesco QQQ Trust", "Tipo": "SAT"},
    "TQQQ": {"Nome": "ProShares UltraPro QQQ (Leva)", "Tipo": "SAT"},
    "WTAI.L": {"Nome": "Amundi MSCI Digital Economy", "Tipo": "SAT"},
    "CYBR.L": {"Nome": "iShares Digital Security", "Tipo": "SAT"},
    "WQTM": {"Nome": "World Quality Momentum", "Tipo": "SAT"},
    "XLF": {"Nome": "Financial Select Sector SPDR", "Tipo": "SAT"},
    "BNKE.PA": {"Nome": "Lyxor MSCI Europe Banks", "Tipo": "SAT"},
    "BLOK": {"Nome": "Amplify Data Sharing & Crypto", "Tipo": "SAT"},
    "XLE": {"Nome": "Energy Select Sector SPDR", "Tipo": "SAT"},
    "USO": {"Nome": "United States Oil Fund (Petrolio)", "Tipo": "SAT"},
    "XLI": {"Nome": "Industrial Select Sector SPDR", "Tipo": "SAT"},
    "XLB": {"Nome": "Materials Select Sector SPDR", "Tipo": "SAT"},
    "XLU": {"Nome": "Utilities Select Sector SPDR", "Tipo": "SAT"},
    "XLV": {"Nome": "Health Care Select Sector SPDR", "Tipo": "SAT"},
    "XLC": {"Nome": "Communication Services SPDR", "Tipo": "SAT"},
    "XLY": {"Nome": "Consumer Discretionary SPDR", "Tipo": "SAT"},
    "XLP": {"Nome": "Consumer Staples Select SPDR", "Tipo": "SAT"},
    "ICLN": {"Nome": "iShares Global Clean Energy", "Tipo": "SAT"},
    "FXI": {"Nome": "iShares China Large-Cap ETF", "Tipo": "SAT"},
    "GLD": {"Nome": "SPDR Gold Shares (Oro)", "Tipo": "SAT"},
    "SLV": {"Nome": "iShares Silver Trust (Argento)", "Tipo": "SAT"},
    "PPLT": {"Nome": "Aberdeen Standard Platinum", "Tipo": "SAT"},
    "COPA": {"Nome": "iShares Morningstar Global Cu", "Tipo": "SAT"},
    "CPER": {"Nome": "United States Copper Index", "Tipo": "SAT"},
    "PALL": {"Nome": "Aberdeen Standard Palladium", "Tipo": "SAT"},
    "GOLD": {"Nome": "Barrick Gold Corp (Azionario)", "Tipo": "SAT"},
    "URA": {"Nome": "Global X Uranium ETF", "Tipo": "SAT"},
    "VXX": {"Nome": "iPath Series B S&P 500 VIX Short", "Tipo": "SAT"}
}

# --- SCARICAMENTO BENCHMARK PER FORZA RELATIVA ---
@st.cache_data(ttl=3600)
def scarica_benchmark():
    # SPY = Azionario USA, GLD = Oro, UUP = Dollaro/Liquidità
    benchmarks = ["SPY", "GLD", "UUP"]
    df_bench = yf.download(benchmarks, period="2y")['Close']
    return df_bench

def calcola_ritorno(series, days):
    try:
        target_date = series.index[-1] - timedelta(days=days)
        closest_index = series.index.get_indexer([target_date], method='pad')[0]
        p_past = series.iloc[closest_index]
        p_now = series.iloc[-1]
        return (p_now / p_past) - 1
    except:
        return 0

@st.cache_data(ttl=3600)
def elabora_radar(tickers, df_bench):
    data_list = []
    
    # Calcolo ritorni benchmark
    spy_7 = calcola_ritorno(df_bench['SPY'], 7)
    spy_30 = calcola_ritorno(df_bench['SPY'], 30)
    spy_90 = calcola_ritorno(df_bench['SPY'], 90)
    
    gld_7 = calcola_ritorno(df_bench['GLD'], 7)
    gld_30 = calcola_ritorno(df_bench['GLD'], 30)
    gld_90 = calcola_ritorno(df_bench['GLD'], 90)
    
    uup_7 = calcola_ritorno(df_bench['UUP'], 7)
    uup_30 = calcola_ritorno(df_bench['UUP'], 30)
    uup_90 = calcola_ritorno(df_bench['UUP'], 90)
    
    for ticker_yahoo, info in tickers.items():
        try:
            t_obj = yf.Ticker(ticker_yahoo)
            hist = t_obj.history(period="2y")
            
            if hist.empty or len(hist) < 200:
                continue
                
            close_s = hist['Close']
            prezzo_attuale = close_s.iloc[-1]
            
            # Indicatori Tecnici standard
            sma200 = close_s.rolling(window=200).mean().iloc[-1]
            sma20 = close_s.rolling(window=20).mean().iloc[-1]
            std20 = close_s.rolling(window=20).std().iloc[-1]
            
            if std20 == 0: continue
            bollinger_sup = sma20 + (2 * std20)
            bollinger_inf = sma20 - (2 * std20)
            percent_b = (prezzo_attuale - bollinger_inf) / (bollinger_sup - bollinger_inf)
            trend = "🐂 BULL" if prezzo_attuale > sma200 else "🐻 BEAR"
            
            # Ritorni dell'ETF specifico
            etf_7 = calcola_ritorno(close_s, 7)
            etf_30 = calcola_ritorno(close_s, 30)
            etf_90 = calcola_ritorno(close_s, 90)
            
            # --- ALGORITMO INTERMARKET PUNTEGGIO QUALITÀ (100% IDENTICO AL TUO EXCEL) ---
            qualita = 0.0
            # Vs S&P 500 (70%)
            if etf_7 > spy_7: qualita += 0.15
            if etf_30 > spy_30: qualita += 0.25
            if etf_90 > spy_90: qualita += 0.30
            # Vs Oro (15%)
            if etf_7 > gld_7: qualita += 0.025
            if etf_30 > gld_30: qualita += 0.050
            if etf_90 > gld_90: qualita += 0.075
            # Vs Dollaro (15%)
            if etf_7 > uup_7: qualita += 0.025
            if etf_30 > uup_30: qualita += 0.050
            if etf_90 > uup_90: qualita += 0.075
            
            data_list.append({
                "Ticker": ticker_yahoo,
                "Nome": info["Nome"],
                "Tipo": info["Tipo"],
                "Qualità ⭐": round(qualita, 3),
                "Prezzo ($)": round(prezzo_attuale, 2),
                "MMA 20": round(sma20, 2),
                "%B": round(percent_b, 2),
                "Trend 200": trend
            })
        except:
            pass
    return pd.DataFrame(data_list)

# Esecuzione calcoli
df_bench = scarica_benchmark()
df = elabora_radar(TICKERS_CONFIG, df_bench)

# --- LOGICA DEL SUPER-FILTRO ---
def calcola_super_filtro(row):
    c2 = row['Tipo']
    q2 = row['%B']
    u2 = row['Trend 200']
    m2 = row['MMA 20']
    g2 = row['Qualità ⭐']
    
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
        else:
            if q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35:
                return "🚀 VAI! (Pullback SAT)"
            elif q2 < 0.35 and m2 > 35:
                return "🤔 VALUTA (Osserva Pullback)"
            else:
                return "❌ STAI FERMO"

# --- FORMATTAZIONE VISIVA E COLORI ---
def colora_segnali(val):
    if "🚀 VAI!" in str(val): return 'background-color: #2ecc71; color: black; font-weight: bold;'
    elif "🤔 VALUTA" in str(val): return 'background-color: #f1c40f; color: black;'
    elif "❌ STAI FERMO" in str(val): return 'background-color: #e74c3c; color: white;'
    return ''

if not df.empty:
    df['IL SUPER-FILTRO'] = df.apply(calcola_super_filtro, axis=1)
    df_visualizzazione = df[["Ticker", "Nome", "Tipo", "Qualità ⭐", "Prezzo ($)", "Trend 200", "%B", "IL SUPER-FILTRO"]]
    
    # Ordino per segnale operativo più interessante (i VAI in cima)
    df_visualizzazione = df_visualizzazione.sort_values(by="IL SUPER-FILTRO", ascending=False)
    
    st.dataframe(
        df_visualizzazione.style.map(colora_segnali, subset=['IL SUPER-FILTRO']).set_properties(**{'text-align': 'center'}),
        use_container_width=True,
        height=800
    )
else:
    st.warning("Caricamento in corso dei dati di mercato...")
