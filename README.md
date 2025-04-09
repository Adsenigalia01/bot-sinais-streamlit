# 📈 Bot de Sinais de Compra e Venda

Este é um aplicativo Streamlit que utiliza a API da Twelve Data para analisar ativos como ações e criptomoedas e identificar os melhores momentos para compra e venda com base em múltiplos indicadores técnicos.

---

## 🚀 Funcionalidades

- Análise automática de ativos favoritos
- Indicadores técnicos usados:
  - Média Móvel (SMA 50 e SMA 200)
  - RSI (Índice de Força Relativa)
  - MACD
  - Bandas de Bollinger
- Resultados simplificados com mensagens claras:
  - 🟢 Ótimo para compra
  - ❌ Ótimo para venda
  - 🟡 Alerta para compra
  - 🔁 Instável
  - ⚪ Estável
- Envio automático dos sinais por WhatsApp via Twilio

---

## 📋 Pré-requisitos

- Conta no [Twelve Data](https://twelvedata.com) com API Key
- Conta no [Twilio](https://www.twilio.com/) com acesso ao envio via WhatsApp
- Python 3.8+

---

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/bot-sinais-streamlit.git
cd bot-sinais-streamlit
