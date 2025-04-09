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
            df.dropna(inplace=True)

            # Indicadores técnicos (forçando todos como Series 1D)
            df['SMA50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
            df['SMA200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
            df['RSI'] = RSIIndicator(close=df['Close']).rsi()
            df['MACD'] = MACD(close=df['Close']).macd_diff()
            df['Bollinger_low'] = BollingerBands(close=df['Close']).bollinger_lband()
            df['Bollinger_high'] = BollingerBands(close=df['Close']).bollinger_hband()
            df['ADX'] = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close']).adx()

            df.dropna(inplace=True)
            ultimo = df.iloc[-1]

            # Cálculo de pontuação para classificação
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

            # Classificação simples
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

            st.subheader(f"📊 Resultado da Análise para {ativo}")
            st.write(f"**Data da análise:** {df.index[-1].date()}")
            st.success(f"**Classificação:** {sinal}")

            with st.expander("📉 Ver últimos dados"):
                st.dataframe(df.tail(5))

    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
