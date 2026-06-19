import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Terminale Quantitativo eToro", layout="wide")
st.title("📊 Il Mio Terminale Quantitativo Intermarket")
st.write("Sincronizzato eToro - Corretto bug fuso orario su ATR e Volumi.")

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
            
            # BLINDATURA: Rimuoviamo il fuso orario dall'intero DataFrame subito
            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)
            
            close_s = hist['Close'].dropna()
            volume_s = hist['Volume']
            high_s = hist['High']
            low_s = hist['Low']
            
            prezzo_attuale = close_s.iloc[-1]
            prezzo_ieri = close_s.iloc[-2]
            var_giornaliera = (prezzo_attuale - prezzo_ieri) / prezzo_ieri
            
            # --- BANDE DI BOLLINGER & ALERT ---
            sma20 = close_s.rolling(window=20).mean().iloc[-1]
            std20 = close_s.rolling(window=20).std().iloc[-1]
            if std20 == 0: continue
            bollinger_sup = sma20 + (2 * std20)
            bollinger_inf = sma20 - (2 * std20)
            percent_b = (prezzo_attuale - bollinger_inf) / (bollinger_sup - bollinger_inf)
            
            if prezzo_attuale >= bollinger_sup: alert_bande = "💥 TOCCO SUP"
            elif prezzo_attuale <= bollinger_inf: alert_bande = "💥 TOCCO INF"
            else: alert_bande = "In range"
            
            # --- VOLATILITÀ (BANDWIDTH & ATR) ---
            bandwidth = (bollinger_sup - bollinger_inf) / sma20
            prev_close = close_s.shift(1)
            tr = pd.concat([high_s - low_s, (high_s - prev_close).abs(), (low_s - prev_close).abs()], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            # --- VOLUME CHECK (SE VOLUME > VOLUMEAVG) ---
            vol_attuale = volume_s.iloc[-1]
            vol_avg30 = volume_s.tail(30).mean()
            if vol_attuale > vol_avg30:
                vol_check = "✅ VOLUME ALTO"
            else:
                vol_check = "⚠️ VOL. BASSO"
            
            # --- TREND 30 GIORNI (LISTA PER GRAFICO) ---
            trend_30g_list = close_s.tail(30).tolist()
            
            # --- STATO MERCATO ---
            sma200 = close_s.rolling(window=200).mean().iloc[-1]
            trend_200 = "🐂 BULL" if prezzo_attuale > sma200 else "🐻 BEAR"
            if giorno_settimana >= 5: stato_mercato = "🔴 CHIUSO"
            else:
                if any(ticker_yahoo.endswith(ext) for ext in [".L", ".PA", ".AS"]):
                    stato_mercato = "🟢 APERTO" if 9.0 <= ora_decimale <= 17.5 else "🔴 CHIUSO"
                else: stato_mercato = "🟢 APERTO" if 15.5 <= ora_decimale <= 22.0 else "🔴 CHIUSO"
            
            # --- FORZA RELATIVA DELTA % ---
            etf_7 = calcola_ritorno_sicuro(close_s, 7)
            etf_30 = calcola_ritorno_sicuro(close_s, 30)
            etf_90 = calcola_ritorno_sicuro(close_s, 90)
            
            fr_spy_7, fr_spy_30, fr_spy_90 = etf_7 - spy_7, etf_30 - spy_30, etf_90 - spy_90
            fr_gld_7, fr_gld_30, fr_gld_90 = etf_7 - gld_7, etf_30 - gld_30, etf_90 - gld_90
            fr_uup_7, fr_uup_30, fr_uup_90 = etf_7 - uup_7, etf_30 - uup_30, etf_90 - uup_90
            
            qualita = 0.0
            if fr_spy_7 > 0: qualita += 0.15
            if fr_spy_30 > 0: qualita += 0.25
            if fr_spy_90 > 0: qualita += 0.30
            if fr_gld_7 > 0: qualita += 0.025
            if fr_gld_30 > 0: qualita += 0.050
            if fr_gld_90 > 0: qualita += 0.075
            if fr_uup_7 > 0: qualita += 0.025
            if fr_uup_30 > 0: qualita += 0.050
            if fr_uup_90 > 0: qualita += 0.075
            
            data_list.append({
                "Ticker": ticker_yahoo,
                "Nome": info["Nome"],
                "Tipo": info["Tipo"],
                "Qualità ⭐": round(qualita, 3),
                "Prezzo ($)": round(prezzo_attuale, 2),
                "Var. Giornaliera": var_giornaliera,
                "Stato Mercato": stato_mercato,
                "ALERT BANDE": alert_bande,
                "Trend 30G": trend_30g_list,
                "VOLUME CHECK": vol_check,
                "Bandwidth": bandwidth,
                "ATR": round(atr, 2),
                "FR vs SPY 7g": fr_spy_7, "FR vs SPY 30g": fr_spy_30, "FR vs SPY 90g": fr_spy_90,
                "FR vs ORO 7g": fr_gld_7, "FR vs ORO 30g": fr_gld_30, "FR vs ORO 90g": fr_gld_90,
                "FR vs USD 7g": fr_uup_7, "FR vs USD 30g": fr_uup_30, "FR vs USD 90g": fr_uup_90,
                "Trend 200": trend_200, "%B": round(percent_b, 2), "MMA 20": round(sma20, 2)
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
def color_text_red_green(val):
    if val > 0: return 'color: #2e7d32; font-weight: bold;'
    elif val < 0: return 'color: #c62828; font-weight: bold;'
    return ''

def colora_stato_soft(val):
    if "APERTO" in str(val): return 'background-color: #e8f5e9; color: #1b5e20; font-weight: bold;'
    elif "CHIUSO" in str(val): return 'background-color: #ffebee; color: #c62828;'
    return ''

def colora_alert_bande(val):
    if "TOCCO" in str(val): return 'background-color: #ffe0b2; color: #e65100; font-weight: bold;'
    return 'color: #757575;'

def colora_volumi(val):
    if "ALTO" in str(val): return 'background-color: #e8f5e9; color: #1b5e20; font-weight: bold;'
    elif "BASSO" in str(val): return 'background-color: #f5f5f5; color: #9e9e9e;'
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
    
    colonne_finali = [
        "Ticker", "Nome", "Tipo", "Qualità ⭐", "Prezzo ($)", "Var. Giornaliera", "Stato Mercato",
        "ALERT BANDE", "Trend 30G", "VOLUME CHECK", "Bandwidth", "ATR",
        "FR vs SPY 7g", "FR vs SPY 30g", "FR vs SPY 90g",
        "FR vs ORO 7g", "FR vs ORO 30g", "FR vs ORO 90g",
        "FR vs USD 7g", "FR vs USD 30g", "FR vs USD 90g",
        "Trend 200", "%B", "IL SUPER-FILTRO"
    ]
    
    df_visualizzazione = df[colonne_finali]
    
    formati_percentuali = {"Qualità ⭐": "{:.0%}", "Var. Giornaliera": "{:+.2%}", "Bandwidth": "{:.1%}"}
    for col in colonne_finali:
        if "FR vs" in col: formati_percentuali[col] = "{:+.2%}"
        
    st.dataframe(
        df_visualizzazione.style.format(formati_percentuali)
                                .map(color_text_red_green, subset=['Var. Giornaliera', 'FR vs SPY 7g', 'FR vs SPY 30g', 'FR vs SPY 90g', 'FR vs ORO 7g', 'FR vs ORO 30g', 'FR vs ORO 90g', 'FR vs USD 7g', 'FR vs USD 30g', 'FR vs USD 90g'])
                                .map(colora_stato_soft, subset=['Stato Mercato'])
                                .map(colora_alert_bande, subset=['ALERT BANDE'])
                                .map(colora_volumi, subset=['VOLUME CHECK'])
                                .map(colora_segnali_soft, subset=['IL SUPER-FILTRO'])
                                .set_properties(**{'text-align': 'center'}),
        column_config={
            "Trend 30G": st.column_config.LineChartColumn("Trend 30G", width="medium"),
        },
        use_container_width=True,
        height=850,
        hide_index=True
    )
else:
    st.warning("Caricamento del tuo terminale quantitativo completo...")
