import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Bot de Sinais", layout="wide")
st.title("📈 Bot de Sinais - Ações e Criptomoedas")

# Entrada do usuário
ativo = st.text_input("Digite o código do ativo (ex: PETR4.SA ou BTC-USD):", "PETR4.SA")
periodo = st.selectbox("Período de análise:", ["3mo", "6mo", "1y"], index=1)

if st.button("🔍 Analisar"):
    try:
        df = yf.download(ativo, period=periodo, interval="1d")

        if df.empty or 'Close' not in df.columns:
            st.error("❌ Ativo não encontrado ou sem dados disponíveis.")
        else:
            df.dropna(inplace=True)

            # Indicadores técnicos com conversão para Series
            df['SMA50'] = pd.Series(SMAIndicator(close=df['Close'], window=50).sma_indicator(), index=df.index)
            df['SMA200'] = pd.Series(SMAIndicator(close=df['Close'], window=200).sma_indicator(), index=df.index)
            df['RSI'] = pd.Series(RSIIndicator(close=df['Close']).rsi(), index=df.index)
            df['MACD'] = pd.Series(MACD(close=df['Close']).macd_diff(), index=df.index)
            bb = BollingerBands(close=df['Close'])
            df['Bollinger_high'] = pd.Series(bb.bollinger_hband(), index=df.index)
            df['Bollinger_low'] = pd.Series(bb.bollinger_lband(), index=df.index)
            df['ADX'] = pd.Series(ADXIndicator(high=df['High'], low=df['Low'], close=df['Close']).adx(), index=df.index)

            # Estratégia de sinais
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

    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
