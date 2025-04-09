import streamlit as st
import pandas as pd
import numpy as np
from twelvedata import TDClient
from ta.trend import SMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

st.set_page_config(page_title="Bot de Sinais com Twelve Data", layout="wide")
st.title("📊 Bot de Sinais com API da Twelve Data")

api_key = st.secrets["TWELVE_DATA_API_KEY"] if "TWELVE_DATA_API_KEY" in st.secrets else st.text_input("1351656ba22446b98cd1964398849126", "")

ativo = st.text_input("Digite o código do ativo (ex: BTC/USD ou AAPL):", "BTC/USD")
periodo = st.selectbox("Período de análise:", ["30", "60", "90", "180"], index=0)

if st.button("🔍 Analisar") and api_key:
    try:
        td = TDClient(apikey=api_key)
        ts = td.time_series(
            symbol=ativo,
            interval="1day",
            outputsize=int(periodo),
            timezone="UTC"
        ).as_pandas()

        if ts is None or ts.empty:
            st.error("❌ Não foi possível buscar os dados.")
        else:
            ts.sort_index(inplace=True)
            df = ts.rename(columns={"close": "Close", "high": "High", "low": "Low", "open": "Open"})
            df['Close'] = df['Close'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)

            # Indicadores
            df['SMA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
            df['SMA200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
            df['RSI'] = RSIIndicator(close=df['Close']).rsi()
            df['MACD'] = MACD(close=df['Close']).macd_diff()
            df['Bollinger_low'] = BollingerBands(close=df['Close']).bollinger_lband()
            df['Bollinger_high'] = BollingerBands(close=df['Close']).bollinger_hband()
            df['ADX'] = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close']).adx()

            df.dropna(inplace=True)

            if df.empty:
                st.error("❌ Dados insuficientes após cálculo dos indicadores.")
            else:
                ultimo = df.iloc[-1]
                pontos = 0

                if ultimo['SMA50'] > ultimo['SMA200']:
                    pontos += 1
                if ultimo['RSI'] < 30:
                    pontos += 1
                if ultimo['MACD'] > 0:
                    pontos += 1
                if ultimo['Close'] < ultimo['Bollinger_low']:
                    pontos += 1
                if ultimo['ADX'] > 25:
                    pontos += 1

                if ultimo['MACD'] < 0 and ultimo['RSI'] > 70 and ultimo['Close'] > ultimo['Bollinger_high']:
                    sinal = "🔴 Alerta para venda"
                elif ultimo['SMA50'] < ultimo['SMA200'] and ultimo['RSI'] > 70:
                    sinal = "❌ Ótimo para venda"
                elif pontos == 5:
                    sinal = "🟢 Ótimo para compra"
                elif pontos >= 4:
                    sinal = "🟡 Alerta para compra"
                elif pontos == 3:
                    sinal = "🔁 Instável"
                else:
                    sinal = "⚪ Estável"

                st.subheader(f"📈 Resultado da análise para {ativo}")
                st.success(f"Classificação: **{sinal}**")
                st.write(f"📅 Última data: {df.index[-1].date()}")
                with st.expander("🔍 Últimos dados"):
                    st.dataframe(df.tail(5))

    except Exception as e:
        st.error(f"Erro: {e}")

