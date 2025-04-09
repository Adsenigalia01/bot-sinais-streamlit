import yfinance as yf
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import streamlit as st

st.set_page_config(page_title="Bot de Sinais Simplificado", layout="wide")
st.title("📈 Bot de Sinais Simplificado")

ativo = st.text_input("Digite o código do ativo (ex: PETR4.SA ou BTC-USD):", "BTC-USD")
periodo = st.selectbox("Período:", ["3mo", "6mo", "1y"], index=0)

if st.button("🔍 Analisar"):
    try:
        df = yf.download(ativo, period=periodo, interval="1d")

        if df.empty or 'Close' not in df.columns:
            st.error("❌ Dados indisponíveis para o ativo.")
        else:
            # Calcula os indicadores
            df['SMA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
            df['SMA200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
            df['RSI'] = RSIIndicator(close=df['Close']).rsi()
            df['MACD'] = MACD(close=df['Close']).macd_diff()
            df['Bollinger_low'] = BollingerBands(close=df['Close']).bollinger_lband()
            df['Bollinger_high'] = BollingerBands(close=df['Close']).bollinger_hband()
            df['ADX'] = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close']).adx()

            # Remove linhas com valores faltando (causam erro fora do horário de mercado)
            df.dropna(subset=[
                'Close', 'High', 'Low', 'Open',
                'SMA50', 'SMA200', 'RSI',
                'MACD', 'Bollinger_low', 'Bollinger_high', 'ADX'
            ], inplace=True)

            if df.empty:
                st.error("❌ Dados insuficientes após cálculo dos indicadores.")
            else:
                # Seleciona a última linha com todos os dados
