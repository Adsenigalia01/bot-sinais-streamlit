import yfinance as yf
import pandas as pd
import ta
import streamlit as st

# Lista de ativos e criptomoedas
ativos = [
    "AAPL", "GOOG", "AMZN", "MSFT", "TSLA", "META", "SPY", "QQQ", "BTC-USD", "ETH-USD",
    "XRP-USD", "ADA-USD", "LTC-USD", "SOL-USD", "DOGE-USD", "PETR4.SA", "VALE3.SA", "ITUB4.SA", 
    "B3SA3.SA", "BRFS3.SA", "PETR3.SA", "WEGE3.SA", "USDCAD=X", "OIL=F", "GOLD=F", "SILVER=F"
]

# Função para calcular os indicadores
def calculate_indicators(df):
    if df.empty:
        raise ValueError("Os dados do ativo estão vazios.")
    
    # Garantir que 'Close' seja uma série unidimensional
    df['Close'] = df['Close'].squeeze()
    
    # Calculando os indicadores
    try:
        df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd_diff(df['Close'])
        df['Stochastic'] = ta.momentum.stochastic_oscillator(df['Close'], window=14)
        df['ADX'] = ta.trend.adx(df['Close'], window=14)
        df['CCI'] = ta.trend.cci(df['Close'], window=14)
    except Exception as e:
        st.write(f"Erro ao calcular os indicadores: {e}")  # Exibindo o erro completo no Streamlit
        raise ValueError(f"Erro ao calcular os indicadores: {e}")
    
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

    if df['CCI'].iloc[-1] > 100:
        buy_signals += 1
    elif df['CCI'].iloc[-1] < -100:
        sell_signals += 1

    # Definir a análise com base na quantidade de sinais
    if buy_signals == 7:
        return "🟢 Ótimo para compra"
    elif buy_signals >= 5:
        return "🟡 Alerta para compra"
    elif sell_signals == 7:
        return "❌ Ótimo para venda"
    elif sell_signals >= 5:
        return "🔴 Alerta para venda"
    else:
        return "⚪ Instável"

# Função para baixar dados de Yahoo Finance
def get_data(ativo):
    df = yf.download(ativo, period="1y", interval="1d")
    if df.empty:
        st.error(f"Não foi possível obter dados para o ativo: {ativo}")
        return None
    return df

# Main function
st.title("Análise de Sinais para Ativos e Criptomoedas")

# Escolher um único ativo
ativo_selecionado = st.selectbox("Escolha um ativo ou criptomoeda", ativos)

if ativo_selecionado:
    st.write(f"Analisando: {ativo_selecionado}")
    df = get_data(ativo_selecionado)
    if df is not None:
        try:
            df = calculate_indicators(df)
            result = analyze(df)

            # Exibir o resultado
            st.write(f"Resultado para {ativo_selecionado}: {result}")
        except ValueError as e:
            st.error(f"Erro no cálculo para {ativo_selecionado}: {e}")
else:
    st.write("Por favor, selecione um ativo ou criptomoeda.")
