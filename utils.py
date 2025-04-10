import pandas as pd
import json
import os
from twelvedata import TDClient
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator

favoritos_path = "favoritos.json"

def carregar_ativos():
    return ["AAPL", "BTC/USD", "ETH/USD", "PETR4.SA", "VALE3.SA"]

def salvar_favoritos(lista):
    with open(favoritos_path, "w") as f:
        json.dump(lista, f)

def carregar_favoritos():
    if os.path.exists(favoritos_path):
        with open(favoritos_path, "r") as f:
            return json.load(f)
    return []

def analisar_ativo(simbolo, api_key):
    try:
        td = TDClient(apikey=api_key)
        ts = td.time_series(symbol=simbolo, interval="1day", outputsize=365)
        df = ts.as_pandas()
        df = df[::-1].reset_index(drop=True)
        df = df[['close']].rename(columns={'close': 'Close'}).dropna()

        df['SMA'] = SMAIndicator(df['Close'], window=20).sma_indicator()
        df['EMA'] = EMAIndicator(df['Close'], window=20).ema_indicator()
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd_diff()
        df['RSI'] = RSIIndicator(df['Close']).rsi()
        stoch = StochasticOscillator(df['Close'], df['Close'], df['Close'])
        df['Stoch'] = stoch.stoch()
        df.dropna(inplace=True)

        sinais = {
            'SMA': df['Close'].iloc[-1] > df['SMA'].iloc[-1],
            'EMA': df['Close'].iloc[-1] > df['EMA'].iloc[-1],
            'MACD': df['MACD'].iloc[-1] > 0,
            'RSI': df['RSI'].iloc[-1] < 30,
            'Stoch': df['Stoch'].iloc[-1] < 20,
        }

        score = sum(sinais.values())

        if score == 5:
            return "🟢 Ótimo para compra"
        elif score >= 4:
            return "🟡 Atenção para compra"
        elif score == 0:
            return "❌ Ótimo para venda"
        elif score <= 1:
            return "🟠 Atenção para venda"
        else:
            return "🔁 Instável"

    except Exception as e:
        return f"Erro ao buscar dados: {e}"
