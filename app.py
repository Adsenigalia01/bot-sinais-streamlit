import streamlit as st
import pandas as pd
import ta
import requests

# Função para obter dados do Twelve Data
def get_data_twelvedata(symbol, api_key, interval='1day', period='365'):
    url = f'https://api.twelvedata.com/time_series'
    params = {
        'symbol': symbol,
        'interval': interval,
        'apikey': api_key,
        'outputsize': period
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "values" not in data:
        return None  # Caso não tenha retornado dados, retorna None
    
    df = pd.DataFrame(data['values'])
    if df.empty:
        return None  # Se o dataframe estiver vazio, retorna None
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

# Função para calcular indicadores
def calculate_indicators(df):
    try:
        df['SMA50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['SMA200'] = ta.trend.sma_indicator(df['close'], window=200)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['MACD'] = ta.trend.macd(df['close'])
        df['Stochastic'] = ta.momentum.stoch(df['close'], window=14)
        df['ADX'] = ta.trend.adx(df['close'])
        return df
    except Exception as e:
        raise ValueError(f"Erro ao calcular os indicadores: {e}")

# Função para calcular pontuação de compra/venda
def analyze_signals(df):
    scores = 0
    
    # SMA50 vs SMA200
    if df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
        scores -= 1  # Compra
    else:
        scores += 1  # Venda

    # RSI
    if df['RSI'].iloc[-1] < 30:
        scores -= 1  # Compra
    elif df['RSI'].iloc[-1] > 70:
        scores += 1  # Venda

    # MACD
    if df['MACD'].iloc[-1] > 0:
        scores -= 1  # Compra
    else:
        scores += 1  # Venda

    # Stochastic
    if df['Stochastic'].iloc[-1] < 20:
        scores -= 1  # Compra
    elif df['Stochastic'].iloc[-1] > 80:
        scores += 1  # Venda

    # ADX
    if df['ADX'].iloc[-1] > 25:
        if df['SMA50'].iloc[-1] > df['SMA200'].iloc[-1]:
            scores -= 1  # Compra
        else:
            scores += 1  # Venda
    else:
        scores = 0  # Instável

    if scores <= -6:
        return "🟢 Ótimo para compra"
    elif -5 <= scores <= -4:
        return "🟡 Alerta para compra"
    elif scores >= 6:
        return "❌ Ótimo para venda"
    elif 4 <= scores <= 5:
        return "⚪ Alerta para venda"
    else:
        return "🔁 Instável"

# Streamlit app
st.title('Análise de Sinais para Ativos e Criptomoedas')

# API Key do Twelve Data
api_key = st.text_input("Digite sua API Key do Twelve Data", type="password")

# Lista de ativos válidos para o Twelve Data (simplificada)
ativos_disponiveis = [
    "AAPL", "GOOG", "AMZN", "BTC/USD", "ETH/USD", "PETR3.SA", "VALE3.SA", "USOIL", "BRL=X"
]

# Escolher ativo
ativo = st.selectbox('Escolha o ativo ou criptomoeda', ativos_disponiveis)

if api_key:
    st.write(f'Analisando: {ativo}')
    
    # Buscar dados do ativo no Twelve Data
    df = get_data_twelvedata(ativo, api_key)
    
    if df is not None:
        try:
            # Calcular indicadores
            df = calculate_indicators(df)
            
            # Analisar sinais
            resultado = analyze_signals(df)
            st.write(f"Resultado da análise: {resultado}")
        except Exception as e:
            st.write(f"Erro ao calcular os indicadores: {e}")
    else:
        st.write("Erro ao buscar dados para o ativo. Verifique se o símbolo está correto ou se há um problema com a API.")
else:
    st.write("Por favor, insira sua API Key para continuar.")
