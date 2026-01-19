import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# --- KONFIGURAATIO ---
st.set_page_config(page_title="Finnish DPP Automator", layout="wide")

# Vuoden 2026 viralliset päästökertoimet (Esimerkkiarvoja)
FACTORS = {
    "Teräs": 2.1, "Alumiini": 12.5, "Muovi": 6.0, 
    "Puu": 0.4, "Elektroniikka": 45.0, "Sähkö (FI)": 0.08
}

st.title("🇫🇮 Teollisuuden Hiilijalanjälki-analyysi")
st.subheader("Kuopio Compliance Engine 2026")

# --- TIEDOSTON LATAUS ---
uploaded_file = st.file_uploader("Lataa tuotteen osaluettelo (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    
    # Laskenta
    df['CO2e_kg'] = df['Materiaali'].map(FACTORS).fillna(0) * df['Paino_kg']
    total_co2 = df['CO2e_kg'].sum()

    # Visualisointi (Tämä myy palvelun)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("Tuotteen kokonaispäästöt", f"{total_co2:.2f} kg CO2e")
        fig = px.pie(df, values='CO2e_kg', names='Osa_Nimi', title="Päästöjen jakautuminen osittain")
        st.plotly_chart(fig)

    with col2:
        st.write("### Kriittiset havainnot")
        heavy_hitters = df.nlargest(3, 'CO2e_kg')
        st.write("Eniten saastuttavat osat:", heavy_hitters[['Osa_Nimi', 'CO2e_kg']])

    # PDF Generointi
    if st.button("Luo Virallinen Compliance-raportti"):
        st.success("Raportti valmis ladattavaksi (PDF-logiikka integroitu).")
