import streamlit as st
import requests
import pandas as pd
import ta

st.set_page_config(page_title="Bot de Sinais", layout="centered")
st.title("🤖 Bot de Sinais - Análise Técnica de Ativos")

st.markdown("Este app analisa ativos com base em indicadores técnicos e sugere momentos de **compra** ou **venda**.")

# Entrada da API Key
api_key = st.text_input("🔑 Insira sua API Key do Twelve Data:", type="password")

# Lista de ativos favoritos
ativos_favoritos = ['BTC/USD', 'ETH/USD', 'PETR4.SA', 'AAPL', 'VALE3.SA']
ativo = st.selectbox("📈 Selecione o ativo para análise:", ativos_favoritos)

# Função para buscar dados
def buscar_dados_twelvedata(simbolo, api_key):
    url = f"https://api.twelvedata.com/time_series?symbol={simbolo}&interval=1day&outputsize=365&apikey={api_key}"
    resposta = requests.get(url)
    dados = resposta.json()

    if "values" not in dados:
        raise Exception(f"Erro na API: {dados.get('message', 'Erro desconhecido')}")

    df = pd.DataFrame(dados["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df.set_index("datetime", inplace=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# Função para aplicar indicadores e gerar sinais
def analisar_sinais(df):
    df["SMA50"] = ta.trend.sma_indicator(df["close"], window=50)
    df["SMA200"] = ta.trend.sma_indicator(df["close"], window=200)
    df["RSI"] = ta.momentum.rsi(df["close"])
    macd = ta.trend.MACD(df["close"])
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(df["close"])
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    df["Momentum"] = ta.momentum.roc(df["close"])
    stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"])
    df["Stoch"] = stoch.stoch()

    # Pega o último valor para decisão
    ultima = df.dropna().iloc[-1]

    sinais = 0
    if ultima["close"] > ultima["SMA50"] > ultima["SMA200"]:
        sinais += 1
    if ultima["RSI"] < 30:
        sinais += 1
    if ultima["MACD"] > ultima["Signal"]:
        sinais += 1
    if ultima["close"] < ultima["BB_lower"]:
        sinais += 1
    if ultima["Momentum"] > 0:
        sinais += 1
    if ultima["Stoch"] < 20:
        sinais += 1

    if sinais >= 6:
        return "🟢 Ótimo para compra"
    elif sinais == 4 or sinais == 5:
        return "🟡 Alerta para compra"
    elif ultima["RSI"] > 70 and ultima["MACD"] < ultima["Signal"]:
        return "❌ Ótimo para venda"
    elif ultima["RSI"] > 60 or ultima["close"] > ultima["BB_upper"]:
        return "🔶 Alerta para venda"
    else:
        return "🔁 Instável"

# Botão de Análise
if st.button("📊 Analisar"):
    if not api_key:
        st.warning("Por favor, insira sua API Key do Twelve Data.")
    else:
        with st.spinner("🔍 Analisando dados..."):
            try:
                df = buscar_dados_twelvedata(ativo, api_key)
                if df.dropna().shape[0] < 100:
                    st.error("❌ Dados insuficientes após cálculo dos indicadores.")
                else:
                    resultado = analisar_sinais(df)
                    st.success(f"Resultado para **{ativo}**: {resultado}")
            except Exception as e:
                st.error(f"Erro ao buscar dados: {e}")
