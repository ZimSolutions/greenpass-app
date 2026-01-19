import streamlit as st
import pandas as pd
import io

# --- KONFIGURAATIO ---
st.set_page_config(page_title="GreenPass PRO 2026", layout="wide")

# --- EXCEL-POHJAN LUONTI ---
def create_template():
    output = io.BytesIO()
    # Luodaan esimerkkidata
    data = {
        'Osa_Nimi': ['Esimerkki-osa 1', 'Esimerkki-osa 2'],
        'Materiaali': ['Teräs', 'Alumiini'],
        'Paino_kg': [10.5, 5.0],
        'Valmistus_Energia_kWh': [20.0, 15.0],
        'Kuljetusmatka_km': [100, 500]
    }
    df_template = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Tuotetiedot')
    return output.getvalue()

st.title("🇫🇮 GreenPass PRO: Excel-pohja ja Analyysi")

# --- LATAA POHJA TÄSTÄ ---
st.sidebar.header("1. Lataa työkalu")
template_xlsx = create_template()
st.sidebar.download_button(
    label="📥 Lataa Excel-malli tästä",
    data=template_xlsx,
    file_name="GreenPass_malli.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.sidebar.divider()

# --- LÄHETÄ TÄYTETTY TIEDOSTO ---
st.sidebar.header("2. Analysoi tuote")
uploaded_file = st.sidebar.file_uploader("Lataa täytetty Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Ladattu data:", df)
    st.success("Hienoa! Data luettu onnistuneesti. Voit nyt jatkaa analyysiin.")
else:
    st.info("Lataa ensi vasemmalta Excel-malli, täytä se ja lataa se takaisin tähän.")
