import streamlit as st
import json
import pandas as pd
import requests
import ta

# Função para carregar os favoritos
def load_favorites():
    try:
        with open('assets.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Função para salvar os favoritos
def save_favorites(favorites):
    with open('assets.json', 'w') as f:
        json.dump(favorites, f)

# Função para buscar dados de ativos
def fetch_data(symbol, period='365', api_key=''):
    if not api_key:
        raise ValueError("API Key não fornecida")
    
    # Ajustando para garantir que o símbolo esteja correto
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&apikey={api_key}&outputsize={period}'
    
    response = requests.get(url)
    data = response.json()
    
    if 'values' in data:
        df = pd.DataFrame(data['values'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['close'] = df['close'].astype(float)
        return df
    else:
        raise ValueError(f"Erro ao buscar dados: {data.get('message', 'Desconhecido')}")

# Função para calcular indicadores técnicos
def calculate_indicators(df):
    df['SMA50'] = ta.trend.sma_indicator(df['close'], window=50)
    df['SMA200'] = ta.trend.sma_indicator(df['close'], window=200)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['MACD'] = ta.trend.macd(df['close'])
    # Substituindo o Stochastic por uma alternativa de indicador
    df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)
    df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)  # Usando o ATR como alternativa
    
    return df

# Função para avaliar o sinal de compra ou venda
def evaluate_signal(df):
    signals = {
        "SMA50": df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1],
        "RSI": df['RSI'].iloc[-1] < 30,
        "MACD": df['MACD'].iloc[-1] > 0,
        "EMA": df['EMA'].iloc[-1] > df['SMA200'].iloc[-1],
        "ATR": df['ATR'].iloc[-1] < df['ATR'].iloc[-2]  # ATR de baixa volatilidade é sinal de estabilidade
    }
    
    count = sum(signals.values())
    
    if count == 5:
        return "🟢 Ótimo para compra"
    elif count == 4:
        return "🟡 Alerta para compra"
    elif count == 3:
        return "⚪ Estável"
    elif count == 2:
        return "🔁 Instável"
    elif count == 1:
        return "❌ Ótimo para venda"
    else:
        return "❌ Ótimo para venda"

# Interface com Streamlit
st.title('Bot de Sinais - Análise de Ativos')

# Inserir API Key da TwelveData
api_key = st.text_input("Insira sua API Key da Twelve Data")

# Seleção de ativo
assets = ['AAPL', 'BTC-USD', 'ETH-USD', 'PETR4.SA', 'VALE3.SA']  # Adicionar mais ativos conforme necessário
selected_asset = st.selectbox("Selecione o ativo", assets)

# Carregar favoritos
favorites = load_favorites()

# Adicionar à lista de favoritos
if st.button('Adicionar aos favoritos'):
    if selected_asset not in favorites:
        favorites.append(selected_asset)
        save_favorites(favorites)
        st.success(f'Ativo {selected_asset} adicionado aos favoritos.')

# Exibir os favoritos
st.subheader("Favoritos")
for asset in favorites:
    st.write(f"- {asset}")

# Seleção de favorito
favorite_asset = st.selectbox("Escolha um favorito para análise", favorites)

# Análise do ativo
if st.button('Analisar'):
    if not api_key:
        st.error("Você precisa fornecer uma API Key válida da Twelve Data.")
    else:
        try:
            df = fetch_data(favorite_asset, api_key=api_key)
            df = calculate_indicators(df)
            signal = evaluate_signal(df)
            st.write(f"Resultado da análise para {favorite_asset}: {signal}")
        except Exception as e:
            st.error(f'Erro ao buscar dados: {e}')
