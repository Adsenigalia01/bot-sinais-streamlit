import yfinance as yf
import streamlit as st
import pandas as pd
import ta

# Função para obter dados do Yahoo Finance
def get_data(symbol, period="1y"):
    try:
        data = yf.download(symbol, period=period)
        return data
    except Exception as e:
        return None

# Função para calcular os indicadores
def calculate_indicators(df):
    df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['MACD'] = ta.trend.macd(df['Close'])
    df['STOCH'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
    df['MFI'] = ta.volume.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'], window=14)
    df.dropna(inplace=True)
    return df

# Função para analisar os sinais
def analyze_signal(df):
    if df is None or len(df) == 0:
        return "❌ Não foi possível obter dados."

    latest_data = df.iloc[-1]
    buy_signals = 0
    sell_signals = 0

    # Analisando os indicadores
    if latest_data['SMA50'] > latest_data['SMA200']:
        buy_signals += 1  # SMA50 > SMA200 indica tendência de compra
    else:
        sell_signals += 1  # SMA50 < SMA200 indica tendência de venda

    if latest_data['RSI'] < 30:
        buy_signals += 1  # RSI < 30 indica sobre-venda, sinal de compra
    elif latest_data['RSI'] > 70:
        sell_signals += 1  # RSI > 70 indica sobre-compra, sinal de venda

    if latest_data['MACD'] > 0:
        buy_signals += 1  # MACD positivo indica tendência de compra
    else:
        sell_signals += 1  # MACD negativo indica tendência de venda

    if latest_data['STOCH'] < 20:
        buy_signals += 1  # Estocástico < 20 indica sinal de compra
    elif latest_data['STOCH'] > 80:
        sell_signals += 1  # Estocástico > 80 indica sinal de venda

    if latest_data['MFI'] < 20:
        buy_signals += 1  # MFI < 20 indica sobre-venda, sinal de compra
    elif latest_data['MFI'] > 80:
        sell_signals += 1  # MFI > 80 indica sobre-compra, sinal de venda

    # Determinando a análise com base nos sinais
    if buy_signals == 6:
        return "🟢 Ótimo para compra"
    elif buy_signals >= 4:
        return "🟡 Alerta para compra"
    elif sell_signals == 6:
        return "❌ Ótimo para venda"
    elif sell_signals >= 4:
        return "⚠️ Alerta para venda"
    else:
        return "🔁 Instável"

# Lista de ativos para a seleção
assets = {
    "Ações": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "SPY"],
    "Criptomoedas": ["BTC-USD", "ETH-USD", "LTC-USD", "XRP-USD", "ADA-USD", "DOGE-USD"]
}

# Interface do Streamlit
st.title("Analisador de Sinais de Ativos")

# Seleção de ativo
selected_category = st.selectbox("Escolha a categoria", list(assets.keys()))
selected_symbol = st.selectbox("Escolha o ativo", assets[selected_category])

# Obtendo os dados
if selected_symbol:
    df = get_data(selected_symbol, period="365d")
    if df is not None:
        df = calculate_indicators(df)
        signal = analyze_signal(df)
        st.write(f"Análise do ativo {selected_symbol}: {signal}")
    else:
        st.error(f"Erro ao buscar dados para {selected_symbol}.")
