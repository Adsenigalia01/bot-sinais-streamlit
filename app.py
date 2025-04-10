import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from favorite_assets import load_favorite_assets, manage_favorite_assets

# Função para obter dados de um ativo a partir do Yahoo Finance
def get_asset_data(asset, period='1y'):
    try:
        # Obter dados históricos para o ativo
        data = yf.download(asset, period=period)
        if data.empty:
            raise ValueError(f"Não foi possível obter dados para o ativo {asset}")
        return data
    except Exception as e:
        st.error(f"Erro ao buscar dados para o ativo {asset}: {e}")
        return None

# Função para calcular indicadores técnicos
def calculate_indicators(df):
    try:
        # Calculando indicadores técnicos
        df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['Stochastic'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
        df['EMA200'] = ta.trend.ema_indicator(df['Close'], window=200)
        return df
    except Exception as e:
        st.error(f"Erro ao calcular os indicadores: {e}")
        raise

# Função para análise de sinais
def analyze_signals(df):
    signals = []
    
    # Verificar os sinais dos indicadores
    if df['SMA50'][-1] > df['SMA200'][-1]: signals.append(-1)  # Sinal de compra
    else: signals.append(1)  # Sinal de venda

    if df['RSI'][-1] < 30: signals.append(-1)  # Sinal de compra
    elif df['RSI'][-1] > 70: signals.append(1)  # Sinal de venda
    else: signals.append(0)  # Instável

    if df['Stochastic'][-1] < 20: signals.append(-1)  # Sinal de compra
    elif df['Stochastic'][-1] > 80: signals.append(1)  # Sinal de venda
    else: signals.append(0)  # Instável

    if df['MACD'][-1] > 0: signals.append(-1)  # Sinal de compra
    else: signals.append(1)  # Sinal de venda

    if df['EMA50'][-1] > df['EMA200'][-1]: signals.append(-1)  # Sinal de compra
    else: signals.append(1)  # Sinal de venda

    if df['Close'][-1] > df['SMA50'][-1]: signals.append(-1)  # Sinal de compra
    else: signals.append(1)  # Sinal de venda

    # Calcular o resultado final baseado na pontuação
    score = sum(signals)

    if score == -7:
        return "Ótimo para compra"
    elif -6 <= score <= -5:
        return "Atenção para compra"
    elif score == 7:
        return "Ótimo para venda"
    elif 5 <= score <= 6:
        return "Atenção para venda"
    else:
        return "Instável"

# Função para exibir a interface de gerenciamento de favoritos
def manage_favorites():
    st.title('Análise de Sinais para Ativos e Criptomoedas')

    # Campo para inserir a API Key do Twelve Data
    api_key = st.text_input("Insira sua API Key da Twelve Data:", type="password")
    if not api_key:
        st.warning("Por favor, insira sua API Key para poder analisar os ativos.")
        return

    # Carregar ativos favoritos
    favorites = load_favorite_assets()
    
    # Exibir lista de ativos favoritos
    st.write("Ativos favoritos:", favorites)

    # Entrada para o ativo
    asset_input = st.text_input("Digite o ativo ou criptomoeda (Ex: AAPL, PETR3.SA):")

    # Seleção para adicionar ou remover ativos
    action = st.selectbox("Escolha a ação", ["Adicionar", "Remover"])

    if st.button(f"{action} ativo"):
        if asset_input:
            # Adicionar ou remover o ativo conforme a ação escolhida
            manage_favorite_assets(action, asset_input)
            st.success(f"Ativo {action.lower()} com sucesso: {asset_input}")
        else:
            st.error("Digite um ativo para adicionar ou remover.")

    # Exibir a lista de favoritos após a ação
    favorites = load_favorite_assets()
    st.write("Ativos favoritos atualizados:", favorites)

    # Permitir o usuário selecionar um ativo da lista de favoritos para análise
    selected_asset = st.selectbox("Escolha um ativo para análise", favorites)
    if selected_asset:
        st.write(f"Analisando: {selected_asset}")
        
        # Buscar dados do ativo
        df = get_asset_data(selected_asset)
        
        if df is not None:
            # Calcular indicadores
            try:
                df = calculate_indicators(df)
                # Analisar sinais
                result = analyze_signals(df)
                st.write(f"Resultado da análise para {selected_asset}: {result}")
            except Exception as e:
                st.error(f"Erro no cálculo dos indicadores: {e}")

# Rodar a função de gerenciamento de favoritos
if __name__ == "__main__":
    manage_favorites()
