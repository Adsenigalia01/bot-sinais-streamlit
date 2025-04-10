import yfinance as yf
import pandas as pd
import ta
import streamlit as st

# Função para calcular os indicadores
def calculate_indicators(df):
    # Garantir que 'Close' seja uma série unidimensional
    if isinstance(df['Close'], pd.DataFrame):
        df['Close'] = df['Close'].squeeze()

    # Calculando os indicadores
    df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['MACD'] = ta.trend.macd_diff(df['Close'])
    df['Stochastic'] = ta.momentum.stochastic_oscillator(df['Close'], window=14)
    df['ADX'] = ta.trend.adx(df['Close'], window=14)

    return df

# Função para realizar a análise
def analyze(df):
    buy_signals = 0
    sell_signals = 0

    # Verificar os sinais de compra/venda com base nos indicadores
    if df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
        buy_signals += 1
    else:
        sell_signals += 1

    if df['RSI'].iloc[-1] < 30:
        buy_signals += 1
    elif df['RSI'].iloc[-1] > 70:
        sell_signals += 1

    if df['MACD'].iloc[-1] > 0:
        buy_signals += 1
    else:
        sell_signals += 1

    if df['Stochastic'].iloc[-1] > 20:
        buy_signals += 1
    elif df['Stochastic'].iloc[-1] < 80:
        sell_signals += 1

    if df['ADX'].iloc[-1] > 25:
        buy_signals += 1
    else:
        sell_signals += 1

    # Definir a análise com base na quantidade de sinais
    if buy_signals == 6:
        return "🟢 Ótimo para compra"
    elif buy_signals >= 4:
        return "🟡 Alerta para compra"
    elif sell_signals == 6:
        return "❌ Ótimo para venda"
    elif sell_signals >= 4:
        return "🔴 Alerta para venda"
    else:
        return "⚪ Instável"

# Main function
st.title("Análise de Sinais para Ativos e Criptomoedas")

# Escolher o ativo
ativo = st.selectbox("Escolha o ativo ou criptomoeda", ["AAPL", "BTC-USD", "ETH-USD", "PETR4.SA", "VALE3.SA"])

# Obter os dados do ativo selecionado
df = yf.download(ativo, period="1y", interval="1d")

# Calcular os indicadores e analisar
df = calculate_indicators(df)
result = analyze(df)

# Exibir o resultado
st.write(f"Resultado para {ativo}: {result}")
