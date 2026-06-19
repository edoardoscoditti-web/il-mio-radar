import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# Configurazione Pagina
st.set_page_config(page_title="Quant Terminal", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 🗂️ DATABASE TITOLI COMPLETO (Sincronizzato eToro + Nuovi ETF Xetra)
# ==============================================================================
TICKERS_CONFIG = {
    # --- CORE ORIGINARI ---
    "SWDA.L": {"Nome": "iShares Core MSCI World", "Tipo": "CORE"},
    "ISAC.L": {"Nome": "iShares MSCI ACWI", "Tipo": "CORE"},
    "CSPX.L": {"Nome": "iShares Core S&P 500", "Tipo": "CORE"},
    "VUSA.L": {"Nome": "Vanguard S&P 500", "Tipo": "CORE"},
    "CNDX.L": {"Nome": "iShares NASDAQ 100", "Tipo": "CORE"},
    "EIMI.L": {"Nome": "iShares Core MSCI EM IMI", "Tipo": "CORE"},
    "MEUD.PA": {"Nome": "Amundi STOXX Europe 600", "Tipo": "CORE"},
    "IMEU.L": {"Nome": "iShares Core MSCI Europe", "Tipo": "CORE"},
    "VTV": {"Nome": "Vanguard Value (USA)", "Tipo": "CORE"},
    "VGK": {"Nome": "Vanguard FTSE Europe", "Tipo": "CORE"},
    "IJPA.L": {"Nome": "iShares MSCI Japan", "Tipo": "CORE"},
    "EWJ": {"Nome": "iShares MSCI Japan ETF (USA)", "Tipo": "CORE"},
    
    # --- NUOVI TITOLI TEDESCHI BORSA XETRA (.DE) ---
    "ESPO.DE": {"Nome": "VanEck Video Gaming & Esports UCITS", "Tipo": "SAT"},
    "IUSN.DE": {"Nome": "iShares MSCI World Small Cap UCITS", "Tipo": "CORE"},
    "IS3N.DE": {"Nome": "iShares Core MSCI EM IMI UCITS", "Tipo": "CORE"},
    "IS3Q.DE": {"Nome": "iShares MSCI World Quality Factor", "Tipo": "SAT"},
    "IS3S.DE": {"Nome": "iShares MSCI World Value Factor", "Tipo": "SAT"},
    "HDX1.DE": {"Nome": "L&G DAX Daily 2x Long UCITS (Leva)", "Tipo": "SAT"},

    # --- SATELLITI ORIGINARI ---
    "WDEF.L": {"Nome": "WisdomTree Europe Defence", "Tipo": "SAT"},
    "VUG": {"Nome": "Vanguard Growth (USA)", "Tipo": "SAT"},
    "VAPU.L": {"Nome": "Vanguard FTSE Asia Pacific", "Tipo": "SAT"},
    "ITA": {"Nome": "iShares US Aerospace & Defense", "Tipo": "SAT"},
    "FEZ": {"Nome": "SPDR Euro STOXX 50 (Top 50)", "Tipo": "SAT"},
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
            hist = obj.history(period="1y", auto_adjust=False)
            if not hist.empty and 'Close' in hist.columns:
                s = hist['Close']
                if s.index.tz is not None: s = s.tz_localize(None)
                benchmarks[b] = s.dropna()
        except: pass
    return benchmarks

# --- MOTORE GEOMETRICO ORIGINARIO ---
def calcola_fr_geometrica(etf_series, bench_series, days_lookback):
    try:
        df_aligned = pd.concat([etf_series, bench_series], axis=1, join='inner').dropna()
        if df_aligned.empty: return 0
        etf_now = df_aligned.iloc[-1, 0]
        bench_now = df_aligned.iloc[-1, 1]
        endpoint_date = df_aligned.index[-1].normalize()
        target_date = endpoint_date - pd.Timedelta(days=days_lookback)
        idx_past = df_aligned.index.get_indexer([target_date], method='nearest')[0]
        etf_past = df_aligned.iloc[idx_past, 0]
        bench_past = df_aligned.iloc[idx_past, 1]
        if etf_past == 0 or bench_past == 0 or bench_now == 0: return 0
        return ((etf_now / bench_now) / (etf_past / bench_past)) - 1
    except:
        return 0

@st.cache_data(ttl=300)
def elabora_radar(tickers, benchmarks):
    data_list = []
    
    # === SOLUZIONE OROLOGIO E STATO MERCATI ===
    # Forziamo l'estrazione dell'ora esatta di Roma (Italia)
    ora_it = pd.Timestamp.utcnow().tz_convert('Europe/Rome')
    giorno_settimana = ora_it.dayofweek # 0=Lunedì, 6=Domenica
    ora_decimale = ora_it.hour + (ora_it.minute / 60.0)
    
    spy_clean = benchmarks.get("SPY", pd.Series())
    gld_clean = benchmarks.get("GLD", pd.Series())
    uup_clean = benchmarks.get("UUP", pd.Series())
    
    for ticker_yahoo, info in tickers.items():
        try:
            t_obj = yf.Ticker(ticker_yahoo)
            hist = t_obj.history(period="1y", auto_adjust=False)
            if hist.empty or len(hist) < 200: continue
            
            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)
            
            close_series = hist['Close'].dropna()
            high_series = hist['High']
            low_series = hist['Low']
            prezzo_attuale = close_series.iloc[-1]
            prezzo_ieri = close_series.iloc[-2]
            var_giornaliera = (prezzo_attuale - prezzo_ieri) / prezzo_ieri
            
            # --- CALCOLO NUOVI SETUP OPERATIVI ---
            ema12 = close_series.ewm(span=12, adjust=False).mean()
            ema26 = close_series.ewm(span=26, adjust=False).mean()
            macd_line = ema12 - ema26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            macd_cross_up = macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]
            
            low14 = low_series.rolling(window=14).min()
            high14 = high_series.rolling(window=14).max()
            stoch_k = 100 * (close_series - low14) / (high14 - low14 + 1e-9)
            stoch_k_smoothed = stoch_k.rolling(window=3).mean()
            stoch_d = stoch_k_smoothed.rolling(window=3).mean()
            stoch_cross_up = stoch_k_smoothed.iloc[-1] > stoch_d.iloc[-1] and stoch_k_smoothed.iloc[-2] <= stoch_d.iloc[-2]
            
            delta = close_series.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(com=13, adjust=False).mean()
            avg_loss = loss.ewm(com=13, adjust=False).mean()
            rs = avg_gain / (avg_loss + 1e-9)
            rsi_attuale = (100 - (100 / (1 + rs))).iloc[-1]
            
            if (macd_cross_up or stoch_cross_up) and rsi_attuale < 38:
                setup_operativo = "🚀 INGRESSO"
            elif macd_line.iloc[-1] > signal_line.iloc[-1] and stoch_k_smoothed.iloc[-1] > stoch_d.iloc[-1] and rsi_attuale < 50:
                setup_operativo = "Mantenere"
            else:
                setup_operativo = "Monitoraggio"
                
            ema9 = close_series.ewm(span=9, adjust=False).mean()
            ema21 = close_series.ewm(span=21, adjust=False).mean()
            if ema9.iloc[-1] > ema21.iloc[-1] and ema9.iloc[-2] <= ema21.iloc[-2]:
                trend_anticipato = "⚡ ACCELERAZIONE"
            else:
                trend_anticipato = "Rialzista" if ema9.iloc[-1] > ema21.iloc[-1] else "Ribassista"

            # --- VECCHI INDICATORI TECNICI ORIGINARI ---
            sma20 = close_series.rolling(window=20).mean().iloc[-1]
            std20 = close_series.rolling(window=20).std().iloc[-1]
            if std20 == 0: continue
            bollinger_sup = sma20 + (2 * std20)
            bollinger_inf = sma20 - (2 * std20)
            percent_b = (prezzo_attuale - bollinger_inf) / (bollinger_sup - bollinger_inf)
            alert_bande = "💥 TOCCO SUP" if prezzo_attuale >= bollinger_sup else ("💥 TOCCO INF" if prezzo_attuale <= bollinger_inf else "In range")
            close_30 = close_series.tail(30)
            rsi_semplificato = 50 + (10 * (prezzo_attuale - close_30.mean()) / close_30.std()) if close_30.std() > 0 else 50
            bandwidth = (bollinger_sup - bollinger_inf) / sma20
            prev_close = close_series.shift(1)
            tr = pd.concat([hist['High'] - hist['Low'], (hist['High'] - prev_close).abs(), (hist['Low'] - prev_close).abs()], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            vol_check = "✅ VOLUME ALTO" if hist['Volume'].iloc[-1] > hist['Volume'].tail(30).mean() else "⚠️ VOL. BASSO"
            trend_7g_list = close_series.tail(7).tolist()
            trend_30g_list = close_series.tail(30).tolist()
            sma200 = close_series.rolling(window=200).mean().iloc[-1]
            trend_200 = "🐂 BULL" if prezzo_attuale > sma200 else "🐻 BEAR"
            
            # --- ASSEGNAZIONE STATO MERCATO (OROLOGIO ITALIANO) ---
            if giorno_settimana >= 5: 
                stato_mercato = "🔴 CHIUSO"
            else:
                # Titoli Europei (Borse Xetra, Londra, Parigi, Amsterdam)
                if any(ticker_yahoo.endswith(ext) for ext in [".L", ".PA", ".AS", ".DE", ".MI"]):
                    stato_mercato = "🟢 APERTO" if 9.0 <= ora_decimale <= 17.5 else "🔴 CHIUSO"
                # Titoli Americani (NYSE, NASDAQ)
                else: 
                    stato_mercato = "🟢 APERTO" if 15.5 <= ora_decimale <= 22.0 else "🔴 CHIUSO"
            
            fr_spy_7  = calcola_fr_geometrica(close_series, spy_clean, 7)
            fr_spy_30 = calcola_fr_geometrica(close_series, spy_clean, 30)
            fr_spy_90 = calcola_fr_geometrica(close_series, spy_clean, 90)
            fr_gld_7  = calcola_fr_geometrica(close_series, gld_clean, 7)
            fr_gld_30 = calcola_fr_geometrica(close_series, gld_clean, 30)
            fr_gld_90 = calcola_fr_geometrica(close_series, gld_clean, 90)
            fr_uup_7  = calcola_fr_geometrica(close_series, uup_clean, 7)
            fr_uup_30 = calcola_fr_geometrica(close_series, uup_clean, 30)
            fr_uup_90 = calcola_fr_geometrica(close_series, uup_clean, 90)
            
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
                "Ticker": ticker_yahoo, "Nome": info["Nome"], "Tipo": info["Tipo"], "IL SUPER-FILTRO": "", 
                "Setup Operativo": setup_operativo, "Trend Anticipato ⚡": trend_anticipato,
                "Qualità ⭐": round(qualita, 3), "Prezzo": round(prezzo_attuale, 2), "Var. Giornaliera": var_giornaliera, "Stato Mercato": stato_mercato,
                "ALERT BANDE": alert_bande, "Trend 7G": trend_7g_list, "Trend 30G": trend_30g_list, "Trend 200": trend_200, "VOLUME CHECK": vol_check, "Bandwidth": bandwidth, "ATR": round(atr, 2),
                "FR vs SPY 7g": fr_spy_7, "FR vs SPY 30g": fr_spy_30, "FR vs SPY 90g": fr_spy_90,
                "FR vs ORO 7g": fr_gld_7, "FR vs ORO 30g": fr_gld_30, "FR vs ORO 90g": fr_gld_90,
                "FR vs USD 7g": fr_uup_7, "FR vs USD 30g": fr_uup_30, "FR vs USD 90g": fr_uup_90,
                "RSI Semplificato": round(rsi_semplificato, 1), "%B": round(percent_b, 2), "MMA 20": round(sma20, 2)
            })
        except: pass
    return pd.DataFrame(data_list)

benchmarks = scarica_benchmarks_sicuri()
df = elabora_radar(TICKERS_CONFIG, benchmarks)

def calcola_super_filtro(row):
    c2, q2, u2, m2, g2 = row['Tipo'], row['%B'], row['Trend 200'], row['RSI Semplificato'], row['Qualità ⭐']
    if c2 == "CORE":
        if q2 < 0.45 and u2 == "🐂 BULL" and m2 > 40: return "🚀 VAI! (Pullback CORE)"
        elif q2 < 0.55 and m2 > 40: return "🤔 VALUTA (Osserva CORE)"
        else: return "❌ STAI FERMO"
    else:
        if g2 >= 0.75:
            if q2 >= 0.55 and q2 <= 1.0 and u2 == "🐂 BULL" and m2 > 50: return "🚀 VAI! (Trend SAT)"
            elif q2 >= 0.45 and m2 > 45: return "🤔 VALUTA (Osserva Trend)"
            elif q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35: return "🚀 VAI! (PULLBACK PREMIUM)"
            elif q2 < 0.35 and m2 > 35: return "🤔 VALUTA (Osserva Pullback Premium)"
            else: return "❌ STAI FERMO"
        else:
            if q2 < 0.25 and u2 == "🐂 BULL" and m2 > 35: return "🚀 VAI! (Pullback SAT)"
            elif q2 < 0.35 and m2 > 35: return "🤔 VALUTA (Osserva Pullback)"
            else: return "❌ STAI FERMO"

def color_text_red_green(val):
    if isinstance(val, str):
        if "ACCELERAZIONE" in val or "Rialzista" in val: return 'color: #2e7d32; font-weight: bold;'
        elif "Ribassista" in val: return 'color: #c62828; font-weight: bold;'
        return ''
    try:
        if val > 0: return 'color: #2e7d32; font-weight: bold;'
        elif val < 0: return 'color: #c62828; font-weight: bold;'
    except: pass
    return ''

def colora_setup_operativo(val):
    if "INGRESSO" in str(val): return 'background-color: #1b5e20; color: white; font-weight: bold;'
    elif "Mantenere" in str(val): return 'background-color: #e8f5e9; color: #1b5e20;'
    return 'color: #757575;'

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
    
    # --- RIGA KPI PREMIUM (GRANDI E PULITI) ---
    titoli_analizzati = len(df)
    setup_attivi = len(df[df['Setup Operativo'] == "🚀 INGRESSO"])
    super_filtro_on = len(df[df['IL SUPER-FILTRO'].str.contains("VAI!", na=False)])
    mercati_aperti = len(df[df['Stato Mercato'].str.contains("APERTO", na=False)])
    
    st.markdown(f"""
        <div style="display: flex; justify-content: space-around; background-color: #f8f9fa; padding: 22px; border-radius: 12px; margin-top: 15px; margin-bottom: 25px; border: 1px solid #e2e8f0; font-family: 'Segoe UI', system-ui, sans-serif;">
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 1.15rem; color: #4A5568; font-weight: 600; letter-spacing: 0.5px;">📊 TITOLI SCANSIONATI</p>
                <p style="margin: 5px 0 0 0; font-size: 2.8rem; font-weight: 800; color: #1A365D; line-height: 1;">{titoli_analizzati}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 1.15rem; color: #4A5568; font-weight: 600; letter-spacing: 0.5px;">🎯 SEGNALI ATTIVI</p>
                <p style="margin: 5px 0 0 0; font-size: 2.8rem; font-weight: 800; color: #2E7D32; line-height: 1;">{super_filtro_on}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 1.15rem; color: #4A5568; font-weight: 600; letter-spacing: 0.5px;">🚀 SETUP INGRESSO</p>
                <p style="margin: 5px 0 0 0; font-size: 2.8rem; font-weight: 800; color: #E65100; line-height: 1;">{setup_attivi}</p>
            </div>
            <div style="text-align: center;">
                <p style="margin: 0; font-size: 1.15rem; color: #4A5568; font-weight: 600; letter-spacing: 0.5px;">🟢 MERCATI APERTI</p>
                <p style="margin: 5px 0 0 0; font-size: 2.8rem; font-weight: 800; color: #2E7D32; line-height: 1;">{mercati_aperti}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    colonne_finali = [
        "Ticker", "Nome", "Tipo", "IL SUPER-FILTRO", "Setup Operativo", "Trend Anticipato ⚡", "Qualità ⭐", "Prezzo", "Var. Giornaliera", "Stato Mercato",
        "ALERT BANDE", "Trend 7G", "Trend 30G", "Trend 200", "VOLUME CHECK", "Bandwidth", "ATR",
        "FR vs SPY 7g", "FR vs SPY 30g", "FR vs SPY 90g",
        "FR vs ORO 7g", "FR vs ORO 30g", "FR vs ORO 90g",
        "FR vs USD 7g", "FR vs USD 30g", "FR vs USD 90g",
        "RSI Semplificato", "%B", "MMA 20"
    ]
    
    df_visualizzazione = df[colonne_finali]
    formati_percentuali = {"Qualità ⭐": "{:.0%}", "Var. Giornaliera": "{:+.2%}", "Bandwidth": "{:.1%}"}
    for col in colonne_finali:
        if "FR vs" in col: formati_percentuali[col] = "{:+.2%}"
        
    st.dataframe(
        df_visualizzazione.style.format(formati_percentuali)
                                .map(color_text_red_green, subset=['Var. Giornaliera', 'FR vs SPY 7g', 'FR vs SPY 30g', 'FR vs SPY 90g', 'FR vs ORO 7g', 'FR vs ORO 30g', 'FR vs ORO 90g', 'FR vs USD 7g', 'FR vs USD 30g', 'FR vs USD 90g', 'Trend Anticipato ⚡'])
                                .map(colora_stato_soft, subset=['Stato Mercato'])
                                .map(colora_alert_bande, subset=['ALERT BANDE'])
                                .map(colora_volumi, subset=['VOLUME CHECK'])
                                .map(colora_setup_operativo, subset=['Setup Operativo'])
                                .map(colora_segnali_soft, subset=['IL SUPER-FILTRO'])
                                .set_properties(**{'text-align': 'center'}),
        column_config={
            "Trend 7G": st.column_config.LineChartColumn("Trend 7G", width="small"),
            "Trend 30G": st.column_config.LineChartColumn("Trend 30G", width="small"),
        },
        use_container_width=True, height=650, hide_index=True
    )
else:
    st.warning("Caricamento del terminale quantitativo in corso...")
