import streamlit as st
import json
import pandas as pd
import requests
import ta
from twilio.rest import Client

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
def fetch_data(symbol, period='365'):
    api_key = 'SUA_API_KEY'  # Substitua pela sua chave da TwelveData
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
    df['Stochastic'] = ta.momentum.stochastic(df['high'], df['low'], df['close'], window=14)
    df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)
    
    return df

# Função para avaliar o sinal de compra ou venda
def evaluate_signal(df):
    signals = {
        "SMA50": df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1],
        "RSI": df['RSI'].iloc[-1] < 30,
        "MACD": df['MACD'].iloc[-1] > 0,
        "Stochastic": df['Stochastic'].iloc[-1] > 0.8,
        "EMA": df['EMA'].iloc[-1] > df['SMA200'].iloc[-1]
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

# Função para enviar mensagem via WhatsApp
def send_whatsapp_message(message, to_phone):
    account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
    auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
    from_phone = 'whatsapp:+14155238886'  # Número do WhatsApp do Twilio
    
    client = Client(account_sid, auth_token)
    
    message = client.messages.create(
        body=message,
        from_=from_phone,
        to=to_phone
    )
    return message.sid

# Interface com Streamlit
st.title('Bot de Sinais - Análise de Ativos')

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
    try:
        df = fetch_data(favorite_asset)
        df = calculate_indicators(df)
        signal = evaluate_signal(df)
        st.write(f"Resultado da análise para {favorite_asset}: {signal}")
        
        # Enviar WhatsApp se o sinal for forte
        if signal in ["🟢 Ótimo para compra", "❌ Ótimo para venda"]:
            send_whatsapp_message(f'Análise de {favorite_asset}: {signal}', 'whatsapp:+5511999999999')  # Número de destino do WhatsApp
    except Exception as e:
        st.error(f'Erro ao buscar dados: {e}')
