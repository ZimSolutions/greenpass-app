import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- KONFIGURAATIO ---
st.set_page_config(page_title="GreenPass PRO 2026", layout="wide")

# Päästökertoimet 2026
FACTORS = {
    "Teräs": 2.1, "Alumiini": 12.5, "Muovi": 6.0, 
    "Puu": 0.4, "Lasi": 1.2, "Elektroniikka": 45.0,
    "Sähkö_FI": 0.08,  # kg CO2e / kWh
    "Logistiikka": 0.0001 # kg CO2e / kg / km
}

# --- EXCEL-POHJAN LUONTI-FUNKTIO ---
def create_template():
    output = io.BytesIO()
    data = {
        'Osa_Nimi': ['Esimerkki-runko', 'Esimerkki-kuori'],
        'Materiaali': ['Teräs', 'Muovi'],
        'Paino_kg': [10.0, 1.5],
        'Valmistus_Energia_kWh': [5.5, 2.0],
        'Kuljetusmatka_km': [150, 800]
    }
    df_template = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Tuotetiedot')
    return output.getvalue()

# --- KÄYTTÖLIITTYMÄ ---
st.title("🇫🇮 GreenPass PRO: Tuoteanalyysi")

# Sidebar - Ohjeet ja lataus
st.sidebar.header("1. Valmistelu")
template_xlsx = create_template()
st.sidebar.download_button(
    label="📥 Lataa Excel-malli tästä",
    data=template_xlsx,
    file_name="GreenPass_malli.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.sidebar.divider()
st.sidebar.header("2. Analysointi")
uploaded_file = st.sidebar.file_uploader("Lataa täytetty Excel", type=["xlsx"])

# --- ANALYYSI-OSIO ---
if uploaded_file:
    # Lue data
    df = pd.read_excel(uploaded_file)
    
    # Tarkistetaan, että sarakkeet ovat oikein
    try:
        # Laskenta
        df['Mat_CO2e'] = df['Materiaali'].map(FACTORS).fillna(0) * df['Paino_kg']
        df['Energy_CO2e'] = df['Valmistus_Energia_kWh'] * FACTORS['Sähkö_FI']
        df['Log_CO2e'] = df['Paino_kg'] * df['Kuljetusmatka_km'] * FACTORS['Logistiikka']
        df['Yhteensä_CO2e'] = df['Mat_CO2e'] + df['Energy_CO2e'] + df['Log_CO2e']
        
        total_impact = df['Yhteensä_CO2e'].sum()

        st.success(f"Analyysi valmis! Tuotteen kokonaisjalanjälki: {total_impact:.2f} kg CO2e")

        # Visualisointi kolmeen sarakkeeseen
        c1, c2 = st.columns(2)

        with c1:
            # Päästölähteiden jakautuminen
            breakdown = pd.DataFrame({
                'Lähde': ['Materiaali', 'Energia', 'Logistiikka'],
                'Päästöt': [df['Mat_CO2e'].sum(), df['Energy_CO2e'].sum(), df['Log_CO2e'].sum()]
            })
            fig_pie = px.pie(breakdown, values='Päästöt', names='Lähde', title="Mistä päästöt tulevat?")
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            # Osakohtainen vertailu
            fig_bar = px.bar(df, x='Osa_Nimi', y='Yhteensä_CO2e', color='Materiaali', title="Osien vaikutus")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Datataulukko alareunassa
        st.write("### Tarkka erittely osittain")
        st.dataframe(df[['Osa_Nimi', 'Materiaali', 'Paino_kg', 'Yhteensä_CO2e']].style.format({'Yhteensä_CO2e': '{:.2f}'}))

    except Exception as e:
        st.error(f"Virhe tiedoston käsittelyssä. Varmista, että käytit oikeaa Excel-mallia. (Virhe: {e})")

else:
    st.info("👈 Aloita lataamalla Excel-malli vasemmalta, täytä se ja lataa se takaisin.")
    # Lisätään kuvaus, mitä ohjelma tekee
    st.markdown("""
    ### Ohjelman käyttöohje:
    1. **Lataa malli:** Käytä sivupalkin nappia.
    2. **Täytä tiedot:** Lisää omat tuoteosasi, materiaalit ja painot.
    3. **Analysoi:** Vedä tallennettu tiedosto ohjelmaan.
    4. **Tulokset:** Ohjelma laskee hiilijalanjäljen automaattisesti EU-standardien mukaisesti.
    """)
