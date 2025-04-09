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
            close = df['Close']
            high = df['High']
            low = df['Low']

            df['SMA50'] = pd.Series(SMAIndicator(close=close, window=50).sma_indicator())
            df['SMA200'] = pd.Series(SMAIndicator(close=close, window=200).sma_indicator())
            df['RSI'] = pd.Series(RSIIndicator(close=close).rsi())
            df['MACD'] = pd.Series(MACD(close=close).macd_diff())
            df['Bollinger_low'] = pd.Series(BollingerBands(close=close).bollinger_lband())
            df['Bollinger_high'] = pd.Series(BollingerBands(close=close).bollinger_hband())
            df['ADX'] = pd.Series(ADXIndicator(high=high, low=low, close=close).adx())

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

                st.subheader(f"📊 Resultado da Análise para {ativo}")
                st.write(f"**Data da análise:** {df.index[-1].date()}")
                st.success(f"**Classificação:** {sinal}")

                with st.expander("📉 Ver últimos dados"):
                    st.dataframe(df.tail(5))

    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
