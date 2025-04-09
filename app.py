import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Bot de Sinais", layout="wide")
st.title("📈 Bot de Sinais - Ações e Criptomoedas")

# Entrada do usuário
ativo = st.text_input("Digite o código do ativo (ex: PETR4.SA ou BTC-USD):", "PETR4.SA")
periodo = st.selectbox("Período de análise:", ["3mo", "6mo", "1y"], index=1)

if st.button("🔍 Analisar"):
    df = yf.download(ativo, period=periodo, interval="1d")

    if df.empty:
        st.error("❌ Ativo não encontrado ou sem dados disponíveis.")
    else:
        df.dropna(inplace=True)

        # Indicadores técnicos
        df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd_diff()
        bollinger = ta.volatility.BollingerBands(df['Close'])
        df['Bollinger_high'] = bollinger.bollinger_hband()
        df['Bollinger_low'] = bollinger.bollinger_lband()
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'])
        df['ADX'] = adx.adx()

        # Estratégias e sinais
        def gerar_sinal(row):
            sinais = []
            if row['SMA50'] > row['SMA200']:
                sinais.append('Tendência de Alta')
            if row['RSI'] < 30:
                sinais.append('Sobrevendido')
            if row['MACD'] > 0:
                sinais.append('MACD positivo')
            if row['Close'] < row['Bollinger_low']:
                sinais.append('Preço abaixo da banda inferior')
            if row['ADX'] > 25:
                sinais.append('Tendência forte')
            return ', '.join(sinais)

        df['Sinais'] = df.apply(gerar_sinal, axis=1)
        sinal_hoje = df['Sinais'].iloc[-1]

        st.subheader(f"📊 Sinais mais recentes para {ativo}")
        st.write(f"**Data:** {df.index[-1].date()}  ")
        st.success(f"**Sinal de hoje:** {sinal_hoje if sinal_hoje else 'Sem sinal relevante'}")

        with st.expander("📉 Ver dados brutos"):
            st.dataframe(df.tail(10))

        with st.expander("📈 Gráficos"):
            st.line_chart(df[['Close', 'SMA50', 'SMA200']].dropna())