import streamlit as st
import pandas as pd
import json
from utils import carregar_ativos, salvar_favoritos, carregar_favoritos, analisar_ativo

st.set_page_config(page_title="Bot de Sinais", layout="centered")
st.title("📈 Bot de Sinais de Compra e Venda")
st.markdown("Analisa ativos e criptomoedas com base em 6 estratégias técnicas.")

api_key = st.text_input("Insira sua API Key da Twelve Data:", type="password")
if not api_key:
    st.warning("🔐 Insira a API Key para continuar.")
    st.stop()

ativos_disponiveis = carregar_ativos()
favoritos = carregar_favoritos()

st.subheader("⭐ Selecione seus favoritos")
ativos_selecionados = st.multiselect("Escolha ativos para favoritá-los:", ativos_disponiveis, default=favoritos)
salvar_favoritos(ativos_selecionados)

st.subheader("🔍 Análise de Ativo")
ativo_escolhido = st.selectbox("Escolha um ativo favorito para analisar:", ativos_selecionados)

if st.button("🔎 Analisar"):
    with st.spinner("Analisando..."):
        resultado = analisar_ativo(ativo_escolhido, api_key)
        st.success(f"Resultado: {resultado}")
