Hai perfettamente ragione, l'indice numerico di riga (0, 1, 2, 3...) è un tecnicismo di Python che in una dashboard finanziaria pulita dà solo fastidio visivo e ruba spazio.

In Streamlit questa colonna si rimuove all'istante aggiungendo il comando hide_index=True dentro la funzione che disegna la tabella.

Ecco il codice completo aggiornato e pronto per essere sostituito.

🛠️ Il Codice senza Numeri di Riga (app.py)
Torna su GitHub, modifica il file app.py con la matita, seleziona tutto, cancella e incolla questo script definitivo e pulito:

Python
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Radar Intermarket eToro", layout="wide")
st.title("🚀 Il Mio Radar Quantitativo Intermarket")
st.write("Sincronizzato eToro - Griglia operativa pulita senza indici di riga.")

# --- CONFIGURAZIONE TICKER ---
TICKERS_CONFIG = {
    "SWDA.L": {"Nome": "iShares Core MSCI World", "Tipo": "CORE"},
    "ISAC.L": {"Nome": "iShares MSCI ACWI", "Tipo": "CORE"},
    "CSPX.L": {"Nome": "iShares Core S&P 500", "Tipo": "CORE"},
    "VUSA.L": {"Nome": "Vanguard S&P 500", "Tipo": "CORE"},
    "CNDX.L": {"Nome": "iShares NASDAQ 100", "Tipo": "CORE"},
    "EIMI.L": {"Nome": "iShares Core MSCI EM IMI", "Tipo": "CORE"},
    "MEUD.PA": {"Nome": "Amundi STOXX Europe 600", "Tipo": "CORE"},
    "IMEU.L": {"Nome": "iShares Core MSCI Europe", "Tipo": "CORE"},
    "WDEF.L": {"Nome": "WisdomTree Europe Defence", "Tipo": "SAT"},
    "VUG": {"Nome": "Vanguard Growth (USA)", "Tipo": "SAT"},
    "VAPU.L": {"Nome": "Vanguard FTSE Asia Pacific", "Tipo": "SAT"},
    "ITA": {"Nome": "iShares US Aerospace & Defense", "Tipo": "SAT"},
    "VTV": {"Nome": "Vanguard Value (USA)", "Tipo": "CORE"},
    "FEZ": {"Nome": "SPDR Euro STOXX 50 (Top 50)", "Tipo": "SAT"},
    "VGK": {"Nome": "Vanguard FTSE Europe", "Tipo": "CORE"},
    "IJPA.L": {"Nome": "iShares MSCI Japan", "Tipo": "CORE"},
    "EWJ": {"Nome": "iShares MSCI Japan ETF (USA)", "Tipo": "CORE"},
    "DXJA.L": {"Nome": "WisdomTree Japan Equity Hedged", "Tipo": "SAT"},
    "INDA": {"Nome": "iShares MSCI India", "Tipo": "SAT"},
    "EWT": {"Nome": "iShares MSCI Taiwan", "Tipo": "SAT"},
    "RBOT.L": {"Nome": "iShares Automation & Robotics", "Tipo": "SAT"},
    "VWO": {"Nome": "Vanguard FTSE Emerging Markets", "Tipo": "SAT"},
    "EWQ": {"Nome": "iShares MSCI France", "Tipo": "SAT"},
    "EWI": {"Nome": "iShares MSCI Italy", "Tipo": "SAT"},
    "EWG": {"Nome": "iShares MSCI Germany", "Tipo": "SAT"},
    "XLK": {"Nome": "Technology Select Sector SPDR", "Tipo": "SAT"},
    "XLKS.L": {"Nome": "Invesco Technology S&P US", "Tipo": "SAT"},
    "SOXX": {"Nome": "iShares Semiconductor", "Tipo": "SAT"},
    "SMH": {"Nome": "VanEck Semiconductor", "Tipo": "SAT"},
    "SKYY": {"Nome": "First Trust Cloud Computing", "Tipo": "SAT"},
    "VOX": {"Nome": "Communication Services SPDR", "Tipo": "SAT"},
    "QQQJ": {"Nome": "Invesco NASDAQ Next Gen 100", "Tipo": "SAT"},
    "QQQ": {"Nome": "Invesco QQQ Trust (Nasdaq 100)", "Tipo": "SAT"},
    "TQQQ": {"Nome": "ProShares UltraPro QQQ (Leva 3x)", "Tipo": "SAT"},
    "WTAI.L": {"Nome": "Amundi MSCI Digital Economy", "Tipo": "SAT"},
    "CYBR.L": {"Nome": "iShares Digital Security", "Tipo": "SAT"},
    "WQTM": {"Nome": "World Quality Momentum", "Tipo": "SAT"},
    "XLF": {"Nome": "Financial Select Sector SPDR", "Tipo": "SAT"},
    "BNKE.PA": {"Nome": "Lyxor MSCI Europe Banks", "Tipo": "SAT"},
    "BLOK": {"Nome": "Amplify Data Sharing & Blockchain", "Tipo": "SAT"},
    "XLE": {"Nome": "Energy Select Sector SPDR", "Tipo": "SAT"},
    "USO": {"Nome": "United States Oil Fund (Petrolio)", "Tipo": "SAT"},
    "XLI": {"Nome": "Industrial Select Sector SPDR", "Tipo": "SAT"},
    "XLB": {"Nome": "Materials Select Sector SPDR", "Tipo": "SAT"},
    "XLU": {"Nome": "Utilities Select Sector SPDR", "Tipo": "SAT"},
    "XLV": {"Nome": "Health Care Select Sector SPDR", "Tipo": "SAT"},
    "XLC": {"Nome": "Communication Services SPDR", "Tipo": "SAT"},
    "XLY": {"Nome": "Consumer Discretionary SPDR", "Tipo": "SAT"},
    "XLP": {"Nome": "Consumer Staples SPDR", "Tipo": "SAT"},
    "ICLN": {"Nome": "iShares Global Clean Energy", "Tipo": "SAT"},
    "FXI": {"Nome": "iShares China Large-Cap", "Tipo": "SAT"},
    "GLD": {"Nome": "SPDR Gold Shares (Oro)", "Tipo": "SAT"},
    "SLV": {"Nome": "iShares Silver Trust (Argento)", "Tipo": "SAT"},
    "PPLT": {"Nome": "Aberdeen Physical Platinum", "Tipo": "SAT"},
    "COPA": {"Nome": "iShares Morningstar Global Copper", "Tipo": "SAT"},
    "CPER": {"Nome": "United States Copper Index", "Tipo": "SAT"},
    "PALL": {"Nome": "Aberdeen Physical Palladium", "Tipo": "SAT"},
    "GOLD": {"Nome": "Barrick Gold Corp (Azionario)", "Tipo": "SAT"},
    "URA": {"Nome": "Global X Uranium ETF", "Tipo": "SAT"},
    "VXX": {"Nome": "iPath S&P 500 VIX Short-Term", "Tipo": "SAT"}
}

@st.cache_data(ttl=300)
def scarica_benchmarks_sicuri():
    benchmarks = {}
    for b in ["SPY", "GLD", "UUP"]:
        try:
            obj = yf.Ticker(b)
            hist = obj.history(period="1y")
            if not hist.empty and 'Close' in hist.columns:
                s = hist['Close']
                if s.index.tz is not None: s = s.tz_localize(None)
                benchmarks[b] = s.dropna()
        except: pass
    return benchmarks

def calcola_ritorno_sicuro(series, days):
    try:
        if series is None or series.empty: return 0
        p_now = series.iloc[-1]
        target_date = series.index[-1] - pd.Timedelta(days=days)
        idx = series.index.get_indexer([target_date], method='nearest')[0]
        p_past = series.iloc[idx]
        return (p_now / p_past) - 1 if p_past != 0 else 0
    except: return 0

@st.cache_data(ttl=300)
def elabora_radar(tickers, benchmarks):
    data_list = []
    spy_s, gld_s, uup_s = benchmarks.get("SPY"), benchmarks.get("GLD"), benchmarks.get("UUP")
    spy_7, spy_30, spy_90 = calcola_ritorno_sicuro(spy_s, 7), calcola_ritorno_sicuro(spy_s, 30), calcola_ritorno_sicuro(spy_s, 90)
    gld_7, gld_30, gld_90 = calcola_ritorno_sicuro(gld_s, 7), calcola_ritorno_sicuro(gld_s, 30), calcola_ritorno_sicuro(gld_s, 90)
    uup_7, uup_30, uup_90 = calcola_ritorno_sicuro(uup_s, 7), calcola_ritorno_sicuro(uup_s, 30), calcola_ritorno_sicuro(uup_s, 90)
    
    ora_it = pd.Timestamp.now(tz='Europe/Rome')
    giorno_settimana = ora_it.dayofweek
    ora_decimale = ora_it.hour + ora_it.minute / 60.0
    
    for ticker_yahoo, info in tickers.items():
        try:
            t_obj = yf.Ticker(ticker_yahoo)
            hist = t_obj.history(period="1y")
            if hist.empty or len(hist) < 200: continue
            
            close_s = hist['Close']
            if close_s.index.tz is not None: close_s = close_s.tz_localize(None)
            close_s = close_s.dropna()
            
            prezzo_attuale = close_s.iloc[-1]
            prezzo_ieri = close_s.iloc[-2]
            var_giornaliera = (prezzo_attuale - prezzo_ieri) / prezzo_ieri
            
            sma200 = close_s.rolling(window=200).mean().iloc[-1]
            sma20 = close_s.rolling(window=20).mean().iloc[-1]
            std20 = close_s.rolling(window=20).std().iloc[-1]
            if std20 == 0: continue
            
            bollinger_sup = sma20 + (2 * std20)
            bollinger_inf = sma20 - (2 * std20)
            percent_b = (prezzo_attuale - bollinger_inf) / (bollinger_sup - bollinger_inf)
            trend = "🐂 BULL" if prezzo_attuale > sma200 else "🐻 BEAR"
            
            if giorno_settimana >= 5:
                stato_mercato = "🔴 CHIUSO"
            else:
                if any(ticker_yahoo.endswith(ext) for ext in [".L", ".PA", ".AS"]):
                    stato_mercato = "🟢 APERTO" if 9.0 <= ora_decimale <= 17.5 else "🔴 CHIUSO"
                else:
                    stato_mercato = "🟢 APERTO" if 15.5 <= ora_decimale <= 22.0 else "🔴 CHIUSO"
            
            etf_7, etf_30, etf_90 = calcola_ritorno_sicuro(close_s, 7), calcola_ritorno_sicuro(close_s, 30), calcola_ritorno_sicuro(close_s, 90)
            qualita = 0.0
            if etf_7 > spy_7: qualita += 0.15
            if etf_30 > spy_30: qualita += 0.25
            if etf_90 > spy_90: qualita += 0.30
            if etf_7 > gld_7: qualita += 0.025
            if etf_30 > gld_30: qualita += 0.050
            if etf_90 > gld_90: qualita += 0.075
            if etf_7 > uup_7: qualita += 0.025
            if etf_30 > uup_30: qualita += 0.050
            if etf_90 > uup_90: qualita += 0.075
            
            data_list.append({
                "Ticker": ticker_yahoo,
                "Nome": info["Nome"],
                "Tipo": info["Tipo"],
                "Qualità ⭐": round(qualita, 3),
                "Prezzo ($)": round(prezzo_attuale, 2),
                "Var. Giornaliera": var_giornaliera,
                "Stato Mercato": stato_mercato,
                "MMA 20": round(sma20, 2),
                "%B": round(percent_b, 2),
                "Trend 200": trend
            })
        except: pass
    return pd.DataFrame(data_list)

benchmarks = scarica_benchmarks_sicuri()
df = elabora_radar(TICKERS_CONFIG, benchmarks)

def calcola_super_filtro(row):
    c2, q2, u2, m2, g2 = row['Tipo'], row['%B'], row['Trend 200'], row['MMA 20'], row['Qualità ⭐']
    if c2 == "CORE":
        if q2 < 0.45 and u2 == "🐂 BULL" and m2 > 40: return "🚀 VAI! (Pullback CORE)"
        elif q2 < 0.55 and m2 > 40: return "🤔 VALUTA (Osserva CORE)"
        else: return "❌ STAI FERMO"
    else:
        if g2 >= 0.75:
            if q2 >= 0.55 and q2 <= 1 and u2 == "🐂 BULL" and m2 > 50: return "🚀 VAI! (Trend SAT)"
            elif q2 >= 0.45 and m2 > 45: return "🤔 VALUTA (Osserva Trend)"
            elif q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35: return "🚀 VAI! (PULLBACK PREMIUM)"
            elif q2 < 0.35 and m2 > 35: return "🤔 VALUTA (Osserva Pullback Premium)"
            else: return "❌ STAI FERMO"
        else:
            if q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35: return "🚀 VAI! (Pullback SAT)"
            elif q2 < 0.35 and m2 > 35: return "🤔 VALUTA (Osserva Pullback)"
            else: return "❌ STAI FERMO"

# --- STYLE FUNCTIONS ---
def color_var_text(val):
    if val > 0: return 'color: #2e7d32; font-weight: bold;'
    elif val < 0: return 'color: #c62828; font-weight: bold;'
    return ''

def colora_stato_soft(val):
    if "APERTO" in str(val): return 'background-color: #e8f5e9; color: #1b5e20; font-weight: bold;'
    elif "CHIUSO" in str(val): return 'background-color: #ffebee; color: #c62828;'
    return ''

def colora_segnali_soft(val):
    val_str = str(val)
    if "🚀 VAI!" in val_str:
        if "Pullback" in val_str or "PULLBACK" in val_str: return 'background-color: #1b5e20; color: white; font-weight: bold;'
        elif "Trend" in val_str: return 'background-color: #c8e6c9; color: #1b5e20; font-weight: bold;'
    elif "🤔 VALUTA" in val_str: return 'background-color: #fff9c4; color: #f57f17;'
    elif "❌ STAI FERMO" in val_str: return 'background-color: #ffcdd2; color: #b71c1c;'
    return ''

def assegna_priorita(val):
    val_str = str(val)
    if "🚀 VAI!" in val_str:
        if "Pullback" in val_str or "PULLBACK" in val_str: return 1
        elif "Trend" in val_str: return 2
    elif "🤔 VALUTA" in val_str: return 3
    return 4

if not df.empty:
    df['IL SUPER-FILTRO'] = df.apply(calcola_super_filtro, axis=1)
    df['_rank'] = df['IL SUPER-FILTRO'].apply(assegna_priorita)
    df = df.sort_values(by=["_rank", "Qualità ⭐"], ascending=[True, False]).drop(columns=['_rank'])
    
    df_visualizzazione = df[["Ticker", "Nome", "Tipo", "Qualità ⭐", "Prezzo ($)", "Var. Giornaliera", "Stato Mercato", "Trend 200", "%B", "IL SUPER-FILTRO"]]
    
    # AGGIUNTO IL COMANDO HIDE_INDEX=TRUE PER UN LOOK PROFESSIONALE
    st.dataframe(
        df_visualizzazione.style.format({"Qualità ⭐": "{:.0%}", "Var. Giornaliera": "{:+.2%}"})
                                .map(color_var_text, subset=['Var. Giornaliera'])
                                .map(colora_stato_soft, subset=['Stato Mercato'])
                                .map(colora_segnali_soft, subset=['IL SUPER-FILTRO'])
                                .set_properties(**{'text-align': 'center'}),
        use_container_width=True,
        height=800,
        hide_index=True
    )
else:
    st.warning("Caricamento in corso dei dati di mercato...")
